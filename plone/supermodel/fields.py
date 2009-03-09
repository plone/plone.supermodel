from plone.supermodel.exportimport import BaseHandler
import zope.schema

# Field import/export handlers

BytesHandler = BaseHandler(zope.schema.Bytes, element_name="field")
ASCIIHandler = BaseHandler(zope.schema.ASCII, element_name="field")
BytesLineHandler = BaseHandler(zope.schema.BytesLine, element_name="field")
ASCIILineHandler = BaseHandler(zope.schema.ASCIILine, element_name="field")
TextHandler = BaseHandler(zope.schema.Text, element_name="field")
TextLineHandler = BaseHandler(zope.schema.TextLine, element_name="field")
BoolHandler = BaseHandler(zope.schema.Bool, element_name="field")
IntHandler = BaseHandler(zope.schema.Int, element_name="field")
FloatHandler = BaseHandler(zope.schema.Float, element_name="field")
TupleHandler = BaseHandler(zope.schema.Tuple, element_name="field")
ListHandler = BaseHandler(zope.schema.List, element_name="field")
SetHandler = BaseHandler(zope.schema.Set, element_name="field")
FrozenSetHandler = BaseHandler(zope.schema.FrozenSet, element_name="field")
PasswordHandler = BaseHandler(zope.schema.Password, element_name="field")
DictHandler = BaseHandler(zope.schema.Dict, element_name="field")
DatetimeHandler = BaseHandler(zope.schema.Datetime, element_name="field")
DateHandler = BaseHandler(zope.schema.Date, element_name="field")
SourceTextHandler = BaseHandler(zope.schema.SourceText, element_name="field")
ObjectHandler = BaseHandler(zope.schema.Object, element_name="field")
URIHandler = BaseHandler(zope.schema.URI, element_name="field")
IdHandler = BaseHandler(zope.schema.Id, element_name="field")
DottedNameHandler = BaseHandler(zope.schema.DottedName, element_name="field")
InterfaceFieldHandler = BaseHandler(zope.schema.InterfaceField, element_name="field")