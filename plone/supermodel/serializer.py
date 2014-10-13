# -*- coding: utf-8 -*-
from lxml import etree
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.interfaces import I18N_NAMESPACE
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IFieldMetadataHandler
from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.interfaces import ISchemaMetadataHandler
from plone.supermodel.interfaces import XML_NAMESPACE
from plone.supermodel.model import Schema
from plone.supermodel.utils import ns
from plone.supermodel.utils import prettyXML
from plone.supermodel.utils import sortedFields
from zope.component import adapter
from zope.component import getUtilitiesFor
from zope.component import queryUtility
from zope.interface import implementer
from zope.schema.interfaces import IField


@implementer(IFieldNameExtractor)
@adapter(IField)
class DefaultFieldNameExtractor(object):
    """Extract a name
    """

    def __init__(self, context):
        self.context = context

    def __call__(self):
        field_module = self.context.__class__.__module__

        # workaround for the fact that some fields are defined in one
        # module, but commonly used from zope.schema.*

        if field_module.startswith('zope.schema._bootstrapfields'):
            field_module = field_module.replace("._bootstrapfields", "")
        elif field_module.startswith('zope.schema._field'):
            field_module = field_module.replace("._field", "")

        return "%s.%s" % (field_module, self.context.__class__.__name__)


# Algorithm


def serialize(model):

    handlers = {}
    schema_metadata_handlers = tuple(getUtilitiesFor(ISchemaMetadataHandler))
    field_metadata_handlers = tuple(getUtilitiesFor(IFieldMetadataHandler))

    nsmap = {'i18n': I18N_NAMESPACE}
    for name, handler in schema_metadata_handlers + field_metadata_handlers:
        namespace, prefix = handler.namespace, handler.prefix
        if namespace is not None and prefix is not None:
            nsmap[prefix] = namespace

    xml = etree.Element('model', nsmap=nsmap)
    xml.set('xmlns', XML_NAMESPACE)

    def writeField(field, parentElement):
        name_extractor = IFieldNameExtractor(field)
        fieldType = name_extractor()
        handler = handlers.get(fieldType, None)
        if handler is None:
            handler = handlers[fieldType] = queryUtility(IFieldExportImportHandler, name=fieldType)
            if handler is None:
                raise ValueError("Field type %s specified for field %s is not supported" % (fieldType, fieldName))
        fieldElement = handler.write(field, fieldName, fieldType)
        if fieldElement is not None:
            parentElement.append(fieldElement)

            for handler_name, metadata_handler in field_metadata_handlers:
                metadata_handler.write(fieldElement, schema, field)

    for schemaName, schema in model.schemata.items():

        fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])

        fieldset_fields = set()
        for fieldset in fieldsets:
            fieldset_fields.update(fieldset.fields)

        non_fieldset_fields = [name for name, field in sortedFields(schema)
                                if name not in fieldset_fields]

        schema_element = etree.Element('schema')
        if schemaName:
            schema_element.set('name', schemaName)

        bases = [b.__identifier__ for b in schema.__bases__ if b is not Schema]
        if bases:
            schema_element.set('based-on', ' '.join(bases))

        for invariant in schema.queryTaggedValue('invariants', []):
            invariant_element = etree.Element('invariant')
            invariant_element.text = "%s.%s" % (invariant.__module__, invariant.__name__)
            schema_element.append(invariant_element)

        for fieldName in non_fieldset_fields:
            field = schema[fieldName]
            writeField(field, schema_element)

        for fieldset in fieldsets:

            fieldset_element = etree.Element('fieldset')
            fieldset_element.set('name', fieldset.__name__)
            if fieldset.label:
                fieldset_element.set('label', fieldset.label)
            if fieldset.description:
                fieldset_element.set('description', fieldset.description)

            for fieldName in fieldset.fields:
                field = schema[fieldName]
                writeField(field, fieldset_element)

            schema_element.append(fieldset_element)

        for handler_name, metadata_handler in schema_metadata_handlers:
            metadata_handler.write(schema_element, schema)

        xml.append(schema_element)

    # handle i18n
    i18n_domain = xml.get(ns('domain', prefix=I18N_NAMESPACE))
    for node in xml.xpath('//*[@i18n:translate]', namespaces=nsmap):
        domain = node.get(ns('domain', prefix=I18N_NAMESPACE), i18n_domain)
        if i18n_domain is None:
            i18n_domain = domain
        if domain == i18n_domain:
            node.attrib.pop(ns('domain', prefix=I18N_NAMESPACE))
    if i18n_domain:
        xml.set(ns('domain', prefix=I18N_NAMESPACE), i18n_domain)

    return prettyXML(xml)


__all__ = ('serialize', )
