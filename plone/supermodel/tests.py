import unittest
import zope.app.testing.placelesssetup

from zope.interface import Interface
from plone.supermodel.directives import Schema, model

import zope.component.testing
from zope.testing import doctest

from zope.interface import Interface
from zope.schema import getFieldNamesInOrder
from zope import schema

from plone.supermodel import utils

from grokcore.component.testing import grok, grok_component

class TestUtils(unittest.TestCase):
    
    def test_sync_schema(self):
        
        class ISource(Interface):
            one = schema.TextLine(title=u"A") # order: 0
            two = schema.Int(title=u"B")      # order: 1
        
        class IDest(Interface):
            one = schema.TextLine(title=u"C") # order: 0
            three = schema.Int(title=u"D")    # order: 1
        
        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")
        
        utils.sync_schema(ISource, IDest)
        
        self.assertEquals(u"C", IDest['one'].title)
        
        self.assertEquals(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEquals(['two', 'one', 'three'], getFieldNamesInOrder(IDest))
        
        self.assertEquals("first tag", IDest.getTaggedValue("tag1"))
        self.assertEquals("tag two", IDest.getTaggedValue("tag2"))
    
    def test_sync_schema_overwrite(self):
        
        class ISource(Interface):
            one = schema.TextLine(title=u"A")
            two = schema.Int(title=u"B")
        
        class IDest(Interface):
            one = schema.TextLine(title=u"C")
            three = schema.Int(title=u"D")
        
        ISource.setTaggedValue("tag1", "tag one")
        ISource.setTaggedValue("tag2", "tag two")
        IDest.setTaggedValue("tag1", "first tag")
        
        utils.sync_schema(ISource, IDest, overwrite=True)
        
        self.assertEquals(u"A", IDest['one'].title)
        
        self.assertEquals(['one', 'two'], getFieldNamesInOrder(ISource))
        self.assertEquals(['one', 'two'], getFieldNamesInOrder(IDest))
        
        self.assertEquals("tag one", IDest.getTaggedValue("tag1"))
        self.assertEquals("tag two", IDest.getTaggedValue("tag2"))

class TestDirectives(unittest.TestCase):
    
    def setUp(self):
        grok('plone.supermodel.directives')
        
    def teatDown(self):
        zope.component.testing.tearDown(self)
    
    def test_schema_without_model_not_grokker(self):
        
        class IFoo(Schema):
            pass
            
        self.assertEquals(False, grok_component('IFoo', IFoo))

    def test_non_schema_not_grokked(self):
        
        class IFoo(Interface):
            model('dummy.xml')
            
        self.assertEquals(False, grok_component('IFoo', IFoo))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        unittest.makeSuite(TestDirectives),
        doctest.DocFileSuite('schema.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
