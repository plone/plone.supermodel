from StringIO import StringIO

from zope.interface import moduleProvides

from plone.supermodel.interfaces import IXMLToSchema
from plone.supermodel import parser
from plone.supermodel import serializer
from plone.supermodel import utils
from plone.supermodel import model

# Cache models by absolute filename
_model_cache = {}

def xml_schema(filename, schema=u"", policy=u"", _frame=2):
    model = load_file(filename, policy=policy, _frame=_frame+1)
    return model.schemata[schema].schema

def load_file(filename, reload=False, policy=u"", _frame=2):
    global _model_cache
    path = utils.relative_to_calling_package(filename, _frame)
    if reload or path not in _model_cache:
        model = parser.parse(path, policy=policy)
        for schema_info in model.schemata.values():
            schema_info.schema.setTaggedValue('plone.supermodel.filename', path)
        _model_cache[path] = model
    return _model_cache[path]

def load_string(model, policy=u""):
    return parser.parse(StringIO(model), policy=policy)
    
def serialize_schema(schema, name=u""):
    return serialize_model(model.Model({name: model.SchemaInfo(schema=schema, metadata={})}))
    
def serialize_model(model):
    return serializer.serialize(model) 

moduleProvides(IXMLToSchema)

__all__ = ('xml_schema', 'load_file', 'load_string', 'serialize_schema', 'serialize_model',)