import time, datetime

from zope.interface import implements
from zope.component import adapts

from zope.schema.interfaces import IField, IFromUnicode
from zope.schema.interfaces import IDate, IDatetime, IInterfaceField, IObject

from zope.dottedname.resolve import resolve

from plone.supermodel.interfaces import IToUnicode
from plone.supermodel.utils import fieldTypecast

# Defaults

class DefaultFromUnicode(object):
    implements(IFromUnicode)
    adapts(IField)
    
    def __init__(self, context):
        self.context = context
        
    def fromUnicode(self, value):
        return fieldTypecast(self.context, value)

class DefaultToUnicode(object):
    implements(IToUnicode)
    adapts(IField)
    
    def __init__(self, context):
        self.context = context
        
    def toUnicode(self, value):
        return unicode(value)

# Date/time fields

class DateFromUnicode(object):
    implements(IFromUnicode)
    adapts(IDate)
    
    format = "%Y-%m-%d"
    
    def __init__(self, context):
        self.context = context
        
    def fromUnicode(self, value):
        t = time.strptime(value, self.format)
        d = datetime.date(*t[:3])
        self.context.validate(d)
        return d

class DatetimeFromUnicode(object):
    implements(IFromUnicode)
    adapts(IDatetime)
    
    format = "%Y-%m-%d %H:%M:%S"
    
    def __init__(self, context):
        self.context = context
        
    def fromUnicode(self, value):
        t = time.strptime(value[:19], self.format)
        d = datetime.datetime(*t[:7])
        self.context.validate(d)
        return d

# Interface fields

class InterfaceFieldFromUnicode(object):
    implements(IFromUnicode)
    adapts(IInterfaceField)
    
    def __init__(self, context):
        self.context = context
        
    def fromUnicode(self, value):
        iface = resolve(value)
        self.context.validate(iface)
        return iface
        
class InterfaceFieldToUnicode(object):
    implements(IToUnicode)
    adapts(IInterfaceField)
    
    def __init__(self, context):
        self.context = context
        
    def toUnicode(self, value):
        return unicode(value.__identifier__)

# Object fields - we can read, but not write, as there is no way to know
# the original dotted name of an object in memory (and the id() is not
# particularly useful)

class ObjectFromUnicode(object):
    implements(IFromUnicode)
    adapts(IObject)
    
    def __init__(self, context):
        self.context = context
        
    def fromUnicode(self, value):
        obj = resolve(value)
        self.context.validate(obj)
        return obj