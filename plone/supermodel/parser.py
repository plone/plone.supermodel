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
    
    def module(self, schemaName, tree):
        return 'plone.supermodel.generated'
        
    def bases(self, schemaName, tree):
        return ()
        
    def name(self, schemaName, tree):
        return schemaName

# Algorithm

def parse(source, policy=u""):
    tree = ElementTree.parse(source)
    root = tree.getroot()
    
    model = Model()
    
    handlers = {}
    schema_metadata_handlers = tuple(getUtilitiesFor(ISchemaMetadataHandler))
    field_metadata_handlers = tuple(getUtilitiesFor(IFieldMetadataHandler))
    
    policy_util = getUtility(ISchemaPolicy, name=policy)
    
    def readField(fieldElement, schemaAttributes, fieldElements, baseFields):
        
        # Parse field attributes
        fieldName = fieldElement.get('name')
        fieldType = fieldElement.get('type')
    
        if fieldName is None or fieldType is None:
            raise ValueError("The attributes 'name' and 'type' are required for each <field /> element")
    
        handler = handlers.get(fieldType, None)
        if handler is None:
            handler = handlers[fieldType] = queryUtility(IFieldExportImportHandler, name=fieldType)
            if handler is None:
                raise ValueError("Field type %s specified for field %s is not supported" % (fieldType, fieldName,))
    
        field = handler.read(fieldElement)
        
        # Preserve order from base interfaces if this field is an override
        # of a field with the same name in a base interface
        base_field = baseFields.get(fieldName, None)
        if base_field is not None:
            field.order = base_field.order
        
        # Save for the schema
        schemaAttributes[fieldName] = field
        fieldElements[fieldName] = fieldElement
        
        return fieldName
    
    for schema_element in root.findall(ns('schema')):
        schemaAttributes = {}
        schema_metadata = {}
        
        schemaName = schema_element.get('name')
        if schemaName is None:
            schemaName = u""
        
        bases = ()
        baseFields = {}
        based_on = schema_element.get('based-on')
        if based_on is not None:
            bases = tuple([resolve(dotted) for dotted in based_on.split()])
            for base_schema in bases:
                baseFields.update(getFields(base_schema))
        
        fieldElements = {}
        
        # Read global fields
        for fieldElement in schema_element.findall(ns('field')):
            readField(fieldElement, schemaAttributes, fieldElements, baseFields)
    
        # Read fieldsets and their fields
        fieldsets = []
        fieldsets_by_name = {}
    
        for subelement in schema_element:
            
            if subelement.tag == ns('field'):
                readField(subelement, schemaAttributes, fieldElements, baseFields)
            elif subelement.tag == ns('fieldset'):
                
                fieldset_name = subelement.get('name')
                if fieldset_name is None:
                    raise ValueError(u"Fieldset in schema %s has no name" % (schemaName))
                
                fieldset = fieldsets_by_name.get(fieldset_name, None)
                if fieldset is None:
                    fieldset_label = subelement.get('label')
                    fieldset_description = subelement.get('description')
                
                    fieldset = fieldsets_by_name[fieldset_name] = Fieldset(fieldset_name, 
                                    label=fieldset_label, description=fieldset_description)
                    fieldsets_by_name[fieldset_name] = fieldset
                    fieldsets.append(fieldset)
                
                for fieldElement in subelement.findall(ns('field')):
                    parsed_fieldName = readField(fieldElement, schemaAttributes, fieldElements, baseFields)
                    if parsed_fieldName:
                        fieldset.fields.append(parsed_fieldName)
    
        schema = InterfaceClass(name=policy_util.name(schemaName, tree),
                                bases=bases + policy_util.bases(schemaName, tree),
                                __module__=policy_util.module(schemaName, tree),
                                attrs=schemaAttributes)
        
        schema.setTaggedValue(FIELDSETS_KEY, fieldsets)
        
        # Save fieldsets
        
        # Let metadata handlers write metadata
        for handler_name, metadata_handler in field_metadata_handlers:
            for fieldName in schema:
                if fieldName in fieldElements:
                    metadata_handler.read(fieldElements[fieldName], schema, schema[fieldName])
        
        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.read(schema_element, schema)

        model.schemata[schemaName] = schema
    
    return model



__all__ = ('parse',)