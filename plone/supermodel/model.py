import logging
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

try:
    from plone.rfc822.interfaces import IPrimaryField
except ImportError:
    pass
else:
    zope.deferredimport.defineFrom('plone.supermodel.directives', 'primary')

logger = logging.getLogger('plone.supermodel')


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

    def __init__(self, name, bases=(), attrs=None, __doc__=None,
                 __module__=None):
        InterfaceClass.__init__(self, name, bases, attrs, __doc__, __module__)
        self._SchemaClass_finalize()

    def _SchemaClass_finalize(self):
        adapters = [(getattr(adapter, 'order', 0), name, adapter)
                    for name, adapter in getAdapters((self,), ISchemaPlugin)]
        adapters.sort()
        for order, name, adapter in adapters:
            adapter()

Schema = SchemaClass("Schema", (Interface,), __module__='plone.supermodel.model')


def finalizeSchemas(parent=Schema):
    """Configuration action called after plone.supermodel is configured.
    """
    if not isinstance(parent, SchemaClass):
        raise TypeError('Only instances of plone.supermodel.model.SchemaClass can be finalized.')
    def walk(schema):
        yield  schema
        for child in schema.dependents.keys():
            for s in walk(child):
                yield s
    schemas = set(walk(parent))
    for schema in schemas:
        if hasattr(schema, '_SchemaClass_finalize'):
            schema._SchemaClass_finalize()
        elif isinstance(schema, InterfaceClass):
            logger.warn('%s is not an instance of SchemaClass. '
                'This can happen if the first base class of a schema is not a '
                'SchemaClass. See https://bugs.launchpad.net/zope.interface/+bug/791218'
                % ('%s.%s' % (schema.__module__, schema.__name__)))
