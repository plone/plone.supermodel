# -*- coding: utf-8 -*-
from lxml import etree
from plone.supermodel.debug import parseinfo
from plone.supermodel.interfaces import IDefaultFactory
from plone.supermodel.interfaces import IFieldExportImportHandler
from plone.supermodel.interfaces import IFieldNameExtractor
from plone.supermodel.utils import elementToValue
from plone.supermodel.utils import noNS
from plone.supermodel.utils import valueToElement
from zope.component import queryUtility
from zope.interface import implementedBy
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IField
from zope.schema.interfaces import IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import six
import zope.schema


try:
    from collections import OrderedDict
except ImportError:
    from zope.schema.vocabulary import OrderedDict  # <py27


class OrderedDictField(zope.schema.Dict):
    _type = OrderedDict


@implementer(IFieldExportImportHandler)
class BaseHandler(object):
    """Base class for import/export handlers.

    The read_field method is called to read one field of the known subtype
    from an XML element.

    The write_field method is called to write one field to a particular
    element.
    """

    # Elements that we will not read/write. 'r' means skip when reading;
    # 'w' means skip when writing; 'rw' means skip always.

    filteredAttributes = {'order': 'rw', 'unique': 'rw', 'defaultFactory': 'w'}

    # Elements that are of the same type as the field itself
    fieldTypeAttributes = ('min', 'max', 'default', )

    # Elements that are of the same type as the field itself, but are
    # otherwise not validated
    nonValidatedfieldTypeAttributes = ('missing_value', )

    # Attributes that contain another field. Unfortunately,
    fieldInstanceAttributes = ('key_type', 'value_type', )

    # Fields that are always written

    forcedFields = frozenset(['default', 'missing_value'])

    def __init__(self, klass):
        self.klass = klass
        self.fieldAttributes = {}

        # Build a dict of the parameters supported by this field type.
        # Each parameter is itself a field, which can be used to convert
        # text input to an appropriate object.
        for schema in implementedBy(self.klass).flattened():
            self.fieldAttributes.update(zope.schema.getFields(schema))

        self.fieldAttributes['defaultFactory'] = zope.schema.Object(
            __name__='defaultFactory',
            title=u"defaultFactory",
            schema=Interface
        )

    def _constructField(self, attributes):
        return self.klass(**attributes)

    def read(self, element):
        """Read a field from the element and return a new instance
        """
        attributes = {}
        deferred = {}
        deferred_nonvalidated = {}

        for attribute_element in element.iterchildren(tag=etree.Element):
            parseinfo.stack.append(attribute_element)
            attribute_name = noNS(attribute_element.tag)

            if 'r' in self.filteredAttributes.get(attribute_name, ''):
                continue

            attributeField = self.fieldAttributes.get(attribute_name, None)
            if attributeField is not None:

                if attribute_name in self.fieldTypeAttributes:
                    deferred[attribute_name] = attribute_element

                elif attribute_name in self.nonValidatedfieldTypeAttributes:
                    deferred_nonvalidated[attribute_name] = attribute_element

                elif attribute_name in self.fieldInstanceAttributes:

                    attributeField_type = attribute_element.get('type')
                    handler = queryUtility(
                        IFieldExportImportHandler,
                        name=attributeField_type
                    )

                    if handler is None:
                        raise NotImplementedError(
                            u"Type %s used for %s not supported" %
                            (attributeField_type, attribute_name)
                        )

                    attributes[attribute_name] = handler.read(
                        attribute_element
                    )

                else:
                    attributes[attribute_name] = self.readAttribute(
                        attribute_element,
                        attributeField
                    )
            parseinfo.stack.pop()

        name = element.get('name')
        if name is not None:
            name = str(name)
            attributes['__name__'] = name

        field_instance = self._constructField(attributes)

        # some fields can't validate fully until they're finished setting up
        field_instance._init_field = True

        # Handle those elements that can only be set up once the field is
        # constructed, in the preferred order.
        for attribute_name in self.fieldTypeAttributes:
            if attribute_name in deferred:
                attribute_element = deferred[attribute_name]
                parseinfo.stack.append(attribute_element)
                value = self.readAttribute(attribute_element, field_instance)
                setattr(field_instance, attribute_name, value)
                parseinfo.stack.pop()

        for attribute_name in self.nonValidatedfieldTypeAttributes:
            if attribute_name in deferred_nonvalidated:

                # this is pretty nasty: we need the field's fromUnicode(),
                # but this always validates. The missing_value field may by
                # definition be invalid. Therefore, we need to fake it.

                clone = self.klass.__new__(self.klass)
                clone.__dict__.update(field_instance.__dict__)
                clone.__dict__['validate'] = lambda value: True

                attribute_element = deferred_nonvalidated[attribute_name]
                parseinfo.stack.append(attribute_element)
                value = self.readAttribute(attribute_element, clone)
                setattr(field_instance, attribute_name, value)
                parseinfo.stack.pop()

        field_instance._init_field = False

        if field_instance.defaultFactory is not None:
            # we want to add some additional requirements for defaultFactory.
            # zope.schema will be happy with any function, we'd like to
            # restrict to those that provide IContextAwareDefaultFactory
            # or IDefaultFactory
            if not (
                IContextAwareDefaultFactory.providedBy(
                    field_instance.defaultFactory
                ) or
                IDefaultFactory.providedBy(field_instance.defaultFactory)
            ):
                raise ImportError(
                    u"defaultFactory must provide "
                    u"zope.schema.interfaces.IContextAwareDefaultFactory "
                    u"or plone.supermodel.IDefaultFactory"
                )

        return field_instance

    def write(self, field, name, type, elementName='field'):
        """Create and return a new element representing the given field
        """

        element = etree.Element(elementName)

        if name:
            element.set('name', name)

        element.set('type', type)

        for attribute_name in sorted(self.fieldAttributes.keys()):
            attributeField = self.fieldAttributes[attribute_name]
            if 'w' in self.filteredAttributes.get(attribute_name, ''):
                continue
            child = self.writeAttribute(attributeField, field)
            if child is not None:
                element.append(child)

        return element

    # Field attribute read and write

    def readAttribute(self, element, attributeField):
        """Read a single attribute from the given element. The attribute is of
        a type described by the given Field object.
        """
        return elementToValue(attributeField, element)

    def writeAttribute(self, attributeField, field, ignoreDefault=True):
        """Create and return a element that describes the given attribute
        field on the given field
        """

        elementName = attributeField.__name__
        attributeField = attributeField.bind(field)
        value = attributeField.get(field)

        force = (elementName in self.forcedFields)

        if ignoreDefault and value == attributeField.default:
            return None

        # The value points to another field. Recurse.
        if IField.providedBy(value):
            value_fieldType = IFieldNameExtractor(value)()
            handler = queryUtility(
                IFieldExportImportHandler,
                name=value_fieldType
            )
            if handler is None:
                return None
            return handler.write(
                value, name=None,
                type=value_fieldType,
                elementName=elementName
            )

        # For 'default', 'missing_value' etc, we want to validate against
        # the imported field type itself, not the field type of the attribute
        if elementName in self.fieldTypeAttributes or \
                elementName in self.nonValidatedfieldTypeAttributes:
            attributeField = field

        return valueToElement(
            attributeField,
            value,
            name=elementName,
            force=force
        )


