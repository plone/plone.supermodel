from zope.interface import implements

from plone.supermodel.interfaces import IModel

# Keys for tagged values on interfaces

FILENAME_KEY = 'plone.supermodel.filename'
SCHEMA_NAME_KEY = 'plone.supermodel.schemaname'
    
class Model(object):
    implements(IModel)
    
    def __init__(self, schemata=None):
        if schemata is None:
            schemata = {}
        self.schemata = schemata
    
    # Default schema
    
    @property
    def schema(self):
        return self.schemata.get(u"", None)