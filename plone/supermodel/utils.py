import os.path
import sys
import re

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