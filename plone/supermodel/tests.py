from cStringIO import StringIO
from elementtree import ElementTree as etree
import doctest
import unittest

from zope.interface import Interface, implements, alsoProvides

import zope.component.testing

from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope import schema

from plone.supermodel import utils


class IBase(Interface):
    title = schema.TextLine(title=u"Title")
    description = schema.TextLine(title=u"Description")
    name = schema.TextLine(title=u"Name")

# Used in fields.txt


class IDummy(Interface):
    title = schema.TextLine(title=u"Title")


class Dummy(object):
    implements(IDummy)

    def __init__(self):
        self.title = u''


dummy1 = Dummy()


class Binder(object):
    implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        return SimpleVocabulary.fromValues(['a', 'd', 'f'])


dummy_binder = Binder()
dummy_vocabulary_instance = SimpleVocabulary.fromItems([(1, 'a'), (2, 'c')])


class TestUtils(unittest.TestCase):

    def test_syncSchema(self):

        class ISource(Interface):
            one = schema.TextLine(title=u"A") # order: 0
            two = schema.Int(title=u"B")      # order: 1

        class IDest(Interface):
            one = schema.TextLine(title=u"C") # order: 0
            three = schema.Int(title=u"D")    # order: 1

        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")

        utils.syncSchema(ISource, IDest)

        self.assertEquals(u"C", IDest['one'].title)

        self.assertEquals(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEquals(['two', 'one', 'three'], getFieldNamesInOrder(IDest))

        self.assertEquals("first tag", IDest.getTaggedValue("tag1"))
        self.assertEquals("tag two", IDest.getTaggedValue("tag2"))

    def test_syncSchema_overwrite(self):

        class ISource(Interface):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")

        class IDest(Interface):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")

        utils.syncSchema(ISource, IDest, overwrite=True)

        self.assertEquals(u"A", IDest['one'].title)

        self.assertEquals(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEquals(['one', 'two'], getFieldNamesInOrder(IDest))

        self.assertEquals("tag one", IDest.getTaggedValue("tag1"))
        self.assertEquals("tag two", IDest.getTaggedValue("tag2"))

    def test_syncSchema_overwrite_no_bases(self):

        class IBase(Interface):
            base = schema.TextLine(title=u"Base")

        class ISource(IBase):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")

        class IDest(Interface):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=False)

        self.assertEquals((Interface, ), IDest.__bases__)
        self.assertEquals(['two', 'one', 'three'], getFieldNamesInOrder(IDest))

    def test_syncSchema_overwrite_with_bases(self):

        class IBase(Interface):
            base = schema.TextLine(title=u"Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title=u"Foo")

        class ISource(IBase):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")

        class IDest(IOtherBase):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest, overwrite=True, sync_bases=True)

        self.assertEquals((IBase, ), IDest.__bases__)
        self.assertEquals(['base', 'one', 'two'], getFieldNamesInOrder(IDest))

    def test_syncSchema_overwrite_with_bases_and_no_overwrite(self):

        class IBase(Interface):
            base = schema.TextLine(title=u"Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title=u"Foo")

        class ISource(IBase):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")

        class IDest(IOtherBase):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=True)

        self.assertEquals((IBase, IOtherBase, ), IDest.__bases__)
        self.assertEquals(['base', 'foo', 'two', 'one', 'three'], getFieldNamesInOrder(IDest))

    def test_syncSchema_overwrite_with_bases_and_no_overwrite_with_old_bases(self):

        class IBase(Interface):
            base = schema.TextLine(title=u"Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title=u"Foo")

        class ISource(IBase):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")

        class IDest(IOtherBase, IBase):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=True)

        self.assertEquals((IBase, IOtherBase, ), IDest.__bases__)
        self.assertEquals(['base', 'foo', 'two', 'one', 'three'], getFieldNamesInOrder(IDest))

    def test_syncSchema_with_markers_no_overwrite(self):

        class IMarker(Interface):
            pass

        class ISource(Interface):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")
            four = schema.Text(title=u"C")

        alsoProvides(ISource['one'], IMarker)
        alsoProvides(ISource['four'], IMarker)

        class IDest(Interface):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest)

        self.failIf(IMarker.providedBy(IDest['one']))
        self.failIf(IMarker.providedBy(IDest['two']))
        self.failIf(IMarker.providedBy(IDest['three']))
        self.failUnless(IMarker.providedBy(IDest['four']))

    def test_syncSchema_with_markers_overwrite(self):

        class IMarker(Interface):
            pass

        class ISource(Interface):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")
            four = schema.Text(title=u"C")

        alsoProvides(ISource['one'], IMarker)
        alsoProvides(ISource['four'], IMarker)

        class IDest(Interface):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")

        utils.syncSchema(ISource, IDest, overwrite=True)

        self.failUnless(IMarker.providedBy(IDest['one']))
        self.failIf(IMarker.providedBy(IDest['two']))
        self.failUnless(IMarker.providedBy(IDest['four']))

    def test_syncSchema_always_overwrites_fields_from_bases(self):

        class IBase(Interface):
            one = schema.TextLine(title=u'A')

        class ISource(Interface):
            one = schema.TextLine(title=u'B')

        class IDest(IBase):
            pass

        utils.syncSchema(ISource, IDest, overwrite=False)

        self.assertTrue(IDest['one'].interface is IDest)

    def test_mergedTaggedValueList(self):

        class IBase1(Interface):
            pass

        class IBase2(Interface):
            pass

        class IBase3(Interface):
            pass

        class ISchema(IBase1, IBase2, IBase3):
            pass

        IBase1.setTaggedValue(u"foo", [1, 2])  # more specific than IBase2 and IBase3
        IBase3.setTaggedValue(u"foo", [3, 4])  # least specific of the bases
        ISchema.setTaggedValue(u"foo", [4, 5])  # most specific

        self.assertEquals([3, 4, 1, 2, 4, 5], utils.mergedTaggedValueList(ISchema, u"foo"))

    def test_mergedTaggedValueDict(self):

        class IBase1(Interface):
            pass

        class IBase2(Interface):
            pass

        class IBase3(Interface):
            pass

        class ISchema(IBase1, IBase2, IBase3):
            pass

        IBase1.setTaggedValue(u"foo", {1: 1, 2: 1})      # more specific than IBase2 and IBase3
        IBase3.setTaggedValue(u"foo", {3: 3, 2: 3, 4: 3}) # least specific of the bases
        ISchema.setTaggedValue(u"foo", {4: 4, 5: 4})      # most specific

        self.assertEquals({1: 1, 2: 1, 3: 3, 4: 4, 5: 4}, utils.mergedTaggedValueDict(ISchema, u"foo"))


