from io import BytesIO
from io import StringIO
from lxml import etree
from plone.supermodel import utils
from plone.supermodel.exportimport import ChoiceHandler
from plone.supermodel.interfaces import IDefaultFactory
from plone.supermodel.interfaces import IInvariant
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
import re
import unittest
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
    title = schema.TextLine(title="Title")
    description = schema.TextLine(title="Description")
    name = schema.TextLine(title="Name")


# Used in fields.txt


class IDummy(Interface):
    title = schema.TextLine(title="Title")


@implementer(IDummy)
class Dummy:
    def __init__(self):
        self.title = ""


dummy1 = Dummy()


@implementer(IContextSourceBinder)
class Binder:
    def __init__(self):
        pass

    def __call__(self, context):
        return SimpleVocabulary.fromValues(["a", "d", "f"])


dummy_binder = Binder()
dummy_vocabulary_instance = SimpleVocabulary.fromItems([(1, "a"), (2, "c")])


@provider(IContextAwareDefaultFactory)
def dummy_defaultCAFactory(context):
    return "b"


@provider(IDefaultFactory)
def dummy_defaultFactory():
    return "b"


def dummy_defaultBadFactory():
    return "b"


@provider(IInvariant)
def dummy_invariant(data):
    raise Invalid("Yikes! Invalid")


@provider(IInvariant)
def dummy_invariant_prime(data):
    return None


def dummy_unmarkedInvariant(data):
    """lacks IInvariant marker"""
    return None


class TestUtils(unittest.TestCase):
    def test_syncSchema(self):
        class ISource(Interface):
            one = schema.TextLine(title="A")  # order: 0
            two = schema.Int(title="B")  # order: 1

        class IDest(Interface):
            one = schema.TextLine(title="C")  # order: 0
            three = schema.Int(title="D")  # order: 1

        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")

        utils.syncSchema(ISource, IDest)

        self.assertEqual("C", IDest["one"].title)

        self.assertEqual(["one", "two"], getFieldNamesInOrder(ISource))
        self.assertEqual(["two", "one", "three"], getFieldNamesInOrder(IDest))

        self.assertEqual("first tag", IDest.getTaggedValue("tag1"))
        self.assertEqual("tag two", IDest.getTaggedValue("tag2"))

    def test_syncSchema_overwrite(self):
        class ISource(Interface):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")

        class IDest(Interface):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")

        utils.syncSchema(ISource, IDest, overwrite=True)

        self.assertEqual("A", IDest["one"].title)

        self.assertEqual(["one", "two"], getFieldNamesInOrder(ISource))
        self.assertEqual(["one", "two"], getFieldNamesInOrder(IDest))

        self.assertEqual("tag one", IDest.getTaggedValue("tag1"))
        self.assertEqual("tag two", IDest.getTaggedValue("tag2"))

    def test_syncSchema_overwrite_no_bases(self):
        class IBase(Interface):
            base = schema.TextLine(title="Base")

        class ISource(IBase):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")

        class IDest(Interface):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=False)

        self.assertEqual((Interface,), IDest.__bases__)
        self.assertEqual(["two", "one", "three"], getFieldNamesInOrder(IDest))

    def test_syncSchema_overwrite_with_bases(self):
        class IBase(Interface):
            base = schema.TextLine(title="Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title="Foo")

        class ISource(IBase):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")

        class IDest(IOtherBase):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest, overwrite=True, sync_bases=True)

        self.assertEqual((IBase,), IDest.__bases__)
        self.assertEqual(["base", "one", "two"], getFieldNamesInOrder(IDest))

    def test_syncSchema_overwrite_with_bases_and_no_overwrite(self):
        class IBase(Interface):
            base = schema.TextLine(title="Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title="Foo")

        class ISource(IBase):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")

        class IDest(IOtherBase):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=True)

        self.assertEqual(
            (
                IBase,
                IOtherBase,
            ),
            IDest.__bases__,
        )
        self.assertEqual(
            ["base", "foo", "two", "one", "three"], getFieldNamesInOrder(IDest)
        )

    def test_syncSchema_overwrite_with_bases_and_no_overwrite_with_old_bases(self):
        class IBase(Interface):
            base = schema.TextLine(title="Base")

        class IOtherBase(Interface):
            foo = schema.TextLine(title="Foo")

        class ISource(IBase):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")

        class IDest(IOtherBase, IBase):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest, overwrite=False, sync_bases=True)

        self.assertEqual(
            (
                IBase,
                IOtherBase,
            ),
            IDest.__bases__,
        )
        self.assertEqual(
            ["base", "foo", "two", "one", "three"], getFieldNamesInOrder(IDest)
        )

    def test_syncSchema_with_markers_no_overwrite(self):
        class IMarker(Interface):
            pass

        class ISource(Interface):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")
            four = schema.Text(title="C")

        alsoProvides(ISource["one"], IMarker)
        alsoProvides(ISource["four"], IMarker)

        class IDest(Interface):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest)

        self.assertFalse(IMarker.providedBy(IDest["one"]))
        self.assertFalse(IMarker.providedBy(IDest["two"]))
        self.assertFalse(IMarker.providedBy(IDest["three"]))
        self.assertTrue(IMarker.providedBy(IDest["four"]))

    def test_syncSchema_with_markers_overwrite(self):
        class IMarker(Interface):
            pass

        class ISource(Interface):
            one = schema.TextLine(title="A")
            two = schema.Int(title="B")
            four = schema.Text(title="C")

        alsoProvides(ISource["one"], IMarker)
        alsoProvides(ISource["four"], IMarker)

        class IDest(Interface):
            one = schema.TextLine(title="C")
            three = schema.Int(title="D")

        utils.syncSchema(ISource, IDest, overwrite=True)

        self.assertTrue(IMarker.providedBy(IDest["one"]))
        self.assertFalse(IMarker.providedBy(IDest["two"]))
        self.assertTrue(IMarker.providedBy(IDest["four"]))

    def test_syncSchema_always_overwrites_fields_from_bases(self):
        class IBase(Interface):
            one = schema.TextLine(title="A")

        class ISource(Interface):
            one = schema.TextLine(title="B")

        class IDest(IBase):
            pass

        utils.syncSchema(ISource, IDest, overwrite=False)

        self.assertTrue(IDest["one"].interface is IDest)

    def test_mergedTaggedValueList(self):
        class IBase1(Interface):
            pass

        class IBase2(Interface):
            pass

        class IBase3(Interface):
            pass

        class ISchema(IBase1, IBase2, IBase3):
            pass

        IBase1.setTaggedValue("foo", [1, 2])  # more specific than IBase2 and IBase3
        IBase3.setTaggedValue("foo", [3, 4])  # least specific of the bases
        ISchema.setTaggedValue("foo", [4, 5])  # most specific

        self.assertEqual(
            [3, 4, 1, 2, 4, 5], utils.mergedTaggedValueList(ISchema, "foo")
        )

    def test_mergedTaggedValueDict(self):
        class IBase1(Interface):
            pass

        class IBase2(Interface):
            pass

        class IBase3(Interface):
            pass

        class ISchema(IBase1, IBase2, IBase3):
            pass

        IBase1.setTaggedValue(
            "foo", {1: 1, 2: 1}
        )  # more specific than IBase2 and IBase3
        IBase3.setTaggedValue("foo", {3: 3, 2: 3, 4: 3})  # least specific of the bases
        ISchema.setTaggedValue("foo", {4: 4, 5: 4})  # most specific

        self.assertEqual(
            {1: 1, 2: 1, 3: 3, 4: 4, 5: 4}, utils.mergedTaggedValueDict(ISchema, "foo")
        )


