=============================
plone.supermodel: SchemaClass
=============================

    >>> from plone.supermodel.model import Schema, SchemaClass
    >>> from plone.supermodel import interfaces, PY3
    >>> from zope.interface import Interface, implementer
    >>> from zope.component import adapts, provideAdapter

Schema plugins are registered as named adapters. They may optionally contain
an order attribute, which defaults to 0.

    >>> adapter_calls = []
    >>> @implementer(interfaces.ISchemaPlugin)
    ... class TestPlugin(object):
    ...     adapts(interfaces.ISchema)
    ...     order = 1
    ...     def __init__(self, schema):
    ...         self.schema = schema
    ...     def __call__(self):
    ...         adapter_calls.append(
    ...             (self.__class__.__name__,self.schema.__name__))
    ...
    >>> provideAdapter(TestPlugin, name=u"plone.supermodel.tests.TestPlugin")

Schema plugins are executed at schema declaration.

    >>> class IA(Schema):
    ...     pass
    >>> adapter_calls == [('TestPlugin', 'IA')]
    True

Any class descending from Schema becomes an instance of SchemaClass and has any
schema plugins called.

Except, there is a known issue. Until
https://bugs.launchpad.net/zope.interface/+bug/791218 is resolved, this
inheritance only works if the *first* base class is an instance of SchemaClass.
So below I've commented out the output that we hope for once that issue is
resolved. 
Somehow the issue got solved when using python 3, so we need to check python
version to get expected results here.

    >>> class ISomeInterface(Interface):
    ...     pass

    >>> adapter_calls = []
    >>> class IB(ISomeInterface, IA):
    ...     pass
    >>> adapter_calls == ([('TestPlugin', 'IB')] if PY3 else [])
    True

    >>> adapter_calls = []
    >>> class IC(IB):
    ...     pass
    >>> adapter_calls == ([('TestPlugin', 'IC')] if PY3 else [])
    True

To support the registration of schema plugins in ZCML, plugins are
additionally executed at zope.configuration time with a ZCML order of 1000. To
simulate this we will define another adapter and call the configuration action
directly.

    >>> adapter_calls = []
    >>> class TestPlugin2(TestPlugin):
    ...     order = 0

    >>> provideAdapter(TestPlugin2, name=u"plone.supermodel.tests.TestPlugin2")
    >>> from plone.supermodel.model import finalizeSchemas
    >>> finalizeSchemas(IA)
    >>> adapter_calls == (
    ...     [('TestPlugin2', 'IA'),
    ...         ('TestPlugin', 'IA'),
    ...         ('TestPlugin2', 'IB'),
    ...         ('TestPlugin', 'IB'),
    ...         ('TestPlugin2', 'IC'),
    ...         ('TestPlugin', 'IC'),
    ...        ] if PY3 else [
    ...         ('TestPlugin2', 'IA'),
    ...        ('TestPlugin', 'IA')])
    True
    >>> adapter_calls = []