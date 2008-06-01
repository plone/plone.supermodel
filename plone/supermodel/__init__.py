from zope.interface import moduleProvides

from plone.supermodel.interfaces import IXMLToSchema
from plone.supermodel import parser
from plone.supermodel import serializer
from plone.supermodel import utils

# Cache specs by absolute filename
_spec_cache = {}

def xml_schema(filename, schema=u""):
    return spec(filename, _calling_frame=3)[u"schemata"][schema]

def serialize_schema(schema, name=u""):
    return serialize_spec(dict(widgets={},
                               schemata={name : schema},
                              ))

def spec(filename, reload=False, _calling_frame=2):
    global _spec_cache
    path = utils.relative_to_calling_package(filename, _calling_frame)
    if reload or path not in _spec_cache:
        _spec_cache[path] = parser.parse(path)    
    return _spec_cache[path]
    
def serialize_spec(spec):
    return serializer.serialize(spec)

moduleProvides(IXMLToSchema)

__all__ = ('xml_schema', 'spec', 'serialize')