class TestValueToElement(unittest.TestCase):
    def setUp(self):
        configure()

    tearDown = zope.component.testing.tearDown

    def _assertSerialized(self, field, value, expected):
        element = utils.valueToElement(field, value, b"value")
        sio = BytesIO()
        etree.ElementTree(element).write(sio)
        self.assertEqual(sio.getvalue(), expected)
        unserialized = utils.elementToValue(field, element)
        self.assertEqual(value, unserialized)

    def test_lists(self):
        field = schema.List(value_type=schema.Int())
        value = []
        self._assertSerialized(field, value, b"<value/>")
        value = [1, 2]
        self._assertSerialized(
            field,
            value,
            b"<value>" b"<element>1</element>" b"<element>2</element>" b"</value>",
        )

    def test_sets(self):
        field = schema.Set(
            value_type=schema.Int(),
        )
        value = set()
        self._assertSerialized(field, value, b"<value/>")
        value = {3, 4, 2, 1}
        # Sets should be sorted to ensure nice diffs
        self._assertSerialized(
            field,
            value,
            b"<value>"
            b"<element>1</element>"
            b"<element>2</element>"
            b"<element>3</element>"
            b"<element>4</element>"
            b"</value>",
        )

        field = schema.Set(
            value_type=schema.Choice(["a", "b", "c"]),
        )
        value = {"b", "a"}
        # Sets should be sorted to ensure nice diffs
        self._assertSerialized(
            field,
            value,
            b"<value>" b"<element>a</element>" b"<element>b</element>" b"</value>",
        )

    def test_nested_lists(self):
        field = schema.List(value_type=schema.List(value_type=schema.Int()))
        value = []
        self._assertSerialized(field, value, b"<value/>")
        value = [[1], [1, 2], []]
        self._assertSerialized(
            field,
            value,
            b"<value>"
            b"<element><element>1</element></element>"
            b"<element><element>1</element><element>2</element></element>"
            b"<element/>"
            b"</value>",
        )

    def test_dicts(self):
        field = schema.Dict(key_type=schema.Int(), value_type=schema.TextLine())
        value = {}
        self._assertSerialized(field, value, b"<value/>")
        value = {1: "one", 2: "two"}
        self._assertSerialized(
            field,
            value,
            b"<value>"
            b'<element key="1">one</element>'
            b'<element key="2">two</element>'
            b"</value>",
        )

    def test_nested_dicts(self):
        field = schema.Dict(
            key_type=schema.Int(),
            value_type=schema.Dict(
                key_type=schema.Int(),
                value_type=schema.TextLine(),
            ),
        )
        value = {}
        self._assertSerialized(field, value, b"<value/>")
        value = {1: {2: "two"}, 3: {4: "four", 5: "five"}, 6: {}}
        self._assertSerialized(
            field,
            value,
            b"<value>"
            b'<element key="1"><element key="2">two</element></element>'
            b'<element key="3"><element key="4">four</element><element key="5">five</element></element>'
            b'<element key="6"/>'
            b"</value>",
        )


