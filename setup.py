import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.5.dev0'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
    )

setup(name='plone.supermodel',
      version=version,
      description="Serialize Zope schema definitions to and from XML",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='Plone XML schema',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://code.google.com/p/dexterity',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lxml',
          'zope.component',
          'zope.interface',
          'zope.schema',
          'zope.deferredimport',
          'zope.dottedname',
          'z3c.zcmlhook',
      ],
      extras_require={
        'lxml': [],  # BBB
        'plone.rfc822': ['plone.rfc822'],
        'test': [
            'plone.rfc822',
            ],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
