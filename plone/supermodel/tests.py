# -*- coding: utf-8 -*-
try:
    from io import StringIO, BytesIO
except ImportError:
    from cStringIO import StringIO
from lxml import etree
from plone.supermodel import b, PY3
from plone.supermodel import utils
from plone.supermodel.exportimport import ChoiceHandler
from plone.supermodel.interfaces import IDefaultFactory
from plone.supermodel.interfaces import IInvariant
from six.moves import cStringIO as StringIO
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import provider
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import doctest
import unittest
import re
import sys
import zope.component.testing


def configure():
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


class IBase(Interface):
    title = schema.TextLine(title=u"Title")
    description = schema.TextLine(title=u"Description")
    name = schema.TextLine(title=u"Name")

# Used in fields.txt


class IDummy(Interface):
    title = schema.TextLine(title=u"Title")


@implementer(IDummy)
class Dummy(object):

    def __init__(self):
        self.title = u''


dummy1 = Dummy()


@implementer(IContextSourceBinder)
class Binder(object):

    def __init__(self):
        pass

    def __call__(self, context):
        return SimpleVocabulary.fromValues(['a', 'd', 'f'])


dummy_binder = Binder()
dummy_vocabulary_instance = SimpleVocabulary.fromItems([(1, 'a'), (2, 'c')])


@provider(IContextAwareDefaultFactory)
def dummy_defaultCAFactory(context):
    return u'b'


@provider(IDefaultFactory)
def dummy_defaultFactory():
    return u'b'


def dummy_defaultBadFactory():
    return u'b'


@provider(IInvariant)
def dummy_invariant(data):
    raise Invalid(u"Yikes! Invalid")


@provider(IInvariant)
def dummy_invariant_prime(data):
    return None


def dummy_unmarkedInvariant(data):
    """ lacks IInvariant marker """
    return None


