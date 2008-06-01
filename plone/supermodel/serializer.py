from zope.interface import Interface, implements
from zope.component import adapts

from zope.schema.interfaces import IField
from zope.schema import getFieldsInOrder

from zope.component import queryUtility
from plone.supermodel.interfaces import IFieldExportImportHandler

# Prefer lxml, but fall back on ElementTree if necessary

try:
    
    from lxml import etree as ElementTree
    
    def pretty_xml(tree):
        return ElementTree.tostring(tree, pretty_print=True)
    
except ImportError:
    
    from elementtree import ElementTree

    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for elem in elem:
                indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def pretty_xml(tree):
        indent(tree)
        return ElementTree.tostring(tree)

# Helper adapters

class IFieldNameExtractor(Interface):
    """Adapter to determine the canonical name of a field
    """
    
    def __call__():
        """Return the name of the adapted field
        """

class DefaultFieldNameExtractor(object):
    """Extract a name
    """
    implements(IFieldNameExtractor)
    adapts(IField)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self):
        field_module = self.context.__class__.__module__
        
        # workaround for the fact that some fields are defined in one
        # module, but commonly used from zope.schema.*

        if field_module.startswith('zope.schema._bootstrapfields'):
            field_module = field_module.replace("._bootstrapfields", "")
        elif field_module.startswith('zope.schema._field'):
            field_module = field_module.replace("._field", "")
        
        return "%s.%s" % (field_module, self.context.__class__.__name__,)

# Algorithm

def serialize(spec):
    handlers = {}

    model = ElementTree.Element('model')
    
    for schema_name, schema in spec['schemata'].items():
        schema_element = ElementTree.Element('schema')
        if schema_name:
            schema_element.set('name', schema_name)
        for field_name, field in getFieldsInOrder(schema):

            name_extractor = IFieldNameExtractor(field)
            field_type = name_extractor()
            handler = handlers.get(field_type, None)
            if handler is None:
                handler = handlers[field_type] = queryUtility(IFieldExportImportHandler, name=field_type)
                if handler is None:
                    raise ValueError("Field type %s specified for field %s is not supported" % (field_type, field_name,))
            field_element = handler.write(field, field_name, field_type)
            if field_element is not None:
                schema_element.append(field_element)
        model.append(schema_element)

    # TODO: write widgets
    
    return pretty_xml(model)

__all__ = ('serialize',)