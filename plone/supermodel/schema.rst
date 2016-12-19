==================================================
plone.supermodel: content schemata loaded from XML
==================================================

This package allows content schemata to be read and written as XML. It has a
standard importer and serialiser for interfaces that contain zope.schema
fields. The format is general enough to be able to handle future fields
easily, so long as they are properly specified through interfaces.

Parsing and serializing simple schemata
---------------------------------------

Before we can begin, we must register the field handlers that know how to
import and export fields from/to XML. These are registered as named utilities,
and can be loaded from the configure.zcml file of plone.supermodel.

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

Next, let's define a sample model with a single, unnamed schema.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...         <field type="zope.schema.TextLine" name="title">
    ...             <title>Title</title>
    ...             <required>True</required>
    ...         </field>
    ...         <field type="zope.schema.Text" name="description">
    ...             <!-- we can also put comments in here -->
    ...             <title>Description</title>
    ...             <description>A short summary</description>
    ...             <required>False</required>
    ...             <min_length>10</min_length>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

We can parse this model using the loadString() function:

    >>> from plone.supermodel import loadString
    >>> model = loadString(schema)

This will load one schema, with the default name u"":

    >>> model.schemata.keys()
    [u'']

We can inspect this schema and see that it contains zope.schema fields with
attributes corresponding to the values set in XML.

    >>> schema = model.schema # shortcut to model.schemata[u""]

    >>> from zope.schema import getFieldNamesInOrder
    >>> getFieldNamesInOrder(schema)
    ['title', 'description']

    >>> schema['title'].title
    u'Title'
    >>> schema['title'].required
    True

    >>> schema['description'].title
    u'Description'
    >>> schema['description'].description
    u'A short summary'
    >>> schema['description'].required
    False
    >>> schema['description'].min_length
    10

