# -*- coding: utf-8 -*-
from lxml import etree
from plone.supermodel.debug import parseinfo
from plone.supermodel.interfaces import I18N_NAMESPACE
from plone.supermodel.interfaces import IToUnicode
from plone.supermodel.interfaces import XML_NAMESPACE
from zope.component import getUtility
from zope.i18nmessageid import Message
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode

import os.path
import re
import six
import sys


try:
    from collections import OrderedDict
except ImportError:
    from zope.schema.vocabulary import OrderedDict  # <py27


_marker = object()
noNS_re = re.compile('^{\S+}')


def ns(name, prefix=XML_NAMESPACE):
    """Return the element or attribute name with the given prefix
    """

    return u'{%s}%s' % (prefix, name)


def noNS(name):
    """Return the tag with no namespace
    """
    return noNS_re.sub('', name)


def indent(node, level=0):

    INDENT_SIZE = 2
    node_indent = level * (' ' * INDENT_SIZE)
    child_indent = (level + 1) * (' ' * INDENT_SIZE)

    # node has childen
    if len(node):

        # add indent before first child node
        if not node.text or not node.text.strip():
            node.text = '\n' + child_indent

        # let each child indent itself
        last_idx = len(node) - 1
        for idx, child in enumerate(node):
            indent(child, level + 1)

            # add a tail for the next child node...
            if idx != last_idx:
                if not child.tail or not child.tail.strip():
                    child.tail = '\n' + child_indent
            # ... or for the closing element of this node
            else:
                if not child.tail or not child.tail.strip():
                    child.tail = '\n' + node_indent


def prettyXML(tree):
    indent(tree)
    xml = etree.tostring(tree)
    if six.PY2:
        return xml
    return xml.decode()


def fieldTypecast(field, value):
    typecast = getattr(field, '_type', None)
    if typecast is not None:
        if not isinstance(typecast, (list, tuple)):
            typecast = (typecast, )
        for tc in reversed(typecast):
            if callable(tc):
                try:
                    value = tc(value)
                    break
                except:
                    pass
    return value


def elementToValue(field, element, default=_marker):
    """Read the contents of an element that is assumed to represent a value
    allowable by the given field.

    If converter is given, it should be an IToUnicode instance.

    If not, the field will be adapted to this interface to obtain a converter.
    """
    value = default
    if IDict.providedBy(field):
        key_converter = IFromUnicode(field.key_type)
        value = OrderedDict()
        for child in element.iterchildren(tag=etree.Element):
            if noNS(child.tag.lower()) != 'element':
                continue
            parseinfo.stack.append(child)

            key_text = child.attrib.get('key')
            if key_text is None:
                k = None
            else:
                k = key_converter.fromUnicode(six.text_type(key_text))

            value[k] = elementToValue(field.value_type, child)
            parseinfo.stack.pop()
        value = fieldTypecast(field, value)

    elif ICollection.providedBy(field):
        value = []
        for child in element.iterchildren(tag=etree.Element):
            if noNS(child.tag.lower()) != 'element':
                continue
            parseinfo.stack.append(child)
            v = elementToValue(field.value_type, child)
            value.append(v)
            parseinfo.stack.pop()
        value = fieldTypecast(field, value)

    elif IChoice.providedBy(field):
        vocabulary = None
        try:
            vcf = getUtility(IVocabularyFactory, field.vocabularyName)
            vocabulary = vcf(None)
        except:
            pass

        if vocabulary and hasattr(vocabulary, 'by_value'):
            try:
                field._type = type(list(vocabulary.by_value.keys())[0])
            except:
                pass

        value = fieldTypecast(field, element.text)

    # Unicode
    else:
        text = element.text
        if text is None:
            value = field.missing_value
        else:
            converter = IFromUnicode(field)
            if isinstance(text, six.binary_type):
                text = text.decode()
            else:
                text = six.text_type(text)
            value = converter.fromUnicode(text)

        # handle i18n
        if isinstance(value, six.string_types) and \
                parseinfo.i18n_domain is not None:
            translate_attr = ns('translate', I18N_NAMESPACE)
            domain_attr = ns('domain', I18N_NAMESPACE)
            msgid = element.attrib.get(translate_attr)
            domain = element.attrib.get(domain_attr, parseinfo.i18n_domain)
            if msgid:
                value = Message(msgid, domain=domain, default=value)
            elif translate_attr in element.attrib:
                value = Message(value, domain=domain)

    return value


