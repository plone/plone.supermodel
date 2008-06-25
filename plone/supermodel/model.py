from zope.interface import implements

from plone.supermodel.interfaces import IModel

FILENAME_KEY = 'plone.supermodel.filename'
METADATA_KEY = 'plone.supermodel.metadata'
    
class Model(object):
    implements(IModel)
    
    def __init__(self, schemata=None):
        if schemata is None:
            schemata = {}
        self.schemata = schemata
    
    # Default schema + metadata
    
    @property
    def schema(self):
        return self.lookup_schema(schema=u"")

    @property
    def metadata(self):
        return self.lookup_metadata(schema=u"")

    # Lookup of named schema

    def lookup_schema(self, schema=u""):
        return self.schemata.get(schema, None)
    
    def lookup_metadata(self, schema=u""):
        schema_instance = self.lookup_schema(schema)
        if schema_instance is None:
            return None
        
        # Collate metadata from all base classes, but allow subclasses to
        # override.
        metadata = {}
        for s in list(reversed(schema_instance.getBases())) + [schema_instance]:
            schema_metadata = s.queryTaggedValue(METADATA_KEY)
            if schema_metadata is not None:
                metadata.update(schema_metadata)
                
        return metadata