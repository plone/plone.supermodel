# -*- coding: utf-8 -*-
import zope.interface
import zope.schema
import zope.schema.interfaces


class IDottedName(zope.interface.Interface):
    """A dotted name identifier.
    """

    min_dots = zope.schema.Int(title=u"Minimum number of dots", min=0, required=False)
    max_dots = zope.schema.Int(title=u"Maximum number of dots", min=0, required=False)

# XXX: zope.schema omits these two interface declarations. We add them here
# so that our parsers work.

zope.interface.classImplements(zope.schema.Bool, zope.schema.interfaces.IFromUnicode)
zope.interface.classImplements(zope.schema.DottedName, IDottedName)
