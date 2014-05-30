from zope.interface import Interface
from zope.interface.interfaces import IInterface
import zope.schema

# Keys for tagged values on interfaces

FILENAME_KEY = 'plone.supermodel.filename'    # absolute file name of model file
SCHEMA_NAME_KEY = 'plone.supermodel.schemaname'  # name of schema that was loaded from the model
FIELDSETS_KEY = 'plone.supermodel.fieldsets'   # list of fieldsets
PRIMARY_FIELDS_KEY = 'plone.supermodel.primary'  # Primary fields (requires plone.rfc822)

# The namespace for the default supermodel schema/field parser

XML_NAMESPACE = u"http://namespaces.plone.org/supermodel/schema"
I18N_NAMESPACE = u'http://xml.zope.org/namespaces/i18n'


class ISchema(IInterface):
    """Describes a schema as generated by this library
    """


class IModel(Interface):
    """Describes a model as generated by this library
    """

    schema = zope.schema.InterfaceField(title=u"Default schema",
                                        readonly=True)

    schemata = zope.schema.Dict(title=u"Schemata",
                                key_type=zope.schema.TextLine(title=u"Schema name",
                                        description=u"Default schema is under the key u''."),
                                value_type=zope.schema.Object(title=u"Schema interface",
                                        schema=ISchema))


class IFieldset(Interface):
    """Describes a grouping of fields in the schema
    """

    __name__ = zope.schema.TextLine(title=u"Fieldset name")

    label = zope.schema.TextLine(title=u"Label")

    description = zope.schema.TextLine(title=u"Long description", required=False)

    fields = zope.schema.List(title=u"Field names",
                              value_type=zope.schema.TextLine(title=u"Field name"))


class ISchemaPlugin(Interface):
    """A named adapter that provides additional functionality during schema
    construction.

    Execution is deferred until the full supermodel environment is available.
    """

    order = zope.schema.Int(title=u"Order", required=False,
                            description=u"Sort key for plugin execution order")

    def __call__():
        """Execute plugin
        """


class IXMLToSchema(Interface):
    """Functionality to parse an XML representation of a schema and return
    an interface representation with zope.schema fields.

    A file can be parsed purely for a schema. This allows syntax like:

        schema = xmlSchema('schema.xml')

    If a file contains multiple schemata, you can load them all using:

        model = loadFile('schema.xml')
    """

    def xmlSchema(filename, schema=u"", policy=u""):
        """Given a filename relative to the current module, return an
        interface representing the schema contained in that file. If there
        are multiple <schema /> blocks, return the unnamed one, unless
        a name is supplied, in which case the 'name' attribute of the schema
        will be matched to the schema name.

        The policy argument can be used to pick a different parsing policy.
        Policies must be registered as named utilities providing
        ISchemaPolicy.

        Raises a KeyError if the schema cannot be found.
        Raises an IOError if the file cannot be opened.
        """

    def loadFile(filename, reload=False, policy=u""):
        """Return an IModel as contained in the given XML file, which is read
        relative to the current module (unless it is an absolute path).

        If reload is True, reload a schema even if it's cached. If policy
        is given, it can be used to select a custom schema parsing policy.
        Policies must be registered as named utilities providing
        ISchemaPolicy.
        """

    def loadString(model, policy=u""):
        """Load a model from a string rather than a file.
        """

    def serializeSchema(schema, name=u""):
        """Return an XML string representing the given schema interface. This
        is a convenience method around the serializeModel() method, below.
        """

    def serializeModel(model):
        """Return an XML string representing the given model, as returned by
        the loadFile() or loadString() method.
        """


class ISchemaPolicy(Interface):
    """A utility that provides some basic attributes of the generated
    schemata. Provide a custom one to make policy decisions about where
    generated schemata live, what bases they have and how they are named.
    """

    def module(schemaName, tree):
        """Return the module name to use.
        """

    def bases(schemaName, tree):
        """Return the bases to use.
        """

    def name(schemaName, tree):
        """Return the schema name to use
        """


class IFieldExportImportHandler(Interface):
    """Named utilities corresponding to node names should be registered for
    this interface. They will be called upon to build a schema fields out of
    DOM ndoes.
    """

    def read(node):
        """Read a field from the node and return a new instance
        """

    def write(field, fieldName, fieldType, elementName='field'):
        """Create and return a new node representing the given field
        """


class ISchemaMetadataHandler(Interface):
    """A third party application can register named utilities providing this
    interface. For each schema that is parsed in a model, the read() method
    will be called.
    """

    namespace = zope.schema.URI(title=u"XML namespace used by this handler", required=False)
    prefix = zope.schema.ASCII(title=u"Preferred XML schema namespace for serialisation", required=False)

    def read(schemaNode, schema):
        """Called once the schema in the given <schema /> node has been
        read. schema is the schema interface that was read.
        """

    def write(schemaNode, schema):
        """Write the metadata contained in the given schema, to the
        schemaNode. The node will already exist and be populated with
        standard data.
        """


class IFieldMetadataHandler(Interface):
    """A third party application can register named utilities providing this
    interface. For each field that is parsed in a schema, the read() method
    will be called.
    """

    namespace = zope.schema.URI(title=u"XML namespace used by this handler", required=False)
    prefix = zope.schema.ASCII(title=u"Preferred XML schema namespace for serialisation", required=False)

    def read(fieldNode, schema, field):
        """Called once the field in the given <field /> node has been
        read. field is the field instance that was read. schema is the schema
        it is a part of.
        """

    def write(fieldNode, schema, field):
        """Write the metadata for the field in the given schema to the
        fieldNode. The node will already exist and be populated with
        standard data.
        """


class IFieldNameExtractor(Interface):
    """Adapter to determine the canonical name of a field
    """

    def __call__():
        """Return the name of the adapted field
        """


class IToUnicode(Interface):
    """Reciprocal to IToUnicode. Adapting a field to this interface allows
    a string representation to be extracted.
    """

    def toUnicode(value):
        """Convert the field value to a unicode string.
        """


class IDefaultFactory(Interface):
    """A default factory that does not require a context.

    This is a marker for defaultFactory callables that do
    not need an interface.
    """

    def __call__():
        """Returns a default value for the field."""


class IInvariant(Interface):
    """Marker interface for a callable used as a form invariant.
    """
    
    def __call__(data):
        """Returns None or raises zope.interface.Invalid
        """
