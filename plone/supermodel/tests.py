import unittest
from zope.testing import doctest

import zope.app.testing.placelesssetup

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('schema.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
