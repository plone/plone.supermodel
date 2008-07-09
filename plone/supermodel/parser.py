from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component import getUtility, queryUtility, getUtilitiesFor

from plone.supermodel.interfaces import ISchemaPolicy
from plone.supermodel.interfaces import IFieldExportImportHandler

from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import IFieldMetadataHandler

from plone.supermodel.utils import ns

from plone.supermodel.model import Model

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
    
    for schema_element in root.findall(ns('schema')):
        schema_attributes = {}
        schema_metadata = {}
        
        schema_name = schema_element.get('name')
        if schema_name is None:
            schema_name = u""
        
        field_elements = {}
        
        for field_element in schema_element.findall(ns('field')):
            
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
            schema_attributes[field_name] = field
            field_elements[field_name] = field_element
            
        schema = InterfaceClass(name=policy_util.name(schema_name, tree),
                                bases=policy_util.bases(schema_name, tree),
                                __module__=policy_util.module(schema_name, tree),
                                attrs=schema_attributes)
        
        # Let metadata handlers write metadata
        for handler_name, metadata_handler in field_metadata_handlers:
            for field_name in schema:
                metadata_handler.read(field_elements[field_name], schema, schema[field_name])
        
        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.read(schema_element, schema)

        model.schemata[schema_name] = schema
    
    return model

__all__ = ('parse',)