class TestChoiceHandling(unittest.TestCase):
    def setUp(self):
        configure()
        self.handler = ChoiceHandler(schema.Choice)

    def _choice(self):
        vocab = SimpleVocabulary([SimpleTerm(t, title=t) for t in ("a", "b", "c")])
        expected = (
            '<field name="myfield" type="zope.schema.Choice">'
            "<values>"
            "<element>a</element><element>b</element><element>c</element>"
            "</values>"
            "</field>"
        )
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_empty(self):
        # add an empty string term to vocabulary
        vocab = SimpleVocabulary([SimpleTerm(t, title=t) for t in ("a", "")])
        expected = (
            '<field name="myfield" type="zope.schema.Choice">'
            "<values>"
            "<element>a</element>"
            "<element></element>"
            "</values>"
            "</field>"
        )
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_term_titles(self):
        # two terms with distinct titles, one with same as value:
        vocab = SimpleVocabulary(
            [SimpleTerm(t, title=t.upper()) for t in ("a", "b")]
            + [SimpleTerm("c", title="c")],
        )
        expected = (
            '<field name="myfield" type="zope.schema.Choice">'
            "<values>"
            '<element key="a">A</element>'
            '<element key="b">B</element>'
            '<element key="c">c</element>'
            "</values>"
            "</field>"
        )
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_term_titles_and_ns(self):
        # two terms with distinct titles, one with same as value:
        vocab = SimpleVocabulary(
            [SimpleTerm(t, title=t.upper()) for t in ("a", "b")]
            + [SimpleTerm("c", title="c")],
        )
        expected = (
            '<field name="myfield" type="zope.schema.Choice"'
            '      xmlns="http://namespaces.plone.org/supermodel/schema">'
            "<values>"
            '<element key="a">A</element>'
            '<element key="b">B</element>'
            '<element key="c">c</element>'
            "</values>"
            "</field>"
        )
        return (schema.Choice(vocabulary=vocab), expected)

    def _choice_with_integers(self):
        vocab = SimpleVocabulary([SimpleTerm(1, title="One")])
        expected = (
            '<field name="myfield" type="zope.schema.Choice">'
            "<values>"
            '<element key="1">One</element>'
            "</values>"
            "</field>"
        )
        return (schema.Choice(vocabulary=vocab), expected)

    def test_choice_serialized(self):
        """Tests a regular choice, one with empty string term in vocab,
        and another with terms that have titles
        """
        choice = self._choice()
        choice_with_empty = self._choice_with_empty()
        choice_with_term_titles = self._choice_with_term_titles()
        choice_with_integers = self._choice_with_integers()
        for case in (
            choice,
            choice_with_empty,
            choice_with_term_titles,
            choice_with_integers,
        ):
            field, expected = case
            expected = bytes(expected, encoding="latin-1")
            el = self.handler.write(field, "myfield", "zope.schema.Choice")
            self.assertEqual(etree.tostring(el), expected)

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
            self.assertEqual(
                _termvalues(imported_field.vocabulary),
                _termvalues(field.vocabulary),
            )


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        want = re.sub('u"(.*?)"', '"\\1"', want)
        got = re.sub(
            "plone.supermodel.parser.SupermodelParseError", "SupermodelParseError", got
        )
        got = re.sub("zope.interface.exceptions.Invalid", "Invalid", got)
        got = re.sub(
            "(Import|ModuleNotFound)Error: No module named "
            "'plone.supermodel.tests.nonExistentFactory'; "
            "'plone.supermodel.tests' is not a package",
            "ImportError: No module named nonExistentFactory",
            got,
        )
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


optionflags = (
    doctest.ELLIPSIS
    | doctest.REPORT_UDIFF
    | doctest.NORMALIZE_WHITESPACE
    | doctest.REPORT_ONLY_FIRST_FAILURE
)


def test_suite():
    return unittest.TestSuite(
        (
            unittest.defaultTestLoader.loadTestsFromTestCase(TestUtils),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestValueToElement),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestChoiceHandling),
            doctest.DocFileSuite(
                "fields.rst",
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
            doctest.DocFileSuite(
                "directives.rst",
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
            doctest.DocFileSuite(
                "schema.rst",
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
            doctest.DocFileSuite(
                "schemaclass.rst",
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown,
                optionflags=optionflags,
                checker=Py23DocChecker(),
            ),
        )
    )


if __name__ == "__main__":
    unittest.main(default="test_suite")