If we try to parse a schema that has errors, we'll get a useful
SupermodelParseError that includes contextual information. (This requires
lxml.)

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...         <field type="aint_gonna_exist" name="title">
    ...         </field>
    ...     </schema>
    ... </model>
    ... """
    >>> loadString(schema)
    Traceback (most recent call last):
    ...
    SupermodelParseError: Field type aint_gonna_exist specified for field title is not supported
      File "<unknown>", line ...

In addition to parsing, we can serialize a model to an XML representation:

    >>> from plone.supermodel import serializeModel
    >>> print serializeModel(model) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema>
        <field name="title" type="zope.schema.TextLine">
          <title>Title</title>
        </field>
        <field name="description" type="zope.schema.Text">
          <description>A short summary</description>
          <min_length>10</min_length>
          <required>False</required>
          <title>Description</title>
        </field>
      </schema>
    </model>

Building interfaces from schemata
---------------------------------

Above, we saw how to parse a schema from a file directly. Next, let's see how
this can be used more practically to define a custom interface. Here, we will
use two schemata in one file.

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
containing the interface being defined. Here, we need to create a temporary
directory.

    >>> import tempfile, os.path, shutil
    >>> tmpdir = tempfile.mkdtemp()
    >>> schema_filename = os.path.join(tmpdir, "schema.xml")
    >>> schema_file = open(schema_filename, "w")
    >>> schema_file.write(schema)
    >>> schema_file.close()

We can define interfaces from this using a helper function:

    >>> from plone.supermodel import xmlSchema
    >>> ITestContent = xmlSchema(schema_filename)

Note: If the schema filename is not an absolute path, it will be found
relative to the module where the interface is defined.

After being loaded, the interface should have the fields of the default
(unnamed) schema:

    >>> getFieldNamesInOrder(ITestContent)
    ['title', 'body']

We can also use a different, named schema:

    >>> ITestMetadata = xmlSchema(schema_filename, schema=u"metadata")
    >>> getFieldNamesInOrder(ITestMetadata)
    ['created', 'creator']

Of course, a schema can also be written to XML. Either, you can build a model
dict as per the serializeModel() method seen above, or you can write a model
of just a single schema using serializeSchema():

    >>> from plone.supermodel import serializeSchema
    >>> print serializeSchema(ITestContent) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema>
        <field name="title" type="zope.schema.TextLine">
          <title>Title</title>
        </field>
        <field name="body" type="zope.schema.Text">
          <max_length>10000</max_length>
          <title>Body text</title>
        </field>
      </schema>
    </model>

    >>> print serializeSchema(ITestMetadata, name=u"metadata") # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema name="metadata">
        <field name="created" type="zope.schema.Datetime">
          <required>False</required>
          <title>Created date</title>
        </field>
        <field name="creator" type="zope.schema.TextLine">
          <description>Name of the creator</description>
          <title>Creator</title>
        </field>
      </schema>
    </model>

Finally, let's clean up the temporary directory.

    >>> shutil.rmtree(tmpdir)

Base interface support
----------------------

When building a schema interface from XML, it is possible to specify a base
interface. This is analogous to "subclassing" an existing interface. The XML
schema representation can override and/or extend fields from the base.

For the purposes of this test, we have defined a dummy interface in
plone.supermodel.tests. We can't define it in the doctest, because the import
resolver needs to have a proper module path. The interface looks like this
though:

    class IBase(Interface):
        title = zope.schema.TextLine(title=u"Title")
        description = zope.schema.TextLine(title=u"Description")
        name = zope.schema.TextLine(title=u"Name")

In real life, you'd more likely have a dotted name like
my.package.interfaces.IBase, of course.

Then, let's define a schema that is based on this interface.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema based-on="plone.supermodel.tests.IBase">
    ...         <field type="zope.schema.Text" name="description">
    ...             <title>Description</title>
    ...             <description>A short summary</description>
    ...         </field>
    ...         <field type="zope.schema.Int" name="age">
    ...             <title>Age</title>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

Here, notice the use of the 'based-on' attribute, which specifies a dotted
name to the base interface. It is possible to specify multiple interfaces
as a space-separated list. However, if you find that you need this, you
may want to ask yourself why. :) Inside the schema proper, we override the
'description' field and add a new field, 'age'.

When we load this model, we should find that the __bases__ list of the
generated interface contains the base schema.

    >>> model = loadString(schema)
    >>> model.schema.__bases__
    (<InterfaceClass plone.supermodel.tests.IBase>, <SchemaClass plone.supermodel.model.Schema>)

The fields of the base interface will also be replicated in the new schema.

    >>> getFieldNamesInOrder(model.schema)
    ['title', 'description', 'name', 'age']

Notice how the order of the 'description' field is dictated by where it
appeared in the base interface, not where it appears in the XML schema.

We should also verify that the description field was indeed overridden:

    >>> model.schema['description'] # doctest: +ELLIPSIS
    <zope.schema._bootstrapfields.Text object at ...>

Finally, let's verify that bases are preserved upon serialisation:

    >>> print serializeSchema(model.schema) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema based-on="plone.supermodel.tests.IBase">
        <field name="description" type="zope.schema.Text">
          <description>A short summary</description>
          <title>Description</title>
        </field>
        <field name="age" type="zope.schema.Int">
          <title>Age</title>
        </field>
      </schema>
    </model>

Fieldset support
----------------

It is often useful to be able to group form fields in the same schema into
fieldsets, for example for form rendering. While plone.supermodel doesn't have
anything to do with such rendering, it does support some markup to make it
possible to define fieldsets. These are stored in a tagged value on the
generated interface, which can then be used by other code.

Fieldsets can be defined from and serialised to XML, using the <fieldset />
tag to wrap a sequence of fields.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...
    ...         <field type="zope.schema.TextLine" name="title">
    ...             <title>Title</title>
    ...             <required>True</required>
    ...         </field>
    ...         <field type="zope.schema.Text" name="body">
    ...             <title>Body text</title>
    ...             <required>True</required>
    ...             <max_length>10000</max_length>
    ...         </field>
    ...
    ...         <fieldset name="dates" label="Dates" description="Standard dates" order="1">
    ...             <field type="zope.schema.Date" name="publication_date">
    ...                 <title>Publication date</title>
    ...             </field>
    ...         </fieldset>
    ...
    ...         <field type="zope.schema.TextLine" name="author">
    ...             <title>Author</title>
    ...         </field>
    ...
    ...         <fieldset name="dates" label="Ignored" description="Ignored">
    ...             <field type="zope.schema.Date" name="expiry_date">
    ...                 <title>Expiry date</title>
    ...             </field>
    ...             <field type="zope.schema.Date" name="notification_date">
    ...                 <title>Notification date</title>
    ...             </field>
    ...         </fieldset>
    ...     </schema>
    ...
    ...     <schema name="metadata">
    ...
    ...         <fieldset name="standard" label="Standard" />
    ...         <fieldset name="dates" label="Metadata dates" />
    ...         <fieldset name="author" label="Author info" />
    ...
    ...         <fieldset name="dates">
    ...             <field type="zope.schema.Datetime" name="created">
    ...                 <title>Created date</title>
    ...                 <required>False</required>
    ...             </field>
    ...         </fieldset>
    ...
    ...         <fieldset name="standard">
    ...             <field type="zope.schema.TextLine" name="creator">
    ...                 <title>Creator</title>
    ...                 <description>Name of the creator</description>
    ...                 <required>True</required>
    ...             </field>
    ...         </fieldset>
    ...     </schema>
    ...
    ... </model>
    ... """

