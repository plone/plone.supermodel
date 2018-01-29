# -*- coding: utf-8 -*-
from plone.supermodel import model
from plone.supermodel import parser
from plone.supermodel import serializer
from plone.supermodel import utils
from plone.supermodel.interfaces import FILENAME_KEY
from plone.supermodel.interfaces import IXMLToSchema
from six import BytesIO
from six import StringIO
from zope.interface import moduleProvides

import six


# Cache models by absolute filename
_model_cache = {}


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
    source = StringIO(model) if six.PY2 \
        else BytesIO(six.binary_type(model, encoding='latin-1'))
    # source = StringIO(model) if six.PY2 else BytesIO(model)
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
