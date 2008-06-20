from elementtree import ElementTree
    
from zope.interface import implements
from zope.interface import implementedBy
from zope.schema.interfaces import ICollection, IFromUnicode

import zope.schema

from plone.supermodel.interfaces import IFieldExportImportHandler

from plone.supermodel.utils import ns, no_ns

class BaseHandler(object):
    """Base class for import/export handlers.
    
    The read_field method is called to read one field of the known subtype
    from an XML element.
    
    The write_field method is called to write one field to a particular element.
    """
    
    implements(IFieldExportImportHandler)
    
    def __init__(self, klass, element_name, filtered_attributes=['order']):
        self.klass = klass
        self.element_name = element_name
        self.filtered_attributes = filtered_attributes
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
        for attribute_element in element:
            attribute_name = no_ns(attribute_element.tag)
            attribute_field = self.field_attributes.get(attribute_name, None)
            if attribute_field is not None:
                attributes[attribute_name] = self.read_attribute(attribute_element, attribute_field)
        
        return self.klass(__name__=element.get('name'), **attributes)
    
    def write(self, context, name, type):
        """Create and return a new element representing the given context
        """
        element = ElementTree.Element(self.element_name)
        element.set('name', name)
        element.set('type', type)
        
        for attribute_name, attribute_field in self.field_attributes.items():
            if attribute_name not in self.filtered_attributes:
                child = self.write_attribute(attribute_field, context)
                if child is not None:
                    element.append(child)

        return element
        
    # Field attribute read and write
    
    def read_attribute(self, element, attribute_field):
        """Read a single attribute from the given element. The attribute is of
        a type described by the given Field object.
        """
        
        # NOTE: If we had the target field already, we would do this in order
        #   to later be able to validate and set values.
        # attribute_field = attribute_field.bind(context)
        
        value = None
        
        # If we have a collection, we need to look at the value_type.
        # We look for <element>value</element> child elements and get the
        # value from there
        if ICollection.providedBy(attribute_field):
            value_type = attribute_field.value_type
            value = []
            for child in element:
                if child.tag != 'element':
                    continue
                element_value = child.text
                value.append(self.from_unicode(value_type, element_value))
            value = self.field_typecast(attribute_field, value)
        
        # Otherwise, just get the value of the element
        else:
            value = element.text
            value = self.from_unicode(attribute_field, value)
          
        # NOTE: If we had the target field already, we could do this, where
        #   'context' would be the field we're building and 'field' would be
        #   the field that describes this parameter.
        # attribute_field.validate(value)
        # attribute_field.set(context, value)

        return value
        
    def write_attribute(self, attribute_field, context):
        """Create and return a element that describes the given field on the
        given context (which will itself be a field).
        """
        
        attribute_field = attribute_field.bind(context)
        value = attribute_field.get(context)
        
        if value == attribute_field.default:
            return None
        
        child = ElementTree.Element(attribute_field.__name__)
        
        if value is not None:
            if ICollection.providedBy(attribute_field):
                for e in value:
                    list_element = ElementTree.Element('element')
                    list_element.text = unicode(e)
            else:
                child.text = unicode(value)
            
        return child
        
    # Helper methods
        
    def from_unicode(self, field, value):
        
        # XXX: Seems ElementTree uses str unless it finds some non-ASCII;
        # we want to make everything unicode
        if isinstance(value, str):
            value = unicode(value)
        
        # XXX: Bool incorrectly omits to declare that it implements
        # IFromUnicode, even though it does.
        if IFromUnicode.providedBy(field) or isinstance(field, zope.schema.Bool):
            return field.fromUnicode(value)
        else:
            return self.field_typecast(field, value)
    
    def field_typecast(self, field, value):
        # A slight hack to force sequence types to the right type
        typecast = getattr(field, '_type', None)
        if typecast is not None:
            if not isinstance(typecast, (list, tuple)):
                typecast = (typecast,)
            for tc in reversed(typecast):
                if callable(tc):
                    try:
                        value = tc(value)
                        break
                    except:
                        pass
        return value