Fields outside any <fieldset /> tag are not placed in any fieldset. An
empty <fieldset /> will be recorded as one having no fields. This is sometimes
useful to control the order of fieldsets, if those are to be filled later.

If there are two <fieldset /> blocks with the same name, fields from the second
will be appended to the first, and the label and description will be kept
from the first one, as appropriate.

Note that fieldsets are specific to each schema, i.e. the fieldset in the
default schema above is unrelated to the one in the metadata schema.

    >>> model = loadString(schema)
    >>> getFieldNamesInOrder(model.schema)
    ['title', 'body', 'publication_date', 'author', 'expiry_date', 'notification_date']

    >>> getFieldNamesInOrder(model.schemata['metadata'])
    ['created', 'creator']

    >>> from plone.supermodel.interfaces import FIELDSETS_KEY
    >>> model.schema.getTaggedValue(FIELDSETS_KEY)
    [<Fieldset 'dates' order 1 of publication_date, expiry_date, notification_date>]

    >>> model.schemata[u"metadata"].getTaggedValue(FIELDSETS_KEY)
    [<Fieldset 'standard' order 9999 of creator>, <Fieldset 'dates' order 9999 of created>, <Fieldset 'author' order 9999 of >]

When we serialise a schema with fieldsets, fields will be grouped by
fieldset.

    >>> print serializeModel(model) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema>
        <field name="title" type="zope.schema.TextLine">
          <title>Title</title>
        </field>
        <field name="body" type="zope.schema.Text">
          <max_length>10000</max_length>
          <title>Body text</title>
        </field>
        <field name="author" type="zope.schema.TextLine">
          <title>Author</title>
        </field>
        <fieldset name="dates" label="Dates" description="Standard dates">
          <field name="publication_date" type="zope.schema.Date">
            <title>Publication date</title>
          </field>
          <field name="expiry_date" type="zope.schema.Date">
            <title>Expiry date</title>
          </field>
          <field name="notification_date" type="zope.schema.Date">
            <title>Notification date</title>
          </field>
        </fieldset>
      </schema>
      <schema name="metadata">
        <fieldset name="standard" label="Standard">
          <field name="creator" type="zope.schema.TextLine">
            <description>Name of the creator</description>
            <title>Creator</title>
          </field>
        </fieldset>
        <fieldset name="dates" label="Metadata dates">
          <field name="created" type="zope.schema.Datetime">
            <required>False</required>
            <title>Created date</title>
          </field>
        </fieldset>
        <fieldset name="author" label="Author info"/>
      </schema>
    </model>

