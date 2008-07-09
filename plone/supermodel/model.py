from zope.interface import implements

from plone.supermodel.interfaces import IModel
from plone.supermodel.interfaces import IFieldset

# Keys for tagged values on interfaces

FILENAME_KEY = 'plone.supermodel.filename'       # absolute file name of model file
SCHEMA_NAME_KEY = 'plone.supermodel.schemaname'  # name of schema that was loaded from the model
FIELDSETS_KEY = 'plone.supermodel.fieldsets'     # list of fieldsets

class Fieldset(object):
    implements(IFieldset)
    
    def __init__(self, __name__, label=None, description=None, fields=None):
        self.__name__ = __name__
        self.label = label or __name__
        self.description = description
        
        if fields:
            self.fields = fields
        else:
            self.fields = []

    def __repr__(self):
        return "<Fieldset '%s' of %s>" % (self.__name__, ', '.join(self.fields))

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