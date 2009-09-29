import unittest
import zope.app.testing.placelesssetup

from zope.interface import Interface, implements, alsoProvides

import zope.component.testing
from zope.testing import doctest

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
        return SimpleVocabulary.fromValues(['a','d','f'])

dummy_binder = Binder()
dummy_vocabulary_instance = SimpleVocabulary.fromItems([(1,'a'), (2,'c')])

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
        
        self.assertEquals((Interface,), IDest.__bases__)
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
        
        self.assertEquals((IBase,), IDest.__bases__)
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
        
        self.assertEquals((IBase, IOtherBase,), IDest.__bases__)
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
        
        self.assertEquals((IBase, IOtherBase,), IDest.__bases__)
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
    
    def test_mergedTaggedValueList(self):
        
        class IBase1(Interface):
            pass
        class IBase2(Interface):
            pass
        class IBase3(Interface):
            pass
        class ISchema(IBase1, IBase2, IBase3):
            pass
            
        IBase1.setTaggedValue(u"foo",  [1,2])  # more specific than IBase2 and IBase3
        IBase3.setTaggedValue(u"foo",  [3,4])  # least specific of the bases
        ISchema.setTaggedValue(u"foo", [4,5])  # most specific
        
        self.assertEquals([3,4, 1,2, 4,5], utils.mergedTaggedValueList(ISchema, u"foo"))

    def test_mergedTaggedValueDict(self):
        
        class IBase1(Interface):
            pass
        class IBase2(Interface):
            pass
        class IBase3(Interface):
            pass
        class ISchema(IBase1, IBase2, IBase3):
            pass
            
        IBase1.setTaggedValue(u"foo",  {1:1, 2:1})      # more specific than IBase2 and IBase3
        IBase3.setTaggedValue(u"foo",  {3:3, 2:3, 4:3}) # least specific of the bases
        ISchema.setTaggedValue(u"foo", {4:4, 5:4})      # most specific
        
        self.assertEquals({1:1, 2:1, 3:3, 4:4, 5:4}, utils.mergedTaggedValueDict(ISchema, u"foo"))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        doctest.DocFileSuite('schema.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        doctest.DocFileSuite('fields.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
