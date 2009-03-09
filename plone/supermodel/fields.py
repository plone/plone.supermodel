from plone.supermodel.exportimport import BaseHandler
import zope.schema

# Field import/export handlers

BytesHandler = BaseHandler(zope.schema.Bytes)
ASCIIHandler = BaseHandler(zope.schema.ASCII)
BytesLineHandler = BaseHandler(zope.schema.BytesLine)
ASCIILineHandler = BaseHandler(zope.schema.ASCIILine)
TextHandler = BaseHandler(zope.schema.Text)
TextLineHandler = BaseHandler(zope.schema.TextLine)
BoolHandler = BaseHandler(zope.schema.Bool)
IntHandler = BaseHandler(zope.schema.Int)
FloatHandler = BaseHandler(zope.schema.Float)
TupleHandler = BaseHandler(zope.schema.Tuple)
ListHandler = BaseHandler(zope.schema.List)
SetHandler = BaseHandler(zope.schema.Set)
FrozenSetHandler = BaseHandler(zope.schema.FrozenSet)
PasswordHandler = BaseHandler(zope.schema.Password)
DictHandler = BaseHandler(zope.schema.Dict)
DatetimeHandler = BaseHandler(zope.schema.Datetime)
DateHandler = BaseHandler(zope.schema.Date)
SourceTextHandler = BaseHandler(zope.schema.SourceText)
ObjectHandler = BaseHandler(zope.schema.Object)
URIHandler = BaseHandler(zope.schema.URI)
IdHandler = BaseHandler(zope.schema.Id)
DottedNameHandler = BaseHandler(zope.schema.DottedName)
InterfaceFieldHandler = BaseHandler(zope.schema.InterfaceField)