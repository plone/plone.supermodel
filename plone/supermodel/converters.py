# -*- coding: utf-8 -*-
from plone.supermodel.interfaces import IToUnicode
from plone.supermodel.utils import fieldTypecast
from zope.component import adapter
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import IInterfaceField
from zope.schema.interfaces import IObject

import datetime
import six
import time


# Defaults

@implementer(IFromUnicode)
@adapter(IField)
class DefaultFromUnicode(object):

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        return fieldTypecast(self.context, value)


@implementer(IToUnicode)
@adapter(IField)
class DefaultToUnicode(object):

    def __init__(self, context):
        self.context = context

    def toUnicode(self, value):

        return six.text_type(value)


# Date/time fields

@implementer(IFromUnicode)
@adapter(IDate)
class DateFromUnicode(object):

    format = "%Y-%m-%d"

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        t = time.strptime(value, self.format)
        d = datetime.date(*t[:3])
        self.context.validate(d)
        return d


@implementer(IFromUnicode)
@adapter(IDatetime)
class DatetimeFromUnicode(object):

    format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        t = time.strptime(value[:19], self.format)
        d = datetime.datetime(*t[:7])
        self.context.validate(d)
        return d


# Interface fields

@implementer(IFromUnicode)
@adapter(IInterfaceField)
class InterfaceFieldFromUnicode(object):

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        iface = resolve(value)
        self.context.validate(iface)
        return iface


@implementer(IToUnicode)
@adapter(IInterfaceField)
class InterfaceFieldToUnicode(object):

    def __init__(self, context):
        self.context = context

    def toUnicode(self, value):
        return six.text_type(value.__identifier__)


# Object fields - we can read, but not write, as there is no way to know
# the original dotted name of an object in memory (and the id() is not
# particularly useful)


@implementer(IFromUnicode)
@adapter(IObject)
class ObjectFromUnicode(object):

    def __init__(self, context):
        self.context = context

    def fromUnicode(self, value):
        obj = resolve(value)
        self.context.validate(obj)
        return obj


@implementer(IToUnicode)
@adapter(IBytes)
class BytesToUnicode(object):

    def __init__(self, context):
        self.context = context

    def toUnicode(self, value):
        return six.text_type(value)
