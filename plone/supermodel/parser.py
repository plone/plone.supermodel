from zope.interface import Interface, implements
from zope.interface.interface import InterfaceClass
from zope.component import getUtility, queryUtility
    
from plone.supermodel.interfaces import IFieldExportImportHandler

# Prefer lxml, but fall back on ElementTree if necessary

try:
    from lxml import etree as ElementTree
except ImportError:
    from elementtree import ElementTree

# Helper adapters

class ISchemaPolicy(Interface):
    """A utility that provides some basic attributes of the generated
    schemata. Override this to make policy decisions about where generated
    schemata live, what bases they have and how they are named.
    """

    def module(schema_name, tree, default_module):
        """Return the module name to use.
        """
        
    def bases(schema_name, tree, default_bases):
        """Return the bases to use.
        """
        
    def name(schema_name, tree):
        """Return the schema name to use
        """

class DefaultSchemaPolicy(object):
    implements(ISchemaPolicy)
    
    def module(self, schema_name, tree, default_module):
        if default_module:
            return default_module
        else:
            return 'plone.supermodel.generated'
        
    def bases(self, schema_name, tree, default_bases):
        if default_bases:
            return default_bases
        else:
            return ()
        
    def name(self, schema_name, tree):
        return schema_name

# Algorithm

def parse(source, module=None, bases=()):
    tree = ElementTree.parse(source)
    root = tree.getroot()
    
    schemata = {}
    widgets = {}
    handlers = {}
    
    policy = getUtility(ISchemaPolicy)
    
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
            
        schemata[schema_name] = InterfaceClass(name=policy.name(schema_name, tree),
                                               bases=policy.bases(schema_name, tree, bases),
                                               __module__=policy.module(schema_name, tree, module),
                                               attrs=schema_attributes)
    
    # TODO: build widgets
    
    return dict(schemata=schemata,
                widget=widgets)

__all__ = ('parse',)