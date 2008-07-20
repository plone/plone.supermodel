import os.path
import sys
import re

from zope.schema.interfaces import IField

from plone.supermodel.interfaces import XML_NAMESPACE

no_ns_re = re.compile('^{\S+}')

def ns(name, prefix=XML_NAMESPACE):
    """Return the element or attribute name with the given prefix
    """
    
    return u"{%s}%s" % (prefix, name)

def no_ns(name):
    """Return the tag with no namespace
    """
    return no_ns_re.sub('', name)

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