class TestUtils(unittest.TestCase):

    def test_syncSchema(self):

        class ISource(Interface):
            one = schema.TextLine(title=u"A")  # order: 0
            two = schema.Int(title=u"B")       # order: 1

        class IDest(Interface):
            one = schema.TextLine(title=u"C")  # order: 0
            three = schema.Int(title=u"D")     # order: 1

        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")

        utils.syncSchema(ISource, IDest)

        self.assertEqual(u"C", IDest['one'].title)

        self.assertEqual(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEqual(['two', 'one', 'three'], getFieldNamesInOrder(IDest))

        self.assertEqual("first tag", IDest.getTaggedValue("tag1"))
        self.assertEqual("tag two", IDest.getTaggedValue("tag2"))

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

        self.assertEqual(u"A", IDest['one'].title)

        self.assertEqual(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEqual(['one', 'two'], getFieldNamesInOrder(IDest))

        self.assertEqual("tag one", IDest.getTaggedValue("tag1"))
        self.assertEqual("tag two", IDest.getTaggedValue("tag2"))

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

        self.assertEqual((Interface, ), IDest.__bases__)
        self.assertEqual(['two', 'one', 'three'], getFieldNamesInOrder(IDest))

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

        self.assertEqual((IBase, ), IDest.__bases__)
        self.assertEqual(['base', 'one', 'two'], getFieldNamesInOrder(IDest))

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

        self.assertEqual((IBase, IOtherBase, ), IDest.__bases__)
        self.assertEqual(['base', 'foo', 'two', 'one', 'three'], getFieldNamesInOrder(IDest))

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

        self.assertEqual((IBase, IOtherBase, ), IDest.__bases__)
        self.assertEqual(['base', 'foo', 'two', 'one', 'three'], getFieldNamesInOrder(IDest))

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

        self.assertFalse(IMarker.providedBy(IDest['one']))
        self.assertFalse(IMarker.providedBy(IDest['two']))
        self.assertFalse(IMarker.providedBy(IDest['three']))
        self.assertTrue(IMarker.providedBy(IDest['four']))

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

        self.assertTrue(IMarker.providedBy(IDest['one']))
        self.assertFalse(IMarker.providedBy(IDest['two']))
        self.assertTrue(IMarker.providedBy(IDest['four']))

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

        self.assertEqual([3, 4, 1, 2, 4, 5], utils.mergedTaggedValueList(ISchema, u"foo"))

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
        IBase3.setTaggedValue(u"foo", {3: 3, 2: 3, 4: 3})  # least specific of the bases
        ISchema.setTaggedValue(u"foo", {4: 4, 5: 4})      # most specific

        self.assertEqual({1: 1, 2: 1, 3: 3, 4: 4, 5: 4}, utils.mergedTaggedValueDict(ISchema, u"foo"))


class TestValueToElement(unittest.TestCase):

    def setUp(self):
        configure()

    tearDown = zope.component.testing.tearDown

    def _assertSerialized(self, field, value, expected):
        element = utils.valueToElement(field, value, b('value'))
        if PY3:
            sio = BytesIO()
        else:
            sio = StringIO()
        etree.ElementTree(element).write(sio)
        self.assertEqual(sio.getvalue(), expected)
        unserialized = utils.elementToValue(field, element)
        self.assertEqual(value, b(unserialized))

    def test_lists(self):
        field = schema.List(value_type=schema.Int())
        value = []
        self._assertSerialized(field, value, b('<value/>'))
        value = [1, 2]
        self._assertSerialized(
            field, value,
            b('<value>'
              '<element>1</element>'
              '<element>2</element>'
              '</value>')
            )

    def test_nested_lists(self):
        field = schema.List(value_type=schema.List(value_type=schema.Int()))
        value = []
        self._assertSerialized(field, value, b('<value/>'))
        value = [[1], [1, 2], []]
        self._assertSerialized(field, value,
            b('<value>'
              '<element><element>1</element></element>'
              '<element><element>1</element><element>2</element></element>'
              '<element/>'
              '</value>')
            )

    def test_dicts(self):
        field = schema.Dict(key_type=schema.Int(), value_type=schema.TextLine())
        value = {}
        self._assertSerialized(field, value, b('<value/>'))
        value = {1: 'one', 2: 'two'}
        self._assertSerialized(field, value,
            b('<value>'
              '<element key="1">one</element>'
              '<element key="2">two</element>'
              '</value>')
            )

    def test_nested_dicts(self):
        field = schema.Dict(key_type=schema.Int(),
            value_type=schema.Dict(
                key_type=schema.Int(),
                value_type=schema.TextLine(),
                ),
            )
        value = {}
        self._assertSerialized(field, value, b('<value/>'))
        value = {1: {2: 'two'}, 3: {4: 'four', 5: 'five'}, 6: {}}
        self._assertSerialized(field, value,
            b('<value>'
              '<element key="1"><element key="2">two</element></element>'
              '<element key="3"><element key="4">four</element><element key="5">five</element></element>'
              '<element key="6"/>'
              '</value>')
            )


class TestChoiceHandling(unittest.TestCase):

    def setUp(self):
        configure()
        self.handler = ChoiceHandler(schema.Choice)

    def _choice(self):
        vocab = SimpleVocabulary(
            [SimpleTerm(t, title=t) for t in (u'a', u'b', u'c')]
            )
        expected = '<field name="myfield" type="zope.schema.Choice">'\
            '<values>'\
            '<element>a</element><element>b</element><element>c</element>'\
            '</values>'\
            '</field>'
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_empty(self):
        # add an empty string term to vocabulary
        vocab = SimpleVocabulary([SimpleTerm(t, title=t) for t in (u'a', u'')])
        expected = '<field name="myfield" type="zope.schema.Choice">'\
            '<values>'\
            '<element>a</element>'\
            '<element></element>'\
            '</values>'\
            '</field>'
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_term_titles(self):
        # two terms with distinct titles, one with same as value:
        vocab = SimpleVocabulary(
            [SimpleTerm(t, title=t.upper()) for t in (u'a', u'b')] +
            [SimpleTerm(u'c', title=u'c')],
            )
        expected = '<field name="myfield" type="zope.schema.Choice">'\
            '<values>'\
            '<element key="a">A</element>'\
            '<element key="b">B</element>'\
            '<element key="c">c</element>'\
            '</values>'\
            '</field>'
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_term_titles_and_ns(self):
        # two terms with distinct titles, one with same as value:
        vocab = SimpleVocabulary(
            [SimpleTerm(t, title=t.upper()) for t in (u'a', u'b')] +
            [SimpleTerm(u'c', title=u'c')],
            )
        expected = '<field name="myfield" type="zope.schema.Choice"'\
            '      xmlns="http://namespaces.plone.org/supermodel/schema">'\
            '<values>'\
            '<element key="a">A</element>'\
            '<element key="b">B</element>'\
            '<element key="c">c</element>'\
            '</values>'\
            '</field>'
        return (schema.Choice(vocabulary=vocab), expected)

    def test_choice_serialized(self):
        field, expected = self._choice()
        el = self.handler.write(field, 'myfield', 'zope.schema.Choice')
        self.assertEquals(etree.tostring(el), b(expected))
        # now with an empty string term in vocab:
        field, expected = self._choice_with_empty()
        el = self.handler.write(field, 'myfield', 'zope.schema.Choice')
        self.assertEquals(etree.tostring(el), b(expected))
        # now with terms that have titles:
        field, expected = self._choice_with_term_titles()
        el = self.handler.write(field, 'myfield', 'zope.schema.Choice')
        self.assertEquals(etree.tostring(el), b(expected))

    def test_choice_parsing(self):
        def _termvalues(vocab):
            return tuple((t.value, t.title) for t in vocab)
        cases = (
            self._choice(),
            self._choice_with_empty(),
            self._choice_with_term_titles(),
            self._choice_with_term_titles_and_ns(),
        )
        for field, expected in cases:
            el = etree.fromstring(expected)
            imported_field = self.handler.read(el)
            self.assertEquals(
                _termvalues(imported_field.vocabulary),
                _termvalues(field.vocabulary),
            )


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        if sys.version_info[0] > 2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub('u"(.*?)"', '"\\1"', want)
            got = re.sub(
                'plone.supermodel.parser.SupermodelParseError',
                'SupermodelParseError', got)
            got = re.sub(
                'zope.interface.exceptions.Invalid',
                'Invalid', got)
            got = re.sub(
                "(Import|ModuleNotFound)Error: No module named "
                "'plone.supermodel.tests.nonExistentFactory'; "
                "'plone.supermodel.tests' is not a package",
                'ImportError: No module named nonExistentFactory', got)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        unittest.makeSuite(TestValueToElement),
        unittest.makeSuite(TestChoiceHandling),
        doctest.DocFileSuite(
            'schema.rst',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.ELLIPSIS,
            checker=Py23DocChecker()),
        doctest.DocFileSuite(
            'fields.rst',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            optionflags=doctest.ELLIPSIS,
            checker=Py23DocChecker()),
        doctest.DocFileSuite(
            'schemaclass.rst',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            checker=Py23DocChecker()),
        doctest.DocFileSuite(
            'directives.rst',
            setUp=zope.component.testing.setUp,
            tearDown=zope.component.testing.tearDown,
            checker=Py23DocChecker()),
    ))


if __name__ == '__main__':
    unittest.main(default='test_suite')
