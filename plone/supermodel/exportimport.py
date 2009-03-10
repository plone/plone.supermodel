from elementtree import ElementTree
    
from zope.interface import Interface, implements, implementedBy
from zope.component import queryUtility

import zope.schema

from zope.schema.interfaces import IField
from zope.schema.interfaces import IVocabularyTokenized

from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.interfaces import IFieldExportImportHandler

from plone.supermodel.utils import no_ns, value_to_element, element_to_value

class BaseHandler(object):
    """Base class for import/export handlers.
    
    The read_field method is called to read one field of the known subtype
    from an XML element.
    
    The write_field method is called to write one field to a particular element.
    """
    
    implements(IFieldExportImportHandler)
    
    # Elements that we will not read/write. 'r' means skip when reading;
    # 'w' means skip when writing; 'rw' means skip always.

    filtered_attributes = {'order': 'rw', 'unique': 'rw'}
    
    # Elements that are of the same type as the field itself
    field_type_attributes = ('min', 'max', 'default',)
    
    # Elements that are of the same type as the field itself, but are 
    # otherwise not validated
    nonvalidated_field_type_attributes = ('missing_value',)
    
    # Attributes that contain another field. Unfortunately, 
    field_instance_attributes = ('key_type', 'value_type',)
    
    # Fields that are always written
    
    forced_fields = frozenset(['default', 'missing_value'])
    
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
            
            if 'r' in self.filtered_attributes.get(attribute_name, ''):
                continue
            
            attribute_field = self.field_attributes.get(attribute_name, None)
            if attribute_field is not None:

                if attribute_name in self.field_type_attributes:
                    deferred[attribute_name] = attribute_element

                elif attribute_name in self.nonvalidated_field_type_attributes:
                    deferred_nonvalidated[attribute_name] = attribute_element

                elif attribute_name in self.field_instance_attributes:                    
                    
                    attribute_field_type = attribute_element.get('type')
                    handler = queryUtility(IFieldExportImportHandler, name=attribute_field_type)
                    
                    if handler is None:
                        raise NotImplementedError(u"Type %s used for %s not supported" % (attribute_field_type, attribute_name))
                    
                    attributes[attribute_name] = handler.read(attribute_element)
                    
                else:
                    attributes[attribute_name] = \
                        self.read_attribute(attribute_element, attribute_field)
        
        name = element.get('name')
        if name is not None:
            name = unicode(name)
        
        field_instance = self.klass(__name__=name, **attributes)
        
        # some fields can't validate fully until they're finished setting up
        field_instance._init_field = True
        
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
        
        field_instance._init_field = True
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
            if 'w' in self.filtered_attributes.get(attribute_name, ''):
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
        
        return element_to_value(attribute_field, element)
        
    def write_attribute(self, attribute_field, field, ignore_default=True):
        """Create and return a element that describes the given attribute
        field on the given field
        """
        
        element_name = attribute_field.__name__
        attribute_field = attribute_field.bind(field)
        value = attribute_field.get(field)
        
        force = (element_name in self.forced_fields)
        
        if ignore_default and value == attribute_field.default:
            return None
        
        # The value points to another field. Recurse.
        if IField.providedBy(value):
            value_field_type = IFieldNameExtractor(value)()
            handler = queryUtility(IFieldExportImportHandler, name=value_field_type)
            if handler is None:
                return None
            return handler.write(value, name=None, type=value_field_type, element_name=element_name)
        
        # For 'default', 'missing_value' etc, we want to validate against
        # the imported field type itself, not the field type of the attribute
        if element_name in self.field_type_attributes or \
                element_name in self.nonvalidated_field_type_attributes:
            attribute_field = field
        
        return value_to_element(attribute_field, value, name=element_name, force=force)

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
    
    # We can't serialise the value or missing_value of an object field.
    
    filtered_attributes = BaseHandler.filtered_attributes.copy()
    filtered_attributes.update({'default': 'w', 'missing_value': 'w'})
    
    def __init__(self, klass):
        super(ObjectHandler, self).__init__(klass)

        # This is not correctly set in the interface
        self.field_attributes['schema'] = zope.schema.InterfaceField(__name__='schema')
        

class ChoiceHandler(BaseHandler):
    """Special handling for the Choice field
    """
    
    filtered_attributes = BaseHandler.filtered_attributes.copy()
    filtered_attributes.update({'vocabulary': 'w', 'values': 'w', 'source': 'w'})
    
    def __init__(self, klass):
        super(ChoiceHandler, self).__init__(klass)
        
        # Special options for the constructor. These are not automatically written.
        
        self.field_attributes['vocabulary'] = \
            zope.schema.TextLine(__name__='vocabulary', title=u"Named vocabulary")
        
        self.field_attributes['values'] = \
            zope.schema.List(__name__='values', title=u"Values",
                                value_type=zope.schema.Text(title=u"Value"))
        
        # XXX: We can't be more specific about the schema, since the field
        # supports both ISource and IContextSourceBinder. However, the 
        # initialiser will validate.
        self.field_attributes['source'] = \
            zope.schema.Object(__name__='source', title=u"Source", schema=Interface) 
    
    def write(self, field, name, type, element_name='field'):
        
        element = super(ChoiceHandler, self).write(field, name, type, element_name)
        
        # write vocabulary or values list
    
        # Named vocabulary
        if field.vocabularyName is not None and field.vocabulary is None:
            attribute_field = self.field_attributes['vocabulary']
            child = value_to_element(attribute_field, field.vocabularyName, name='vocabulary', force=True)
            element.append(child)
        
        # Listed vocabulary - attempt to convert to a simple list of values
        elif field.vocabularyName is None and IVocabularyTokenized.providedBy(field.vocabulary):
            value = []
            for term in field.vocabulary:
                if not isinstance(term.value, (str, unicode),) or term.token != str(term.value):
                    raise NotImplementedError(u"Cannot export a vocabulary that is not "
                                               "based on a simple list of values")                    
                value.append(term.value)
            
            attribute_field = self.field_attributes['values']
            child = value_to_element(attribute_field, value, name='values', force=True)
            element.append(child)
        
        # Anything else is not allowed - we can't export ISource/IVocabulary or
        #  IContextSourceBinder objects.
        else:
            raise NotImplementedError(u"Choice fields with vocabularies not based on "
                                        "a simple list of values or a named vocabulary "
                                        "cannot be exported")
        
        return element