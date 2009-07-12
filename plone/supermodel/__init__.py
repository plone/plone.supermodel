from StringIO import StringIO

import patches

from zope.interface import moduleProvides

from plone.supermodel.interfaces import FILENAME_KEY, IXMLToSchema
from plone.supermodel import parser
from plone.supermodel import serializer
from plone.supermodel import utils
from plone.supermodel import model

# Cache models by absolute filename
_model_cache = {}

def xmlSchema(filename, schema=u"", policy=u"", _frame=2):
    model = loadFile(filename, policy=policy, _frame=_frame+1)
    return model.schemata[schema]

def loadFile(filename, reload=False, policy=u"", _frame=2):
    global _model_cache
    path = utils.relativeToCallingPackage(filename, _frame)
    if reload or path not in _model_cache:
        parsed_model = parser.parse(path, policy=policy)
        for schema in parsed_model.schemata.values():
            schema.setTaggedValue(FILENAME_KEY, path)
        _model_cache[path] = parsed_model
    return _model_cache[path]

def loadString(model, policy=u""):
    return parser.parse(StringIO(model), policy=policy)
    
def serializeSchema(schema, name=u""):
    return serializeModel(model.Model({name: schema}))
    
def serializeModel(model):
    return serializer.serialize(model)

moduleProvides(IXMLToSchema)

__all__ = ('xmlSchema', 'loadFile', 'loadString', 'serializeSchema', 'serializeModel',)