import os.path
import sys
import re

from elementtree import ElementTree

from zope.schema.interfaces import IField, IFromUnicode

from plone.supermodel.interfaces import XML_NAMESPACE, IToUnicode

_marker = object()
no_ns_re = re.compile('^{\S+}')

def ns(name, prefix=XML_NAMESPACE):
    """Return the element or attribute name with the given prefix
    """
    
    return u"{%s}%s" % (prefix, name)

def no_ns(name):
    """Return the tag with no namespace
    """
    return no_ns_re.sub('', name)

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def pretty_xml(tree):
    indent(tree)
    return ElementTree.tostring(tree)

def field_typecast(field, value):
    typecast = getattr(field, '_type', None)
    if typecast is not None:
        if not isinstance(typecast, (list, tuple)):
            typecast = (typecast,)
        for tc in reversed(typecast):
            if callable(tc):
                try:
                    value = tc(value)
                    break
                except:
                    pass
    return value

def element_to_value(field, element, default=_marker, converter=None, value_type=None):
    """Read the contents of an element that is assumed to represent a value
    allowable by the given field. If converter is given, it should
    be an IFromUnicode instance. If not, the field will be adapted to this
    interface to obtain a converter. If value_type is given, the value will
    be assumed to be an iterable, and the converter will operate on each
    value element.
    """
    
    value = default
        
    if value_type is not None:
        if converter is None:
            converter = IFromUnicode(value_type)
        value = []
        for child in element:
            if child.tag != 'element':
                continue
            value.append(converter.fromUnicode(unicode(child.text)))
        value = field_typecast(field, value)
    else:
        if converter is None:
            converter = IFromUnicode(field)
        value = converter.fromUnicode(unicode(element.text))
      
    return value
    
def value_to_element(field, value, converter=None, value_type=None):
    """Create and return an element that describes the given value, which is
    assumed to be valid for the given field. If converter is given, it should
    be an IToUnicode instance. If not, the field will be adapted to this
    interface to obtain a converter. If value_type is given, the value will
    be assumed to be an iterable, and the converter will operate on each
    value element.
    """
    
    child = ElementTree.Element(field.__name__)
    
    if value is not None:
        if value_type is not None:
            if converter is None:
                converter = IToUnicode(value_type)
            for e in value:
                list_element = ElementTree.Element('element')
                list_element.text = converter.toUnicode(e)
                child.append(list_element)
        else:
            if converter is None:
                converter = IToUnicode(field)
            child.text = converter.toUnicode(value)
        
    return child

def relative_to_calling_package(filename, calling_frame=2):
    """If the filename is not an absolute path, make it into an absolute path
    by calculating the relative path from the module that called the function
    at 'calling_frame' steps down the stack.
    """
    if os.path.isabs(filename):
        return filename
    else:
        name = sys._getframe(calling_frame).f_globals['__name__']
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

def sorted_fields(schema):
    """Like getFieldsInOrder, but does not include fields from bases
    """
    fields = []
    for name in schema.names(all=False):
        field = schema[name]
        if IField.providedBy(field):
            fields.append((name, field,))
    fields.sort(key=lambda item: item[1].order)
    return fields

def merged_tagged_value_dict(schema, name):
    """Look up the tagged value 'name' in schema and all its bases, assuming
    that the value under 'name' is a dict. Return a dict that consists of
    all dict items, with those from more-specific interfaces overriding those
    from more-general ones.
    """
    tv = {}
    for iface in reversed(schema.__iro__):
        tv.update(iface.queryTaggedValue(name, {}))
    return tv

def merged_tagged_value_list(schema, name):
    """Look up the tagged value 'name' in schema and all its bases, assuming
    that the value under 'name' is a list. Return a list that consists of
    all elements from all interfaces and base interfaces, with values from
    more-specific interfaces appearing at the end of the list.
    """
    tv = []
    for iface in reversed(schema.__iro__):
        tv.extend(iface.queryTaggedValue(name, []))
    return tv

def sync_schema(source, dest, overwrite=False, sync_bases=False):
    """Copy attributes and tagged values from the source to the destination.
    If overwrite is False, do not overwrite attributes or tagged values that
    already exist or delete ones that don't exist in source.
    """

    if overwrite:    
        to_delete = set()
    
        # Delete fields in dest, but not in source
        for name, field in sorted_fields(dest):
            if name not in source:
                to_delete.add(name)
    
        for name in to_delete:
            # delattr(dest, name)
            del dest._InterfaceClass__attrs[name]
            if hasattr(dest, '_v_attrs'):
                del dest._v_attrs[name]

    # Add fields that are in source, but not in dest
    
    for name, field in sorted_fields(source):
        if overwrite or name not in dest:
            
            clone = field.__class__.__new__(field.__class__)
            clone.__dict__.update(field.__dict__)
            clone.interface = dest
            clone.__name__ = name
            
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