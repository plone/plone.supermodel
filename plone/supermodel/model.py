import sys
import weakref

import zope.deferredimport
from zope.component import getAdapters
from zope.interface import Interface
from zope.interface import implements
from zope.interface.interface import InterfaceClass

from plone.supermodel.interfaces import IModel
from plone.supermodel.interfaces import IFieldset
from plone.supermodel.interfaces import ISchema
from plone.supermodel.interfaces import ISchemaPlugin

zope.deferredimport.defineFrom('plone.supermodel.directives',
    'load',
    'fieldset',
)

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


class SchemaClass(InterfaceClass):
    implements(ISchema)

    _SchemaClass_configured = False
    _SchemaClass_deferred = weakref.WeakKeyDictionary()

    def __init__(self, name, bases=(), attrs=None, __doc__=None,
                 __module__=None):
        # Execute part of InterfaceClass.__init__ in correct frame.
        if attrs is None:
            attrs = {}

        if __module__ is None:
            __module__ = attrs.get('__module__')
            if isinstance(__module__, str):
                del attrs['__module__']
            else:
                try:
                    # Figure out what module defined the interface.
                    # This is how cPython figures out the module of
                    # a class, but of course it does it in C. :-/
                    __module__ = sys._getframe(1).f_globals['__name__']
                except (AttributeError, KeyError):
                    pass

        InterfaceClass.__init__(self, name, bases, attrs, __doc__, __module__)

        if SchemaClass._SchemaClass_configured:
            self._SchemaClass_finalize()
        else:
            SchemaClass._SchemaClass_deferred[self] = None

    def _SchemaClass_finalize(self):
        adapters = [(getattr(adapter, 'order', 0), name, adapter)
                    for name, adapter in getAdapters((self,), ISchemaPlugin)]
        adapters.sort()
        for order, name, adapter in adapters:
            adapter()

Schema = SchemaClass("Schema", (Interface,), __module__='plone.supermodel.model')


def finalizeSchemas():
    """Configuration action called after plone.supermodel is configured.
    """
    # As finalizeSchemas is called as a configurationa action this should be
    # thread safe.
    SchemaClass._SchemaClass_configured = True
    schemas = SchemaClass._SchemaClass_deferred.keys()
    SchemaClass._SchemaClass_deferred = None
    for schema in schemas:
        schema._SchemaClass_finalize()

try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    def cleanup():
        SchemaClass._SchemaClass_deferred = weakref.WeakKeyDictionary()
        SchemaClass._SchemaClass_configured = False
    addCleanUp(cleanup)
    del addCleanUp
    del cleanup
