=============================
plone.supermodel: SchemaClass
=============================

    >>> from plone.supermodel.model import Schema, SchemaClass
    >>> from plone.supermodel import interfaces
    >>> from zope.interface import Interface, implements
    >>> from zope.component import adapts, provideAdapter

Schema plugins are registered as named adapters. They may optionally contain
an order attribute, which defaults to 0.

    >>> class TestPlugin(object):
    ...     adapts(interfaces.ISchema)
    ...     implements(interfaces.ISchemaPlugin)
    ...     order = 1
    ...     def __init__(self, schema):
    ...         self.schema = schema
    ...     def __call__(self):
    ...         print("%s: %r" % (self.__class__.__name__, self.schema))
    ...
    >>> provideAdapter(TestPlugin, name=u"plone.supermodel.tests.TestPlugin")

Schema plugins are executed at schema declaration.

    >>> class IA(Schema):
    ...     pass
    TestPlugin: <SchemaClass __builtin__.IA>

Any class descending from Schema becomes an instance of SchemaClass and has any
schema plugins called.

Except, there is a known issue. Until
https://bugs.launchpad.net/zope.interface/+bug/791218 is resolved, this
inheritance only works if the *first* base class is an instance of SchemaClass.
So below I've commented out the output that we hope for once that issue is
resolved.

    >>> class ISomeInterface(Interface):
    ...     pass

    >>> class IB(ISomeInterface, IA):
    ...     pass

#    TestPlugin: <SchemaClass __builtin__.IB>

    >>> class IC(IB):
    ...     pass

#    TestPlugin: <SchemaClass __builtin__.IC>

To support the registration of schema plugins in ZCML, plugins are
additionally executed at zope.configuration time with a ZCML order of 1000. To
simulate this we will define another adapter and call the configuration action
directly.

    >>> class TestPlugin2(TestPlugin):
    ...     order = 0

    >>> provideAdapter(TestPlugin2, name=u"plone.supermodel.tests.TestPlugin2")
    >>> from plone.supermodel.model import finalizeSchemas
    >>> finalizeSchemas(IA)
    TestPlugin2: <SchemaClass __builtin__.IA>
    TestPlugin: <SchemaClass __builtin__.IA>

#    TestPlugin2: <SchemaClass __builtin__.IB>
#    TestPlugin: <SchemaClass __builtin__.IB>
#    TestPlugin2: <SchemaClass __builtin__.IC>
#    TestPlugin: <SchemaClass __builtin__.IC>
