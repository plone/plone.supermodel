from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component import getUtility, queryUtility, getUtilitiesFor

from zope.schema import getFields

from zope.dottedname.resolve import resolve

from plone.supermodel.interfaces import ISchemaPolicy
from plone.supermodel.interfaces import IFieldExportImportHandler

from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import IFieldMetadataHandler

from plone.supermodel.utils import ns

from plone.supermodel.model import Model, Fieldset
from plone.supermodel.interfaces import FIELDSETS_KEY

from elementtree import ElementTree

# Helper adapters

class DefaultSchemaPolicy(object):
    implements(ISchemaPolicy)
    
    def module(self, schema_name, tree):
        return 'plone.supermodel.generated'
        
    def bases(self, schema_name, tree):
        return ()
        
    def name(self, schema_name, tree):
        return schema_name

# Algorithm

def parse(source, policy=u""):
    tree = ElementTree.parse(source)
    root = tree.getroot()
    
    model = Model()
    
    handlers = {}
    schema_metadata_handlers = tuple(getUtilitiesFor(ISchemaMetadataHandler))
    field_metadata_handlers = tuple(getUtilitiesFor(IFieldMetadataHandler))
    
    policy_util = getUtility(ISchemaPolicy, name=policy)
    
    def read_field(field_element, schema_attributes, field_elements, base_fields):
        
        # Parse field attributes
        field_name = field_element.get('name')
        field_type = field_element.get('type')
    
        if field_name is None or field_type is None:
            raise ValueError("The attributes 'name' and 'type' are required for each <field /> element")
    
        handler = handlers.get(field_type, None)
        if handler is None:
            handler = handlers[field_type] = queryUtility(IFieldExportImportHandler, name=field_type)
            if handler is None:
                raise ValueError("Field type %s specified for field %s is not supported" % (field_type, field_name,))
    
        field = handler.read(field_element)
        
        # Preserve order from base interfaces if this field is an override
        # of a field with the same name in a base interface
        base_field = base_fields.get(field_name, None)
        if base_field is not None:
            field.order = base_field.order
        
        # Save for the schema
        schema_attributes[field_name] = field
        field_elements[field_name] = field_element
        
        return field_name
    
    for schema_element in root.findall(ns('schema')):
        schema_attributes = {}
        schema_metadata = {}
        
        schema_name = schema_element.get('name')
        if schema_name is None:
            schema_name = u""
        
        bases = ()
        base_fields = {}
        based_on = schema_element.get('based-on')
        if based_on is not None:
            bases = tuple([resolve(dotted) for dotted in based_on.split()])
            for base_schema in bases:
                base_fields.update(getFields(base_schema))
        
        field_elements = {}
        
        # Read global fields
        for field_element in schema_element.findall(ns('field')):
            read_field(field_element, schema_attributes, field_elements, base_fields)
    
        # Read fieldsets and their fields
        fieldsets = []
        fieldsets_by_name = {}
    
        for subelement in schema_element:
            
            if subelement.tag == ns('field'):
                read_field(subelement, schema_attributes, field_elements, base_fields)
            elif subelement.tag == ns('fieldset'):
                
                fieldset_name = subelement.get('name')
                if fieldset_name is None:
                    raise ValueError(u"Fieldset in schema %s has no name" % (schema_name))
                
                fieldset = fieldsets_by_name.get(fieldset_name, None)
                if fieldset is None:
                    fieldset_label = subelement.get('label')
                    fieldset_description = subelement.get('description')
                
                    fieldset = fieldsets_by_name[fieldset_name] = Fieldset(fieldset_name, 
                                    label=fieldset_label, description=fieldset_description)
                    fieldsets_by_name[fieldset_name] = fieldset
                    fieldsets.append(fieldset)
                
                for field_element in subelement.findall(ns('field')):
                    parsed_field_name = read_field(field_element, schema_attributes, field_elements, base_fields)
                    if parsed_field_name:
                        fieldset.fields.append(parsed_field_name)
    
        schema = InterfaceClass(name=policy_util.name(schema_name, tree),
                                bases=bases + policy_util.bases(schema_name, tree),
                                __module__=policy_util.module(schema_name, tree),
                                attrs=schema_attributes)
        
        schema.setTaggedValue(FIELDSETS_KEY, fieldsets)
        
        # Save fieldsets
        
        # Let metadata handlers write metadata
        for handler_name, metadata_handler in field_metadata_handlers:
            for field_name in schema:
                if field_name in field_elements:
                    metadata_handler.read(field_elements[field_name], schema, schema[field_name])
        
        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.read(schema_element, schema)

        model.schemata[schema_name] = schema
    
    return model



__all__ = ('parse',)