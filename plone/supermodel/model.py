# -*- coding: utf-8 -*-
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.interfaces import IFieldset
from plone.supermodel.interfaces import IModel
from plone.supermodel.interfaces import ISchema
from plone.supermodel.interfaces import ISchemaPlugin
from zope.component import getAdapters
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interface import InterfaceClass

import logging
import zope.deferredimport


zope.deferredimport.defineFrom(
    'plone.supermodel.directives',
    'load',
    'fieldset',
)

try:
    from plone.rfc822.interfaces import IPrimaryField
    IPrimaryField  # PEP8
except ImportError:
    pass
else:
    zope.deferredimport.defineFrom('plone.supermodel.directives', 'primary')

logger = logging.getLogger('plone.supermodel')


@implementer(IFieldset)
class Fieldset(object):

    def __init__(
        self,
        __name__,
        label=None,
        description=None,
        fields=None,
        order=DEFAULT_ORDER
    ):
        self.__name__ = __name__
        self.label = label or __name__
        self.description = description
        self.order = order

        if fields:
            self.fields = fields
        else:
            self.fields = []

    def __repr__(self):
        return "<Fieldset '{0}' order {1:d} of {2}>".format(
            self.__name__,
            self.order,
            ', '.join(self.fields)
        )


@implementer(IModel)
class Model(object):

    def __init__(self, schemata=None):
        if schemata is None:
            schemata = {}
        self.schemata = schemata

    # Default schema

    @property
    def schema(self):
        return self.schemata.get(u"", None)


@implementer(ISchema)
class SchemaClass(InterfaceClass):

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

Schema = SchemaClass(
    'Schema',
    (Interface,),
    __module__='plone.supermodel.model'
)


def finalizeSchemas(parent=Schema):
    """Configuration action called after plone.supermodel is configured.
    """
    if not isinstance(parent, SchemaClass):
        raise TypeError(
            'Only instances of plone.supermodel.model.SchemaClass can be '
            'finalized.'
        )

    def walk(schema):
        yield schema
        if getattr(schema, 'dependents', None) is None:
            # This is just a temporary fix for a issue when running Plone-tests
            # with zope4 (http://jenkins.plone.org/view/PLIPs/job/plip-zope4/).
            # InterfaceClass
            # plone.dexterity.schema.generated.plone_0_LockableType
            # has zope.interface.adapter.VerifyingAdapterLookup as a
            # dependent which again has no dependents.
            # Maybe VerifyingAdapterLookup should not be here or it should have
            # dependents (a weakref.WeakKeyDictionary())
            # Maybe also related to the comment below which states that the
            # first base class of a schema must be a SchemaClass.
            logger.info(
                'This should not happen: "%s" has no dependents!' % schema)
        else:
            for child in schema.dependents.keys():
                for s in walk(child):
                    yield s
    schemas = set(walk(parent))
    for schema in schemas:
        if hasattr(schema, '_SchemaClass_finalize'):
            schema._SchemaClass_finalize()
        elif isinstance(schema, InterfaceClass):
            logger.warn(
                '{0}.{1} is not an instance of SchemaClass. '
                'This can happen if the first base class of a schema is not a '
                'SchemaClass. See '
                'https://bugs.launchpad.net/zope.interface/+bug/791218'.format(
                    schema.__module__,
                    schema.__name__
                )
            )
