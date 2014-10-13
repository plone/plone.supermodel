# -*- coding: utf-8 -*-
import plone.supermodel.exportimport
import zope.schema

# Field import/export handlers

BytesHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Bytes)
ASCIIHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.ASCII)
BytesLineHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.BytesLine)
ASCIILineHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.ASCIILine)
TextHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Text)
TextLineHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.TextLine)
BoolHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Bool)
IntHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Int)
FloatHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Float)
DecimalHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Decimal)
TupleHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Tuple)
ListHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.List)
SetHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Set)
FrozenSetHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.FrozenSet)
PasswordHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.Password)
DictHandler = plone.supermodel.exportimport.DictHandler(zope.schema.Dict)
DatetimeHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.Datetime)
DateHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Date)
SourceTextHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.SourceText)
URIHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.URI)
IdHandler = plone.supermodel.exportimport.BaseHandler(zope.schema.Id)
DottedNameHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.DottedName)
InterfaceFieldHandler = plone.supermodel.exportimport.BaseHandler(
    zope.schema.InterfaceField)
ObjectHandler = plone.supermodel.exportimport.ObjectHandler(zope.schema.Object)
ChoiceHandler = plone.supermodel.exportimport.ChoiceHandler(zope.schema.Choice)
