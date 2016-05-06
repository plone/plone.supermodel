================================================
Loading plone.supermodel schemata from XML files
================================================

plone.supermodel contains tools for reading and writing zope.schema-based
interface definitions from/to XML.

This package provides convenience base classes and directives for
creating interfaces.

Setup
-----

First, load this package's configuration:

    >>> configuration = """\
    ... <configure
    ...      xmlns="http://namespaces.zope.org/zope"
    ...      i18n_domain="plone.supermodel.tests">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...
    ...     <include package="plone.supermodel" />
    ...
    ... </configure>
    ... """

    >>> from StringIO import StringIO
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(StringIO(configuration))

We will also need a temporary directory for storing test schema files.

    >>> import tempfile, os.path, shutil
    >>> tmpdir = tempfile.mkdtemp()

Building interfaces from schema files
--------------------------------------

Let us begin by writing a schema file. See plone.supermodel for more details
on how this is structured.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...         <field type="zope.schema.TextLine" name="title">
    ...             <title>Title</title>
    ...             <required>True</required>
    ...         </field>
    ...         <field type="zope.schema.Text" name="body">
    ...             <title>Body text</title>
    ...             <required>True</required>
    ...             <max_length>10000</max_length>
    ...         </field>
    ...     </schema>
    ...
    ...     <schema name="metadata">
    ...         <field type="zope.schema.Datetime" name="created">
    ...             <title>Created date</title>
    ...             <required>False</required>
    ...         </field>
    ...         <field type="zope.schema.TextLine" name="creator">
    ...             <title>Creator</title>
    ...             <description>Name of the creator</description>
    ...             <required>True</required>
    ...         </field>
    ...     </schema>
    ...
    ... </model>
    ... """

Ordinarily, this would be in a file in the same directory as the module
containing the interface being defined. Here, we need to place it in the
temporary directory created above.

    >>> schema_filename = os.path.join(tmpdir, "schema.xml")
    >>> schema_file = open(schema_filename, "w")
    >>> schema_file.write(schema)
    >>> schema_file.close()

We can now define a schema, using the directives defined in this package:

    >>> from plone.supermodel import model
    >>> class ITestContent(model.Schema):
    ...     model.load(schema_filename)

Note: If the schema filename is not an absolute path, it will be found
relative to the module where the interface is defined.

The interface should have the fields of the default (unnamed) schema:

    >>> from zope.schema import getFieldNamesInOrder
    >>> getFieldNamesInOrder(ITestContent)
    ['title', 'body']

It also contains the filename that the schema was loaded from and the schema
name as a tagged values in the base interface.

    >>> from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY
    >>> ITestContent.getTaggedValue(FILENAME_KEY) # doctest: +ELLIPSIS
    '.../schema.xml'
    >>> ITestContent.getTaggedValue(SCHEMA_NAME_KEY)
    u''

We can also use a different, named schema:

    >>> class ITestMetadata(model.Schema):
    ...     """Test metadata schema, built from XML
    ...     """
    ...     model.load(schema_filename, schema=u"metadata")

    >>> getFieldNamesInOrder(ITestMetadata)
    ['created', 'creator']

Again, the interface has tagged values for the filename and schema name.

    >>> ITestMetadata.getTaggedValue(FILENAME_KEY) # doctest: +ELLIPSIS
    '.../schema.xml'
    >>> ITestMetadata.getTaggedValue(SCHEMA_NAME_KEY)
    u'metadata'

Adding and overriding fields
----------------------------

When loading a schema from XML, fields can still be added in code. If a
field defined in code has the same name as one loaded from the file, the
former will override the latter.

    >>> import zope.schema
    >>> class ITestContentWithNewFields(model.Schema):
    ...     model.load(schema_filename)
    ...
    ...     title = zope.schema.TextLine(title=u"Title", default=u"Default title")
    ...     postscript = zope.schema.Text(title=u"Postscript")

    >>> getFieldNamesInOrder(ITestContentWithNewFields)
    ['body', 'title', 'postscript']

    >>> ITestContentWithNewFields[u'title'].default
    u'Default title'

Fieldset support
----------------

plone.supermodel can use a tagged value to store groupings of fields into
fieldsets. The same tagged value can be populated using a directive:

    >>> class IGrouped(model.Schema):
    ...
    ...     model.fieldset(u"default", label="Default", fields=['title', 'description'])
    ...     model.fieldset(u"metadata", label="Metadata", fields=['publication_date'], layout='concise')
    ...
    ...     title = zope.schema.TextLine(title=u"Title")
    ...     description = zope.schema.TextLine(title=u"Description")
    ...
    ...     publication_date = zope.schema.Date(title=u"Publication date")

    >>> from plone.supermodel.interfaces import FIELDSETS_KEY
    >>> IGrouped.getTaggedValue(FIELDSETS_KEY)
    [<Fieldset 'default' order 9999 of title, description>, <Fieldset 'metadata' order 9999 of publication_date>]

Extra parameters, such as the layout parameter for the metadata fieldset, are
accessible as attributes on the fieldset:

    >>> metadata = IGrouped.getTaggedValue(FIELDSETS_KEY)[1]
    >>> metadata.layout
    'concise'


Primary field support
---------------------

In combination with plone.rfc822, primary fields may be marked:

    >>> class IFields(model.Schema):
    ...     title = zope.schema.TextLine(title=u"Title")
    ...     description = zope.schema.TextLine(title=u"Description")
    ...
    ...     model.primary('body')
    ...     body = zope.schema.Text(title=u"Body")

    >>> from plone.rfc822.interfaces import IPrimaryField
    >>> IPrimaryField.providedBy(IFields['body'])
    True

Cleanup
-------

Finally, let's clean up the temporary directory.

    >>> shutil.rmtree(tmpdir)
