================================
plone.supermodel: field handlers
================================

This file tests the various field handlers. Please note the following known
limitations:

  * `Timedelta` fields are not supported.
  * When an `Object` field is serialised, the `default` and `missing_value`
    attributes are ignored.
  * `Choice` fields can only be serialised if were created from a simple list
    of values (the `values` constructor parameter) or use a named vocabulary.
    It is possible to import a Choice field with a source that is either an
    `ISource` or an `IContextSourceBinder`, but only if such instances can be
    imported from a given dotted name. Finally, `Choice` fields imported with
    a `values` list as a vocabulary or with the `default` or `missing_value`
    set, are assumed store a unicode string.

First, let's wire up the package.

    >>> configuration = """\
    ... <configure
    ...      xmlns="http://namespaces.zope.org/zope"
    ...      i18n_domain="plone.behavior.tests">
    ...
    ...     <include package="zope.component" file="meta.zcml" />
    ...
    ...     <include package="plone.supermodel" />
    ...
    ... </configure>
    ... """

    >>> from plone.supermodel import PY3
    >>> if PY3:
    ...     from io import StringIO
    ... else:
    ...     from StringIO import StringIO
    >>> from plone.supermodel import b
    >>> from zope.configuration import xmlconfig
    >>> xmlconfig.xmlconfig(StringIO(configuration))

Then, let's test each field in turn.

    >>> from zope.component import getUtility
    >>> from zope import schema

    >>> from plone.supermodel.interfaces import IFieldExportImportHandler
    >>> from plone.supermodel.interfaces import IFieldNameExtractor
    >>> from plone.supermodel.utils import prettyXML

    >>> import datetime
    >>> import plone.supermodel.tests

    >>> from lxml import etree

