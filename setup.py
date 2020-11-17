# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.6.3'

long_description = (
    read('README.rst') + '\n' +
    read('CHANGES.rst') + '\n'
    )

setup(
    name='plone.supermodel',
    version=version,
    description="Serialize Zope schema definitions to and from XML",
    long_description=long_description,
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: Core",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='Plone XML schema',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/plone/plone.supermodel',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'six',
        'lxml',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema>=4.1.0',
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