def valueToElement(field, value, name=None, force=False):
    """Create and return an element that describes the given value, which is
    assumed to be valid for the given field.

    If name is given, this will be used as the new element name. Otherwise,
    the field's __name__ attribute is consulted.

    If force is True, the value will always be written. Otherwise, it is only
    written if it is not equal to field.missing_value.
    """

    if name is None:
        name = field.__name__

    child = etree.Element(name)

    if value is not None and (force or value != field.missing_value):

        if IDict.providedBy(field):
            key_converter = IToUnicode(field.key_type)
            for k, v in sorted(value.items()):
                list_element = valueToElement(
                    field.value_type, v, 'element', force)
                list_element.attrib['key'] = key_converter.toUnicode(k)
                child.append(list_element)

        elif ICollection.providedBy(field):
            for v in value:
                list_element = valueToElement(
                    field.value_type, v, 'element', force)
                child.append(list_element)

        else:
            converter = IToUnicode(field)
            child.text = converter.toUnicode(value)

            # handle i18n
            if isinstance(value, Message):
                child.set(ns('domain', I18N_NAMESPACE), value.domain)
                if not value.default:
                    child.set(ns('translate', I18N_NAMESPACE), '')
                else:
                    child.set(ns('translate', I18N_NAMESPACE), child.text)
                    child.text = converter.toUnicode(value.default)

    return child


def relativeToCallingPackage(filename, callingFrame=2):
    """If the filename is not an absolute path, make it into an absolute path
    by calculating the relative path from the module that called the function
    at 'callingFrame' steps down the stack.
    """
    if os.path.isabs(filename):
        return filename
    else:
        name = sys._getframe(callingFrame).f_globals['__name__']
        module = sys.modules[name]
        if hasattr(module, '__path__'):
            directory = module.__path__[0]
        elif "." in name:
            parent_module = name[:name.rfind('.')]
            directory = sys.modules[parent_module].__path__[0]
        else:
            directory = name
        directory = os.path.abspath(directory)
        return os.path.abspath(os.path.join(directory, filename))


def sortedFields(schema):
    """Like getFieldsInOrder, but does not include fields from bases
    """
    fields = []
    for name in schema.names(all=False):
        field = schema[name]
        if IField.providedBy(field):
            fields.append((name, field, ))
    fields.sort(key=lambda item: item[1].order)
    return fields


def mergedTaggedValueDict(schema, name):
    """Look up the tagged value 'name' in schema and all its bases, assuming
    that the value under 'name' is a dict. Return a dict that consists of
    all dict items, with those from more-specific interfaces overriding those
    from more-general ones.
    """
    tv = {}
    for iface in reversed(schema.__iro__):
        tv.update(iface.queryTaggedValue(name, {}))
    return tv


def mergedTaggedValueList(schema, name):
    """Look up the tagged value 'name' in schema and all its bases, assuming
    that the value under 'name' is a list. Return a list that consists of
    all elements from all interfaces and base interfaces, with values from
    more-specific interfaces appearing at the end of the list.
    """
    tv = []
    for iface in reversed(schema.__iro__):
        tv.extend(iface.queryTaggedValue(name, []))
    return tv


def syncSchema(source, dest, overwrite=False, sync_bases=False):
    """Copy attributes and tagged values from the source to the destination.
    If overwrite is False, do not overwrite attributes or tagged values that
    already exist or delete ones that don't exist in source.
    """

    if overwrite:
        to_delete = set()

        # Delete fields in dest, but not in source
        for name, field in sortedFields(dest):
            if name not in source:
                to_delete.add(name)

        for name in to_delete:
            # delattr(dest, name)
            del dest._InterfaceClass__attrs[name]
            if hasattr(dest, '_v_attrs'):
                del dest._v_attrs[name]

    # Add fields that are in source, but not in dest

    for name, field in sortedFields(source):
        if overwrite or name not in dest or dest[name].interface is not dest:

            clone = field.__class__.__new__(field.__class__)
            clone.__dict__.update(field.__dict__)
            clone.interface = dest
            clone.__name__ = name

            # copy any marker interfaces
            directlyProvides(clone, *directlyProvidedBy(field))

            # setattr(dest, name, clone)
            dest._InterfaceClass__attrs[name] = clone
            if hasattr(dest, '_v_attrs'):
                dest._v_attrs[name] = clone

    # Copy tagged values
    dest_tags = set(dest.getTaggedValueTags())
    for tag in source.getTaggedValueTags():
        if overwrite or tag not in dest_tags:
            value = source.getTaggedValue(tag)
            dest.setTaggedValue(tag, value)

    # Sync bases
    if sync_bases:
        bases = list(source.__bases__)
        if not overwrite:
            for base in dest.__bases__:
                if base not in bases:
                    bases.append(base)
        dest.__bases__ = tuple(bases)
