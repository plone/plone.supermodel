from elementtree import ElementTree
    
from zope.interface import implements, implementedBy
from zope.component import queryUtility

import zope.schema

from zope.schema.interfaces import IField, ICollection, IDict

from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.interfaces import IFieldExportImportHandler, IToUnicode

from plone.supermodel.utils import no_ns, value_to_element, element_to_value

class BaseHandler(object):
    """Base class for import/export handlers.
    
    The read_field method is called to read one field of the known subtype
    from an XML element.
    
    The write_field method is called to write one field to a particular element.
    """
    
    implements(IFieldExportImportHandler)
    
    # Elements that we will not write
    filtered_attributes = frozenset(['order', 'unique',])
    
    # Elements that are of the same type as the field itself
    field_type_attributes = ('min', 'max', 'default',)
    
    # Elements that are of the same type as the field itself, but are 
    # otherwise not validated
    nonvalidated_field_type_attributes = ('missing_value',)
    
    # Attributes that contain another field. Unfortunately, 
    field_instance_attributes = ('key_type', 'value_type',)
    
    def __init__(self, klass):
        self.klass = klass
        self.field_attributes = {}
        
        # Build a dict of the parameters supported by this field type.
        # Each parameter is itself a field, which can be used to convert
        # text input to an appropriate object.
        for schema in implementedBy(self.klass).flattened():
            self.field_attributes.update(zope.schema.getFields(schema))
        
    def read(self, element):
        """Read a field from the element and return a new instance
        """
        attributes = {}
        deferred = {}
        deferred_nonvalidated = {}
        
        for attribute_element in element:
            attribute_name = no_ns(attribute_element.tag)
            attribute_field = self.field_attributes.get(attribute_name, None)
            if attribute_field is not None:

                if attribute_name in self.field_type_attributes:
                    deferred[attribute_name] = attribute_element

                elif attribute_name in self.nonvalidated_field_type_attributes:
                    deferred_nonvalidated[attribute_name] = attribute_element

                elif attribute_name in self.field_instance_attributes:                    
                    
                    attribute_field_type = attribute_element.get('type')
                    handler = queryUtility(IFieldExportImportHandler, name=attribute_field_type)
                    
                    attributes[attribute_name] = handler.read(attribute_element)
                    
                else:
                    attributes[attribute_name] = \
                        self.read_attribute(attribute_element, attribute_field)
        
        name = element.get('name')
        if name is not None:
            name = unicode(name)
        
        field_instance = self.klass(__name__=name, **attributes)
        
        # Handle those elements that can only be set up once the field is
        # constructed, in the preferred order.
        for attribute_name in self.field_type_attributes:
            if attribute_name in deferred:
                attribute_element = deferred[attribute_name]
                value = self.read_attribute(attribute_element, field_instance)
                setattr(field_instance, attribute_name, value)
        
        for attribute_name in self.nonvalidated_field_type_attributes:
            if attribute_name in deferred_nonvalidated:
                
                # this is pretty nasty: we need the field's fromUnicode(),
                # but this always validates. The missing_value field may by
                # definition be invalid. Therefore, we need to fake it.
                
                clone = self.klass.__new__(self.klass)
                clone.__dict__.update(field_instance.__dict__) 
                clone.__dict__['validate'] = lambda value: True
                
                attribute_element = deferred_nonvalidated[attribute_name]
                value = self.read_attribute(attribute_element, clone)
                setattr(field_instance, attribute_name, value)
                
        return field_instance
    
    def write(self, field, name, type, element_name='field'):
        """Create and return a new element representing the given field
        """
        
        element = ElementTree.Element(element_name)
        
        if name:
            element.set('name', name)
            
        element.set('type', type)
        
        for attribute_name in sorted(self.field_attributes.keys()):
            attribute_field = self.field_attributes[attribute_name]
            if attribute_name in self.filtered_attributes:
                continue
            child = self.write_attribute(attribute_field, field)
            if child is not None:
                element.append(child)

        return element
        
    # Field attribute read and write
    
    def read_attribute(self, element, attribute_field):
        """Read a single attribute from the given element. The attribute is of
        a type described by the given Field object.
        """
        
        key_type = None
        value_type = None
        
        if ICollection.providedBy(attribute_field):
            value_type = attribute_field.value_type
        elif IDict.providedBy(attribute_field):
            key_type = attribute_field.key_type
            value_type = attribute_field.value_type
        
        return element_to_value(attribute_field, element, 
                                    key_type=key_type, value_type=value_type)
        
    def write_attribute(self, attribute_field, field, ignore_default=True):
        """Create and return a element that describes the given attribute
        field on the given field
        """
        
        attribute_field_name = attribute_field.__name__
        attribute_field = attribute_field.bind(field)
        value = attribute_field.get(field)
        
        if ignore_default and value == attribute_field.default:
            return None
        
        # The value points to another field. Recurse.
        if IField.providedBy(value):
            
            name_extractor = IFieldNameExtractor(value)
            value_field_type = name_extractor()
            
            handler = queryUtility(IFieldExportImportHandler, name=value_field_type)
            if handler is None:
                return None
            
            return handler.write(value, None, value_field_type, element_name=attribute_field_name)
        
        # The value is a list of the field's value_type. Write elements.
        elif isinstance(value, (tuple, list, set, frozenset,)) and \
                ICollection.providedBy(field) and \
                (attribute_field_name in self.field_type_attributes or
                 attribute_field_name in self.nonvalidated_field_type_attributes):
            
            return value_to_element(attribute_field, value, value_type=field.value_type)
        
        # The value is a dict of the field's key_type/value_type. Write elements with keys.
        elif isinstance(value, (dict,)) and IDict.providedBy(field) and \
                (attribute_field_name in self.field_type_attributes or
                 attribute_field_name in self.nonvalidated_field_type_attributes):
            return value_to_element(attribute_field, value,
                                        key_type=field.key_type, value_type=field.value_type)

        # The value is a 'primitive'. Convert to unicode and place in element.
        else:
            converter = None
    
            if attribute_field.__name__ in self.field_type_attributes or \
                    attribute_field.__name__ in self.nonvalidated_field_type_attributes:
                converter = IToUnicode(field)
        
            return value_to_element(attribute_field, value, converter=converter)

class DictHandler(BaseHandler):
    """Special handling for the Dict field, which uses Attribute instead of
    Field to describe its key_type and value_type.
    """
    
    def __init__(self, klass):
        super(DictHandler, self).__init__(klass)
        self.field_attributes['key_type'] = zope.schema.Field(__name__='key_type', title=u"Key type")
        self.field_attributes['value_type'] = zope.schema.Field(__name__='value_type', title=u"Value type")

class ObjectHandler(BaseHandler):
    """Special handling for the Object field, which uses Attribute instead of
    Field to describe its schema
    """
    
    def __init__(self, klass):
        super(ObjectHandler, self).__init__(klass)
        self.field_attributes['schema'] = zope.schema.InterfaceField(__name__='schema')

    def write(self, field, name, type, element_name='field'):
        raise NotImplementedError, u"Serialisation of object fields is not supported"