Invariant Support
-----------------

We may specify one or more invariants for the form via the "invariant" tag with
a dotted name for the invariant function.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...         <invariant>plone.supermodel.tests.dummy_invariant</invariant>
    ...         <invariant>plone.supermodel.tests.dummy_invariant_prime</invariant>
    ...         <field type="zope.schema.Text" name="description">
    ...             <title>Description</title>
    ...             <description>A short summary</description>
    ...         </field>
    ...         <field type="zope.schema.Int" name="age">
    ...             <title>Age</title>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

    >>> model = loadString(schema)
    >>> model.schema.getTaggedValue('invariants')
    [<function dummy_invariant at ...>, <function dummy_invariant_prime at ...>]

When invariants are checked for our model.schema, we'll see our invariant
in action.

    >>> model.schema.validateInvariants(object())
    Traceback (most recent call last):
    ...
    Invalid: Yikes! Invalid

The model's serialization should include the invariant.

    >>> print serializeModel(model) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema>
        <invariant>plone.supermodel.tests.dummy_invariant</invariant>
        <invariant>plone.supermodel.tests.dummy_invariant_prime</invariant>
        <field name="description" type="zope.schema.Text">
          <description>A short summary</description>
          <title>Description</title>
        </field>
        <field name="age" type="zope.schema.Int">
          <title>Age</title>
        </field>
      </schema>
    </model>

Invariant functions must provide plone.supermodel.interfaces.IInvariant
or we won't accept them.

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema">
    ...     <schema>
    ...         <invariant>plone.supermodel.tests.dummy_unmarkedInvariant</invariant>
    ...         <field type="zope.schema.Text" name="description">
    ...             <title>Description</title>
    ...             <description>A short summary</description>
    ...         </field>
    ...         <field type="zope.schema.Int" name="age">
    ...             <title>Age</title>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

    >>> model = loadString(schema)
    Traceback (most recent call last):
    ...
    SupermodelParseError: Invariant functions must provide plone.supermodel.interfaces.IInvariant
      File "<unknown>", line ...


Internationalization
--------------------