Bytes
-----

    >>> field = schema.Bytes(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=b('abc'), missing_value='m',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Bytes">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Bytes'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default.decode('latin-1')
    u'abc'
    >>> reciprocal.missing_value.decode('latin-1')
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

BytesLine
---------

    >>> field = schema.BytesLine(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=b('abc'), missing_value='m',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.BytesLine">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.BytesLine'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default.decode('latin-1')
    u'abc'
    >>> reciprocal.missing_value.decode('latin-1')
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

ASCII
-----

    >>> field = schema.ASCII(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='abc', missing_value='m',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.ASCII">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.ASCII'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'abc'
    >>> reciprocal.missing_value
    'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

ASCIILine
---------

    >>> field = schema.ASCIILine(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='abc', missing_value='m',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.ASCIILine">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.ASCIILine'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'abc'
    >>> reciprocal.missing_value
    'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

Text
----

    >>> field = schema.Text(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=u'abc', missing_value=u'm',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Text">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.Text'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    u'abc'
    >>> reciprocal.missing_value
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

TextLine
--------

    >>> field = schema.TextLine(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=u'abc', missing_value=u'm',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.TextLine">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.TextLine'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    u'abc'
    >>> reciprocal.missing_value
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

SourceText
----------

    >>> field = schema.SourceText(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=u'abc', missing_value=u'm',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.SourceText">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.SourceText'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    u'abc'
    >>> reciprocal.missing_value
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

URI
---

    >>> field = schema.URI(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='http://plone.org', missing_value='m',
    ...     min_length=2, max_length=100)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.URI">
      <default>http://plone.org</default>
      <description>Test desc</description>
      <max_length>100</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.URI'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'http://plone.org'
    >>> reciprocal.missing_value
    'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    100
    >>> reciprocal._init_field
    False

Id
--

    >>> field = schema.Id(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='a.b.c', missing_value='m',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Id">
      <default>a.b.c</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Id'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'a.b.c'
    >>> reciprocal.missing_value
    'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

DottedName
-----------

    >>> field = schema.DottedName(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='a.b.c', missing_value='m',
    ...     min_length=2, max_length=10, min_dots=2, max_dots=4)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.DottedName">
      <default>a.b.c</default>
      <description>Test desc</description>
      <max_dots>4</max_dots>
      <max_length>10</max_length>
      <min_dots>2</min_dots>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.DottedName'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'a.b.c'
    >>> reciprocal.missing_value
    'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.min_dots
    2
    >>> reciprocal.max_dots
    4
    >>> reciprocal._init_field
    False

Password
--------

    >>> field = schema.Password(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=u'abc', missing_value=u'm',
    ...     min_length=2, max_length=10)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Password">
      <default>abc</default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value>m</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.Password'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    u'abc'
    >>> reciprocal.missing_value
    u'm'
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal._init_field
    False

Bool
----

    >>> field = schema.Bool(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=False, missing_value=True)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Bool">
      <default>False</default>
      <description>Test desc</description>
      <missing_value>True</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.Bool'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    False
    >>> reciprocal.missing_value
    True
    >>> reciprocal._init_field
    False

Int
---

    >>> field = schema.Int(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=12, missing_value=-1,
    ...     min=1, max=99)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Int">
      <default>12</default>
      <description>Test desc</description>
      <max>99</max>
      <min>1</min>
      <missing_value>-1</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    12
    >>> reciprocal.missing_value
    -1
    >>> reciprocal.min
    1
    >>> reciprocal.max
    99
    >>> reciprocal._init_field
    False

Float
-----

    >>> field = schema.Float(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=12.1, missing_value=-1.0,
    ...     min=1.123, max=99.5)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Float">
      <default>12.1</default>
      <description>Test desc</description>
      <max>99.5</max>
      <min>1.123</min>
      <missing_value>-1.0</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Float'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    12.1
    >>> reciprocal.missing_value
    -1.0
    >>> reciprocal.min
    1.123
    >>> reciprocal.max
    99.5
    >>> reciprocal._init_field
    False

Decimal
-------

    >>> import decimal
    >>> field = schema.Decimal(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=decimal.Decimal("12.1"), missing_value=decimal.Decimal("-1.0"),
    ...     min=decimal.Decimal("1.123"), max=decimal.Decimal("99.5"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Decimal">
      <default>12.1</default>
      <description>Test desc</description>
      <max>99.5</max>
      <min>1.123</min>
      <missing_value>-1.0</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Decimal'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default == decimal.Decimal('12.1')
    True
    >>> reciprocal.missing_value == decimal.Decimal('-1.0')
    True
    >>> reciprocal.min == decimal.Decimal('1.123')
    True
    >>> reciprocal.max == decimal.Decimal('99.5')
    True
    >>> reciprocal._init_field
    False

Date
----

    >>> field = schema.Date(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=datetime.date(2001,1,2), missing_value=datetime.date(2000,1,1),
    ...     min=datetime.date(2000,10,12), max=datetime.date(2099,12,31))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Date">
      <default>2001-01-02</default>
      <description>Test desc</description>
      <max>2099-12-31</max>
      <min>2000-10-12</min>
      <missing_value>2000-01-01</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Date'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    datetime.date(2001, 1, 2)
    >>> reciprocal.missing_value
    datetime.date(2000, 1, 1)
    >>> reciprocal.min
    datetime.date(2000, 10, 12)
    >>> reciprocal.max
    datetime.date(2099, 12, 31)
    >>> reciprocal._init_field
    False

Datetime
---------

    >>> field = schema.Datetime(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=datetime.datetime(2001,1,2,1,2,3), missing_value=datetime.datetime(2000,1,1,2,3,4),
    ...     min=datetime.datetime(2000,10,12,0,0,2), max=datetime.datetime(2099,12,31,1,2,2))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Datetime">
      <default>2001-01-02 01:02:03</default>
      <description>Test desc</description>
      <max>2099-12-31 01:02:02</max>
      <min>2000-10-12 00:00:02</min>
      <missing_value>2000-01-01 02:03:04</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Datetime'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    datetime.datetime(2001, 1, 2, 1, 2, 3, 1)
    >>> reciprocal.missing_value
    datetime.datetime(2000, 1, 1, 2, 3, 4, 5)
    >>> reciprocal.min
    datetime.datetime(2000, 10, 12, 0, 0, 2, 3)
    >>> reciprocal.max
    datetime.datetime(2099, 12, 31, 1, 2, 2, 3)
    >>> reciprocal._init_field
    False

InterfaceField
---------------

    >>> field = schema.InterfaceField(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=plone.supermodel.tests.IDummy,
    ...     missing_value=plone.supermodel.tests.IDummy)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.InterfaceField">
      <default>plone.supermodel.tests.IDummy</default>
      <description>Test desc</description>
      <missing_value>plone.supermodel.tests.IDummy</missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.InterfaceField'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    <InterfaceClass plone.supermodel.tests.IDummy>
    >>> reciprocal.missing_value
    <InterfaceClass plone.supermodel.tests.IDummy>
    >>> reciprocal._init_field
    False

Tuple
-----

    >>> field = schema.Tuple(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=(1,2), missing_value=(),
    ...     min_length=2, max_length=10,
    ...     value_type=schema.Int(title=u"Val"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Tuple">
      <default>
        <element>1</element>
        <element>2</element>
      </default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value/>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <value_type type="zope.schema.Int">
        <title>Val</title>
      </value_type>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Tuple'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    (1, 2)
    >>> reciprocal.missing_value
    ()
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.value_type.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.value_type.title
    u'Val'
    >>> reciprocal._init_field
    False

List
----

    >>> field = schema.List(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=[1,2], missing_value=[],
    ...     min_length=2, max_length=10,
    ...     value_type=schema.Int(title=u"Val"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.List">
      <default>
        <element>1</element>
        <element>2</element>
      </default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value/>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <value_type type="zope.schema.Int">
        <title>Val</title>
      </value_type>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.List'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    [1, 2]
    >>> reciprocal.missing_value
    []
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.value_type.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.value_type.title
    u'Val'
    >>> reciprocal._init_field
    False

Set
---

    >>> field = schema.Set(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=set((1,2)), missing_value=set(),
    ...     min_length=2, max_length=10,
    ...     value_type=schema.Int(title=u"Val"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Set">
      <default>
        <element>1</element>
        <element>2</element>
      </default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value/>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <value_type type="zope.schema.Int">
        <title>Val</title>
      </value_type>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Set'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> isinstance(reciprocal.default, set)
    True
    >>> [i for i in reciprocal.default]
    [1, 2]
    >>> isinstance(reciprocal.missing_value, set)
    True
    >>> len(reciprocal.missing_value)
    0
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.value_type.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.value_type.title
    u'Val'
    >>> reciprocal._init_field
    False

FrozenSet
---------

    >>> field = schema.FrozenSet(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=frozenset((1,2)), missing_value=frozenset(),
    ...     min_length=2, max_length=10,
    ...     value_type=schema.Int(title=u"Val"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.FrozenSet">
      <default>
        <element>1</element>
        <element>2</element>
      </default>
      <description>Test desc</description>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value/>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <value_type type="zope.schema.Int">
        <title>Val</title>
      </value_type>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.FrozenSet'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> isinstance(reciprocal.default, frozenset)
    True
    >>> [i for i in reciprocal.default]
    [1, 2]
    >>> isinstance(reciprocal.missing_value, frozenset)
    True
    >>> len(reciprocal.missing_value)
    0
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.value_type.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.value_type.title
    u'Val'
    >>> reciprocal._init_field
    False

Dict
----

    >>> field = schema.Dict(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default={'a':1, 'b':2}, missing_value={},
    ...     min_length=2, max_length=10,
    ...     key_type=schema.ASCIILine(title=u"Key"),
    ...     value_type=schema.Int(title=u"Val"))
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Dict">
      <default>
        <element key="a">1</element>
        <element key="b">2</element>
      </default>
      <description>Test desc</description>
      <key_type type="zope.schema.ASCIILine">
        <title>Key</title>
      </key_type>
      <max_length>10</max_length>
      <min_length>2</min_length>
      <missing_value/>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <value_type type="zope.schema.Int">
        <title>Val</title>
      </value_type>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Dict'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default['a']
    1
    >>> reciprocal.default['b']
    2
    >>> sorted(reciprocal.default.keys())
    ['a', 'b']
    >>> reciprocal.missing_value
    {}
    >>> reciprocal.min_length
    2
    >>> reciprocal.max_length
    10
    >>> reciprocal.key_type.__class__
    <class 'zope.schema._field.ASCIILine'>
    >>> reciprocal.key_type.title
    u'Key'
    >>> reciprocal.value_type.__class__
    <class 'zope.schema._bootstrapfields.Int'>
    >>> reciprocal.value_type.title
    u'Val'
    >>> reciprocal._init_field
    False

Object
------

Note: when an object field is written, the 'default' and 'missing_value'
fields will be omitted, as there is no way to write these reliably.

    >>> dummy1 = plone.supermodel.tests.Dummy()
    >>> dummy2 = plone.supermodel.tests.Dummy()

    >>> field = schema.Object(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default=dummy1, missing_value=dummy2,
    ...     schema=plone.supermodel.tests.IDummy)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType) #doctest: +ELLIPSIS
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Object">
      <description>Test desc</description>
      <readonly>True</readonly>
      <required>False</required>
      <schema>plone.supermodel.tests.IDummy</schema>
      <title>Test</title>
    </field>

However, we support reading an object dotted name for an
object field that references a particular dotted name.

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.Object">
    ...   <default>plone.supermodel.tests.dummy1</default>
    ...   <description>Test desc</description>
    ...   <missing_value/>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <schema>plone.supermodel.tests.IDummy</schema>
    ...   <title>Test</title>
    ... </field>
    ... """)

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Object'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default is plone.supermodel.tests.dummy1
    True
    >>> reciprocal.missing_value is None
    True
    >>> reciprocal._init_field
    False

Choice
------

The choice field supports several different modes: a named vocabulary, a list
of values, a source object, or a source context binder object. However,
plone.supermodel only supports exporting named vocabularies or lists of
unicode string values. In addition, it is possible to import (but not export)
a source or context source binder, provided it can be imported from a
dotted name.

1. Named vocabularies

These can be both exported and imported.

    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='a', missing_value='', vocabulary=u'dummy.vocab')

    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Choice">
      <default>a</default>
      <description>Test desc</description>
      <missing_value></missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <vocabulary>dummy.vocab</vocabulary>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Choice'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default # note - value is always unicode
    'a'
    >>> reciprocal.missing_value # note - value is always unicode
    ''
    >>> reciprocal.vocabulary is None
    True
    >>> reciprocal.vocabularyName
    u'dummy.vocab'
    >>> reciprocal._init_field
    False

2. Values vocabularies

These can be both imported and exported, but note that the value is always
a unicode string when importing.

    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='a', missing_value='', values=['a', 'b', 'c'])

    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Choice">
      <default>a</default>
      <description>Test desc</description>
      <missing_value></missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <values>
        <element>a</element>
        <element>b</element>
        <element>c</element>
      </values>
    </field>

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Choice'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'a'
    >>> reciprocal.missing_value
    ''
    >>> [t.value for t in reciprocal.vocabulary]
    [u'a', u'b', u'c']
    >>> reciprocal.vocabularyName is None
    True

There was a bug when the XML namespace was specified explicitly; let's make
sure it hasn't regressed.

    >>> from plone.supermodel.interfaces import XML_NAMESPACE
    >>> element.set('xmlns', XML_NAMESPACE)
    >>> element = etree.parse(StringIO(prettyXML(element).decode('latin-1'))).getroot()
    >>> reciprocal = handler.read(element)
    >>> [t.value for t in reciprocal.vocabulary]
    [u'a', u'b', u'c']

Also, make sure we can handle terms with unicode values (as long as their
tokens are the utf8-encoded values).

    >>> from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
    >>> vocab = SimpleVocabulary([
    ...     SimpleTerm(token='a', value=u'a', title=u'a'),
    ...     SimpleTerm(token=r'\xe7', value=u'\xe7', title=u'\xe7'), # c with cedilla
    ...     ])
    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     default='a', missing_value='', vocabulary=vocab)

    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Choice">
      <default>a</default>
      <description>Test desc</description>
      <missing_value></missing_value>
      <readonly>True</readonly>
      <required>False</required>
      <title>Test</title>
      <values>
        <element>a</element>
        <element>&#231;</element>
      </values>
    </field>

    >>> reciprocal = handler.read(element)
    >>> [t.value for t in reciprocal.vocabulary]
    [u'a', u'\xe7']


Additionally, it is possible for Choice fields with a values vocabulary
whose terms contain values distinct from term titles for each
respective term.  This is accomplished by using the 'key' attribute
of each contained 'element' of the values element (this is consistent
with how Dict fields are output, only for Choices, order is guaranteed).

    >>> from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
    >>> vocab = SimpleVocabulary([
    ...     SimpleTerm(value=u'a', title=u'A'),
    ...     SimpleTerm(value=u'b', title=u'B'),
    ...     ])
    >>> field = schema.Choice(
    ...     __name__="dummy",
    ...     title=u"Test",
    ...     vocabulary=vocab,
    ...     )
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType)
    >>> print(prettyXML(element).decode('latin-1'))
    <field name="dummy" type="zope.schema.Choice">
      <title>Test</title>
      <values>
        <element key="a">A</element>
        <element key="b">B</element>
      </values>
    </field>

3. Sources and source binders

We cannot export choice fields with a source or context source binder:

    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     vocabulary=plone.supermodel.tests.dummy_vocabulary_instance)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    NotImplementedError: Cannot export a vocabulary that is not based on a simple list of values

    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     source=plone.supermodel.tests.dummy_vocabulary_instance)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    NotImplementedError: Cannot export a vocabulary that is not based on a simple list of values

    >>> field = schema.Choice(__name__="dummy", title=u"Test",
    ...     description=u"Test desc", required=False, readonly=True,
    ...     source=plone.supermodel.tests.dummy_binder)
    >>> fieldType = IFieldNameExtractor(field)()
    >>> handler = getUtility(IFieldExportImportHandler, name=fieldType)
    >>> element = handler.write(field, 'dummy', fieldType) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    NotImplementedError: Choice fields with vocabularies not based on a simple list of values or a named vocabulary cannot be exported

However, we can import a choice field with a source, provided that source can
be specified via an importable dotted name.

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.Choice">
    ...   <default>a</default>
    ...   <description>Test desc</description>
    ...   <missing_value/>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ...   <source>plone.supermodel.tests.dummy_binder</source>
    ... </field>
    ... """)

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Choice'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'a'
    >>> reciprocal.vocabulary is plone.supermodel.tests.dummy_binder
    True
    >>> reciprocal.vocabularyName is None
    True

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.Choice">
    ...   <default>a</default>
    ...   <description>Test desc</description>
    ...   <missing_value/>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ...   <source>plone.supermodel.tests.dummy_vocabulary_instance</source>
    ... </field>
    ... """)
    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._field.Choice'>
    >>> reciprocal.__name__
    'dummy'
    >>> reciprocal.title
    u'Test'
    >>> reciprocal.description
    u'Test desc'
    >>> reciprocal.required
    False
    >>> reciprocal.readonly
    True
    >>> reciprocal.default
    'a'
    >>> reciprocal.vocabulary is plone.supermodel.tests.dummy_vocabulary_instance
    True
    >>> reciprocal.vocabularyName is None
    True
    >>> reciprocal._init_field
    False

defaultFactory usage
--------------------

Fields may specify defaultFactory attributes as dotted interfaces.
defaultFactory callables should provide either
zope.schema.interfaces.IContextAwareDefaultFactory or
plone.supermodel.interfaces.IDefaultFactory.

Note that zope.schema allows callables without any marker
interface. Our requirements are an extra validation measure.

Try specifying a defaultFactory attribute::

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.TextLine">
    ...   <defaultFactory>plone.supermodel.tests.dummy_defaultFactory</defaultFactory>
    ...   <description>Test desc</description>
    ...   <max_length>10</max_length>
    ...   <min_length>2</min_length>
    ...   <missing_value>m</missing_value>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ... </field>
    ... """)

Import it::
    >>> handler = getUtility(IFieldExportImportHandler, name='zope.schema.TextLine')

Sanity checks::

    >>> reciprocal = handler.read(element)
    >>> reciprocal.__class__
    <class 'zope.schema._bootstrapfields.TextLine'>
    >>> reciprocal._init_field
    False

And, look for the specified defaultFactory::
    >>> reciprocal.defaultFactory == plone.supermodel.tests.dummy_defaultFactory
    True

Let's try it with a callable that provides IContextAwareDefaultFactory::
    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.TextLine">
    ...   <defaultFactory>plone.supermodel.tests.dummy_defaultCAFactory</defaultFactory>
    ...   <description>Test desc</description>
    ...   <max_length>10</max_length>
    ...   <min_length>2</min_length>
    ...   <missing_value>m</missing_value>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ... </field>
    ... """)

    >>> handler = getUtility(IFieldExportImportHandler, name='zope.schema.TextLine')
    >>> reciprocal = handler.read(element)
    >>> reciprocal.defaultFactory == plone.supermodel.tests.dummy_defaultCAFactory
    True
    >>> reciprocal._init_field
    False

And, check to make sure that we can't use a callable that doesn't have one
of our marker interfaces::

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.TextLine">
    ...   <defaultFactory>plone.supermodel.tests.dummy_defaultBadFactory</defaultFactory>
    ...   <description>Test desc</description>
    ...   <max_length>10</max_length>
    ...   <min_length>2</min_length>
    ...   <missing_value>m</missing_value>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ... </field>
    ... """)

    >>> handler = getUtility(IFieldExportImportHandler, name='zope.schema.TextLine')
    >>> reciprocal = handler.read(element)
    Traceback (most recent call last):
    ...
    ImportError: defaultFactory must provide zope.schema.interfaces.IContextAwareDefaultFactory or plone.supermodel.IDefaultFactory

A non-existent callable should also raise an error::

    >>> element = etree.XML("""\
    ... <field name="dummy" type="zope.schema.TextLine">
    ...   <defaultFactory>plone.supermodel.tests.nonExistentFactory</defaultFactory>
    ...   <description>Test desc</description>
    ...   <max_length>10</max_length>
    ...   <min_length>2</min_length>
    ...   <missing_value>m</missing_value>
    ...   <readonly>True</readonly>
    ...   <required>False</required>
    ...   <title>Test</title>
    ... </field>
    ... """)

    >>> handler = getUtility(IFieldExportImportHandler, name='zope.schema.TextLine')
    >>> reciprocal = handler.read(element)
    Traceback (most recent call last):
    ...
    ImportError: No module named nonExistentFactory
