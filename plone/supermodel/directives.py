import os.path
import sys

from zope.component import adapts
from zope.interface import implements
from zope.interface.interface import TAGGED_DATA

from plone.supermodel import loadFile
from plone.supermodel.interfaces import ISchema
from plone.supermodel.interfaces import ISchemaPlugin
from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY, FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.supermodel.utils import syncSchema

class DirectiveClass(type):
    """A Directive is used to apply tagged values to a Schema
    """

    def __init__(self, name, bases, attrs):
        attrs.setdefault('finalize', None)
        super(DirectiveClass, self).__init__(name, bases, attrs)
        self.__instance = super(DirectiveClass, self).__call__()

    def __call__(self, *args, **kw):
        instance = self.__instance
        frame = sys._getframe(1)
        tags = frame.f_locals.setdefault(TAGGED_DATA, {})
        value = instance.factory(*args, **kw)
        instance.store(tags, value)

Directive = DirectiveClass('Directive', (), dict(__module__='plone.supermodel.directives'))


class load(Directive):
    """Directive used to specify the XML model file
    """

    def store(self, tags, value):
        tags[FILENAME_KEY] = value["filename"]
        tags[SCHEMA_NAME_KEY] = value["schema"]

    def factory(self, filename, schema=u""):
        return dict(filename=filename, schema=schema)


class SupermodelSchemaPlugin(object):
    adapts(ISchema)
    implements(ISchemaPlugin)

    order = -1000

    def __init__(self, interface):
        self.interface = interface

    def __call__(self):
        interface = self.interface
        filename = interface.queryTaggedValue(FILENAME_KEY, None)
        if filename is None:
            return
        schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")

        moduleName = interface.__module__
        module = sys.modules[moduleName]

        directory = moduleName

        if hasattr(module, '__path__'):
            directory = module.__path__[0]
        elif "." in moduleName:
            parentModuleName, _ = moduleName.rsplit('.', 1)
            directory = sys.modules[parentModuleName].__path__[0]

        directory = os.path.abspath(directory)
        # Let / act as path separator on all platforms
        filename = filename.replace('/', os.path.sep)
        filename = os.path.abspath(os.path.join(directory, filename))

        model = loadFile(filename)
        if schema not in model.schemata:
            raise ValueError(
                    u"Schema '%s' specified for interface %s does not exist in %s." % 
                        (schema, interface.__identifier__, filename,)) 

        syncSchema(model.schemata[schema], interface, overwrite=False)


class MetadataListStorage(object):
    """Store a list value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def __init__(self, key):
        self.key = key

    def __call__(self, tags, value):
        tags.setdefault(self.key, []).extend(value)


class fieldset(Directive):
    """Directive used to create fieldsets
    """
    store = MetadataListStorage(FIELDSETS_KEY)

    def factory(self, name, label=None, description=None, fields=None, **kw):
        fieldset=Fieldset(name, label=label, description=description, fields=fields)
        for (key,value) in kw.items():
            setattr(fieldset, key, value)
        return [fieldset]


class CheckerPlugin(object):
    key = None

    def __init__(self, schema):
        self.schema = schema
        self.value = schema.queryTaggedValue(self.key, None)

    def fieldsNames(self):
        if self.value is None:
            return []
        return self.value.keys()

    def __call__(self):
        schema = self.schema
        for fieldName in self.fieldNames():
            if fieldName not in schema:
                raise ValueError(
                    u"The directive %s applied to interface %s "
                    u"refers to unknown field name %s" % (self.key, schema.__identifier__, fieldName)
                    )


class FieldsetCheckerPlugin(CheckerPlugin):
    adapts(ISchema)
    implements(ISchemaPlugin)

    key = FIELDSETS_KEY

    def fieldNames(self):
        if self.value is None:
            return
        for fieldset in self.value:
            for fieldName in fieldset.fields:
                yield fieldName
