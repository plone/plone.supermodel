from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "2.0.5.dev0"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

setup(
    name="plone.supermodel",
    version=version,
    description="Serialize Zope schema definitions to and from XML",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords="Plone XML schema",
    author="Martin Aspeli",
    author_email="optilude@gmail.com",
    url="https://github.com/plone/plone.supermodel",
    license="BSD",
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "setuptools",
        "lxml",
        "zope.component",
        "zope.i18nmessageid",
        "zope.interface",
        "zope.schema>=4.1.0",
        "zope.deferredimport",
        "zope.dottedname",
        "z3c.zcmlhook",
    ],
    extras_require={
        "lxml": [],  # BBB
        "plone.rfc822": ["plone.rfc822"],
        "test": [
            "plone.rfc822",
            "zope.configuration[test]",
        ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
