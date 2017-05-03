# -*- coding: utf-8 -*-
import sys
PY3 = sys.version_info[0] == 3

from plone.supermodel import model
from plone.supermodel import parser
from plone.supermodel import serializer
from plone.supermodel import utils
from plone.supermodel.interfaces import FILENAME_KEY
from plone.supermodel.interfaces import IXMLToSchema
from six import StringIO
from zope.interface import moduleProvides

if PY3:
    from io import BytesIO
else:
    from StringIO import StringIO

# Cache models by absolute filename
_model_cache = {}


def b(s):
    if PY3:
        if not isinstance(s, str):
            return s
        return bytes(s, encoding='latin-1')
    else:
        return s


def xmlSchema(filename, schema=u"", policy=u"", _frame=2):
    _model = loadFile(filename, policy=policy, _frame=_frame + 1)
    return _model.schemata[schema]


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
    if PY3:
        source = BytesIO(b(model))
    else:
        source = StringIO(model)
    return parser.parse(source, policy=policy)


def serializeSchema(schema, name=u""):
    return serializeModel(model.Model({name: schema}))


def serializeModel(model):
    return serializer.serialize(model)


moduleProvides(IXMLToSchema)

__all__ = (
    'xmlSchema',
    'loadFile',
    'loadString',
    'serializeSchema',
    'serializeModel'
)
