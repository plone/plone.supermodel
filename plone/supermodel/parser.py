from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component import getUtility, queryUtility

from plone.supermodel.interfaces import ISchemaPolicy
from plone.supermodel.interfaces import IFieldExportImportHandler

# Prefer lxml, but fall back on ElementTree if necessary

try:
    from lxml import etree as ElementTree
except ImportError:
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
    
    schemata = {}
    widgets = {}
    handlers = {}
    
    policy_util = getUtility(ISchemaPolicy, name=policy)
    
    for schema_element in root.findall('schema'):
        schema_attributes = {}
        schema_name = schema_element.get('name')
        if schema_name is None:
            schema_name = u""
        
        for field_element in schema_element.findall('field'):
            field_name = field_element.get('name')
            field_type = field_element.get('type')
            
            if field_name is None or field_type is None:
                raise ValueError("The attributes 'name' and 'type' are required for each <field /> element")
            
            handler = handlers.get(field_type, None)
            if handler is None:
                handler = handlers[field_type] = queryUtility(IFieldExportImportHandler, name=field_type)
                if handler is None:
                    raise ValueError("Field type %s specified for field %s is not supported" % (field_type, field_name,))
            
            schema_attributes[field_name] = handler.read(field_element)
            
        schemata[schema_name] = InterfaceClass(name=policy_util.name(schema_name, tree),
                                               bases=policy_util.bases(schema_name, tree),
                                               __module__=policy_util.module(schema_name, tree),
                                               attrs=schema_attributes)
    
    # TODO: build widgets
    
    return dict(schemata=schemata,
                widget=widgets)

__all__ = ('parse',)