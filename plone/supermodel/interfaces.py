from zope.interface import Interface
from zope import schema

class IXMLToSchema(Interface):
    """Functionality to parse an XML representation of a schema and return
    an interface representation with zope.schema fields.
    
    A file can be parsed purely for a schema. This allows syntax like:
    
        class IMyType( xml_schema('schema.xml') ):
            pass
        
    To get more detailed information, including hints for setting up form
    widgets, use the full version:
    
        spec = spec('schema.xml')
    """
    
    def xml_schema(filename, schema=u""):
        """Given a filename relative to the current module, return an
        interface representing the schema contained in that file. If there
        are multiple <schema /> blocks, return the unnamed one, unless 
        a name is supplied, in which case the 'name' attribute of the schema
        will be matched to the schema name.
        
        Raises a KeyError if the schema cannot be found.
        Raises an IOError if the file cannot be opened.
        """
    
    
    def serialize_schema(schema, name=u""):
        """Return an XML string representing the given schema interface. This
        is a convenience method around the serialize_spec() method, below.
        """
    
    def spec(filename):
        """Return a model definition as contained in the given XML file, which
        is read relative to the current module.
        
        The return value is a dict with keys:
        
         - schemata -- a dict with keys of schema names and values of schema
            interfaces; one of the keys will be u"" (the default schema)
         - widgets -- a dict with keys of schema names and values of dicts,
            which in turn use field names as keys and contain widget hints
            as values
        """
        
    def serialize_spec(spec):
        """Return an XML string representing the given spec, as returned by
        the spec() method.
        """
        
class IFieldExportImportHandler(Interface):
    """Named utilities corresponding to node names should be registered for
    this interface. They will be called upon to build a schema fields out of
    DOM ndoes.
    """
    
    def read(node):
        """Read a field from the node and return a new instance
        """
        
    def write(field, field_name, field_type):
        """Create and return a new node representing the given field
        """