Translation domains and message ids can be specified for text
that is interpreted as unicode. This will result in deserialization
as a zope.i18nmessageid message id rather than a basic Unicode string::

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema"
    ...        xmlns:i18n="http://xml.zope.org/namespaces/i18n"
    ...        i18n:domain="plone.supermodel">
    ...     <schema>
    ...
    ...         <field type="zope.schema.TextLine" name="title">
    ...             <title i18n:translate="supermodel_test_title">Title</title>
    ...         </field>
    ...
    ...         <field type="zope.schema.TextLine" name="description">
    ...             <title i18n:translate="">description</title>
    ...         </field>
    ...
    ...         <field type="zope.schema.TextLine" name="feature">
    ...             <title i18n:translate="domain_test"
    ...                    i18n:domain="other">feature</title>
    ...         </field>
    ...
    ...     </schema>
    ... </model>
    ... """
    >>> model = loadString(schema)
    >>> msgid = model.schema['title'].title
    >>> msgid
    u'supermodel_test_title'
    >>> type(msgid)
    <... 'zope.i18nmessageid.message.Message'>
    >>> msgid.default
    u'Title'
    >>> print serializeModel(model) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns="http://namespaces.plone.org/supermodel/schema" i18n:domain="plone.supermodel">
      <schema>
        <field name="title" type="zope.schema.TextLine">
          <title i18n:translate="supermodel_test_title">Title</title>
        </field>
        <field name="description" type="zope.schema.TextLine">
          <title i18n:translate="">description</title>
        </field>
        <field name="feature" type="zope.schema.TextLine">
          <title i18n:domain="other" i18n:translate="domain_test">feature</title>
        </field>
      </schema>
    </model>

Creating custom metadata handlers
---------------------------------

The plone.supermodel format is extensible with custom utilities that can
write to a "metadata" dictionary. Such utilities may for example read
information captured in attributes in particular namespaces.

Let's imagine we wanted to make it possible to override form layout on a
per-schema level, and override widgets on a per-field level. For this, we
may expect to be able to parse a format like this:

    >>> schema = """\
    ... <?xml version="1.0" encoding="UTF-8"?>
    ... <model xmlns="http://namespaces.plone.org/supermodel/schema"
    ...        xmlns:ui="http://namespaces.acme.com/ui">
    ...     <schema ui:layout="horizontal">
    ...         <field type="zope.schema.TextLine" name="title"
    ...             ui:widget="largetype">
    ...             <title>Title</title>
    ...             <required>True</required>
    ...         </field>
    ...         <field type="zope.schema.Text" name="description">
    ...             <title>Description</title>
    ...             <description>A short summary</description>
    ...             <required>False</required>
    ...             <min_length>10</min_length>
    ...         </field>
    ...     </schema>
    ... </model>
    ... """

We can register schema and field metadata handlers as named utilities.
Metadata handlers should be able to reciprocally read and write metadata.

    >>> from zope.interface import implements
    >>> from zope.component import provideUtility

    >>> from plone.supermodel.interfaces import ISchemaMetadataHandler
    >>> from plone.supermodel.utils import ns

    >>> class FormLayoutMetadata(object):
    ...     implements(ISchemaMetadataHandler)
    ...
    ...     namespace = "http://namespaces.acme.com/ui"
    ...     prefix = "ui"
    ...
    ...     def read(self, schemaNode, schema):
    ...         layout = schemaNode.get(ns('layout', self.namespace))
    ...         if layout:
    ...             schema.setTaggedValue(u'acme.layout', layout)
    ...
    ...     def write(self, schemaNode, schema):
    ...         layout = schema.queryTaggedValue(u'acme.layout', None)
    ...         if layout:
    ...             schemaNode.set(ns('layout', self.namespace), layout)

    >>> provideUtility(component=FormLayoutMetadata(), name='acme.ui.schema')

    >>> from plone.supermodel.interfaces import IFieldMetadataHandler
    >>> class FieldWidgetMetadata(object):
    ...     implements(IFieldMetadataHandler)
    ...
    ...     namespace = "http://namespaces.acme.com/ui"
    ...     prefix = "ui"
    ...
    ...     def read(self, fieldNode, schema, field):
    ...         name = field.__name__
    ...         widget = fieldNode.get(ns('widget', self.namespace))
    ...         if widget:
    ...             widgets = schema.queryTaggedValue(u'acme.widgets', {})
    ...             widgets[name] = widget
    ...             schema.setTaggedValue(u'acme.widgets', widgets)
    ...
    ...     def write(self, fieldNode, schema, field):
    ...         name = field.__name__
    ...         widget = schema.queryTaggedValue(u'acme.widgets', {}).get(name, {})
    ...         if widget:
    ...             fieldNode.set(ns('widget', self.namespace), widget)

    >>> provideUtility(component=FieldWidgetMetadata(), name='acme.ui.fields')

When this model is loaded, utilities above will be invoked for each schema
and each field, respectively.

    >>> model = loadString(schema)

    >>> model.schema.getTaggedValue('acme.layout')
    'horizontal'

    >>> model.schema.getTaggedValue('acme.widgets')
    {'title': 'largetype'}

Of course, we can also serialize the schema back to XML. Here, the 'prefix'
set in the utility (if any) will be used by default.

    >>> print serializeModel(model) # doctest: +NORMALIZE_WHITESPACE
    <model xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:ui="http://namespaces.acme.com/ui" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema ui:layout="horizontal">
        <field name="title" type="zope.schema.TextLine" ui:widget="largetype">
          <title>Title</title>
        </field>
        <field name="description" type="zope.schema.Text">
          <description>A short summary</description>
          <min_length>10</min_length>
          <required>False</required>
          <title>Description</title>
        </field>
      </schema>
    </model>