class TestValueToElement(unittest.TestCase):

    def setUp(self):
        zope.component.testing.setUp()
        configuration = """\
        <configure
             xmlns="http://namespaces.zope.org/zope"
             i18n_domain="plone.supermodel.tests">

            <include package="zope.component" file="meta.zcml" />

            <include package="plone.supermodel" />

        </configure>
        """
        from zope.configuration import xmlconfig
        xmlconfig.xmlconfig(StringIO(configuration))


    tearDown = zope.component.testing.tearDown

    def _assertSerialized(self, field, value, expected):
        element = utils.valueToElement(field, value, 'value')
        sio = StringIO()
        etree.ElementTree(element).write(sio)
        self.assertEquals(sio.getvalue(), expected)
        unserialized = utils.elementToValue(field, element)
        self.assertEquals(value, unserialized)

    def test_lists(self):
        field = schema.List(value_type=schema.Int())
        value = []
        self._assertSerialized(field, value, '<value />')
        value = [1, 2]
        self._assertSerialized(field, value,
            '<value>'
            '<element>1</element>'
            '<element>2</element>'
            '</value>'
            )

    def test_nested_lists(self):
        field = schema.List(value_type=schema.List(value_type=schema.Int()))
        value = []
        self._assertSerialized(field, value, '<value />')
        value = [[1], [1, 2], []]
        self._assertSerialized(field, value,
            '<value>'
            '<element><element>1</element></element>'
            '<element><element>1</element><element>2</element></element>'
            '<element />'
            '</value>'
            )

    def test_dicts(self):
        field = schema.Dict(key_type=schema.Int(), value_type=schema.TextLine())
        value = {}
        self._assertSerialized(field, value, '<value />')
        value = {1: 'one', 2: 'two'}
        self._assertSerialized(field, value,
            '<value>'
            '<element key="1">one</element>'
            '<element key="2">two</element>'
            '</value>'
            )

    def test_nested_dicts(self):
        field = schema.Dict(key_type=schema.Int(),
            value_type=schema.Dict(
                key_type=schema.Int(),
                value_type=schema.TextLine(),
                ),
            )
        value = {}
        self._assertSerialized(field, value, '<value />')
        value = {1: {2: 'two'}, 3: {4: 'four', 5: 'five'}, 6: {}}
        self._assertSerialized(field, value,
            '<value>'
            '<element key="1"><element key="2">two</element></element>'
            '<element key="3"><element key="4">four</element><element key="5">five</element></element>'
            '<element key="6" />'
            '</value>'
            )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        unittest.makeSuite(TestValueToElement),
        doctest.DocFileSuite('schema.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.ELLIPSIS),
        doctest.DocFileSuite('fields.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown),
        doctest.DocFileSuite('schemaclass.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown),
        doctest.DocFileSuite('directives.txt',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown),
        ))


if __name__ == '__main__':
    unittest.main(default='test_suite')
