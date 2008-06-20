from zope.interface import implements

from plone.supermodel.interfaces import ISchemaInfo
from plone.supermodel.interfaces import IModel

class SchemaInfo(object):
    implements(ISchemaInfo)
    
    def __init__(self, schema=None, metadata=None):
        if metadata is None:
            metadata = {}

        self.schema = schema
        self.metadata = metadata
    
class Model(object):
    implements(IModel)
    
    def __init__(self, schemata=None):
        if schemata is None:
            schemata = {}
        self.schemata = schemata
    
    @property
    def schema(self):
        default_schema = self.schemata.get(u"", None)
        if default_schema is None:
            return None
        else:
            return default_schema.schema

    @property
    def metadata(self):
        default_schema = self.schemata.get(u"", None)
        if default_schema is None:
            return None
        else:
            return default_schema.metadata
        