class DictHandler(BaseHandler):
    """Special handling for the Dict field, which uses Attribute instead of
    Field to describe its key_type and value_type.
    """

    def __init__(self, klass):
        super(DictHandler, self).__init__(klass)
        self.fieldAttributes['key_type'] = zope.schema.Field(
            __name__='key_type',
            title=u"Key type"
        )
        self.fieldAttributes['value_type'] = zope.schema.Field(
            __name__='value_type',
            title=u"Value type"
        )


class ObjectHandler(BaseHandler):
    """Special handling for the Object field, which uses Attribute instead of
    Field to describe its schema
    """

    # We can't serialise the value or missing_value of an object field.

    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update({'default': 'w', 'missing_value': 'w'})

    def __init__(self, klass):
        super(ObjectHandler, self).__init__(klass)

        # This is not correctly set in the interface
        self.fieldAttributes['schema'] = zope.schema.InterfaceField(
            __name__='schema'
        )


class ChoiceHandler(BaseHandler):
    """Special handling for the Choice field
    """

    filteredAttributes = BaseHandler.filteredAttributes.copy()
    filteredAttributes.update(
        {'vocabulary': 'w',
         'values': 'w',
         'source': 'w',
         'vocabularyName': 'rw'
         }
    )

    def __init__(self, klass):
        super(ChoiceHandler, self).__init__(klass)

        # Special options for the constructor. These are not automatically
        # written.

        self.fieldAttributes['vocabulary'] = zope.schema.TextLine(
            __name__='vocabulary',
            title=u"Named vocabulary"
        )

        self.fieldAttributes['values'] = zope.schema.List(
            __name__='values',
            title=u"Values",
            value_type=zope.schema.Text(title=u"Value")
        )

        # XXX: We can't be more specific about the schema, since the field
        # supports both ISource and IContextSourceBinder. However, the
        # initialiser will validate.
        self.fieldAttributes['source'] = zope.schema.Object(
            __name__='source',
            title=u"Source",
            schema=Interface
        )

    def readAttribute(self, element, attributeField):
        if (
            etree.QName(element).localname == 'values' and
            any([child.get('key') for child in element])
        ):
            attributeField = OrderedDictField(
                key_type=zope.schema.TextLine(),
                value_type=zope.schema.TextLine(),
            )
        return elementToValue(attributeField, element)

    def _constructField(self, attributes):
        if 'values' in attributes:
            if isinstance(attributes['values'], OrderedDict):
                attributes['values'] = attributes['values'].items()
            terms = []
            for value in attributes['values']:
                title = (value or u'')
                if isinstance(value, tuple):
                    value, title = value
                encoded = (value or '').encode('unicode_escape')
                if value != encoded:
                    value = value or u''
                    term = SimpleTerm(
                        token=encoded,
                        value=value,
                        title=title
                    )
                else:
                    term = SimpleTerm(value=value, title=title)
                terms.append(term)
            attributes['vocabulary'] = SimpleVocabulary(terms)
            del attributes['values']
        return super(ChoiceHandler, self)._constructField(attributes)

    def write(self, field, name, type, elementName='field'):

        element = super(ChoiceHandler, self).write(
            field,
            name,
            type,
            elementName
        )

        # write vocabulary or values list

        # Named vocabulary
        if field.vocabularyName is not None and field.vocabulary is None:
            attributeField = self.fieldAttributes['vocabulary']
            child = valueToElement(
                attributeField,
                field.vocabularyName,
                name='vocabulary',
                force=True
            )
            element.append(child)

        # Listed vocabulary - attempt to convert to a simple list of values
        elif (
            field.vocabularyName is None and
            IVocabularyTokenized.providedBy(field.vocabulary)
        ):
            value = []
            for term in field.vocabulary:
                if (
                    isinstance(term.value, six.integer_types)
                    or (
                        isinstance(term.value, six.string_types)
                        and six.b(term.token) == term.value.encode('unicode_escape')
                    )
                ):
                    if term.title and term.title != term.value:
                        value.append((term.value, term.title))
                    else:
                        value.append(term.value)
                else:
                    raise NotImplementedError(
                        u"Cannot export a vocabulary that is not "
                        u"based on a simple list of values"
                    )

            attributeField = self.fieldAttributes['values']
            if any(map(lambda v: isinstance(v, tuple), value)):
                def _pair(v):
                    return v if len(v) == 2 else (v[0],) * 2
                value = OrderedDict(map(_pair, value))
                attributeField = OrderedDictField(
                    key_type=zope.schema.TextLine(),
                    value_type=zope.schema.TextLine(),
                )
            child = valueToElement(
                attributeField,
                value,
                name='values',
                force=True
            )
            element.append(child)

        # Anything else is not allowed - we can't export ISource/IVocabulary or
        #  IContextSourceBinder objects.
        else:
            raise NotImplementedError(
                u"Choice fields with vocabularies not based on "
                u"a simple list of values or a named vocabulary "
                u"cannot be exported"
            )

        return element
