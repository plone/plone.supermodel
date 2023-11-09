Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

1.7.0 (2023-11-10)
------------------

New features:


- Make finalizeSchema more robust by not handling behavior schema classes.
  Backported from version 2.0.
  [maurits] (#186)


1.6.5 (2022-07-13)
------------------

Bug fixes:


- Release 1.6.3 as 1.6.5.
  The 1.6.4 release in between was meant as a major release.
  I will rerelease that one as 2.0.0.
  [maurits] (#27)


1.6.4 (2021-09-01)
------------------

Breaking changes:

- Make finalizeSchema more robust by not handling behavior schema classes (#27)


1.6.3 (2020-11-17)
------------------

Bug fixes:


- For increased security, in the xml parser do not resolve entities, and remove processing instructions.
  [maurits] (#3209)


1.6.2 (2020-06-24)
------------------

Bug fixes:


- Decimal field moved in zope.schema, do not depend on specific dotted name in test b/c it does not matter.
  [jensens] (#37)
- Fix a deprecation warning on a regular expression [ale-rt] (#38)


1.6.1 (2020-04-22)
------------------

Bug fixes:


- Minor packaging updates. (#1)


1.6.0 (2020-03-09)
------------------

New features:


- zope.interface master, upcoming v5.0, initializes ``_v_attrs`` with ``None`` to save memory and creates the dict upon first usage.
  So we need to do so in order to support the new version. (#33)
- Support for zope.interface 4.7+ [jensens] (#34)


1.5.0 (2019-12-11)
------------------

New features:


- Add support for choices of integers for improved registry.xml export.
  [jone] (#32)


1.4.1 (2019-11-25)
------------------

Bug fixes:

- tests to ensure schema.Set is serialized consistently (#30)



1.4.0 (2018-09-28)
------------------

New features:

- Python 3 compatibility.
  [pbauer, davilima6, dhavlik, ale-rt]


1.3.4 (2017-11-24)
------------------

Bug fixes:

- Python3 compatibility with sixer
  [ale-rt]


1.3.3 (2017-06-04)
------------------

Bug fixes:

- Fixed typecasting of IChoice based on its vocabulary. #16
  [iham]


1.3.2 (2017-02-05)
------------------

Bug fixes:

- Fix issue where supermodel XML choice field parser failed to parse vocabulary
  values with separate keys and display titles, because the parser expected
  values tag to not have any namespace.
  [datakurre]


1.3.1 (2016-12-30)
------------------

Bug fixes:

- Test-Fix: Support latest zope.i18nmessageid.
  [jensens]


1.3.0 (2016-06-07)
------------------

New:

- Python 2.6 and Plone 4.3 no longer officially supported.  It might
  still work, but no special effort is made to keep this compatible.
  [maurits]

- Support to define the order of fieldsets.
  [jensens]

Fixes:

- Remove temporary fix regarding test failures on Zope 4, as it's already fixed.
  [thet]

- Update setup.py url to point to github location.
  [esteele]

- Unset _init_field flag on init completion.
  [metatoaster]


1.2.7 (2016-02-12)
------------------

Fixes:

- Add temporary fix for a test failure within a Zope 4 environment.
  [pbauer]


1.2.6 (2014-10-20)
------------------

- Code modernization: sorted imports, use decorators, utf8 headers.
  [jensens]

- Add i18n serialization from schema value to XML model
  [datakurre]

1.2.5 (2014-09-07)
------------------

- Support Choice fields with terms containing distinct title from value
  as option, while preserving backward-compatible round-trip for all
  Choice fields where title is not distinct from value.
  [seanupton]

- Fix parsing of empty Choice term to u'', not None, which addresses a
  cause of https://github.com/plone/plone.app.dexterity/issues/49
  [seanupton]

- Explicitly construct SimpleTerm instances for each Choice field
  element, instead of relying on zope.schema constructors to do so.
  This ensures that all terms have non-None title attributes.
  [seanupton]

- Tests for ChoiceHandler serialization and parsing.
  [seanupton]


1.2.4 (2014-01-27)
------------------

- Add invariant tag, a sub-element of schema, that accepts a dotted name as
  a value. Invariants must provide plone.supermodel.interface.IInvariant.
  [smcmahon]

- Replace deprecated test assert statements.
  [timo]


1.2.3 (2013-08-14)
------------------

- Add defaultFactory tag for Dexterity XML. Define an interface
  IDefaultFactory. defaultFactories specified via XML must implement it or
  IContextAwareDefaultFactory.
  [smcmahon]


1.2.2 (2013-05-23)
------------------

- Avoid trying to process XML comments within field values.
  [davisagli]


1.2.1 (2013-01-01)
------------------

- Allow XML comments in field definitions.
  [gweis]

1.2.0 (2012-10-17)
------------------

- Nothing changed yet.


1.1.2 (2012-08-29)
------------------

- Use lxml instead of elementtree.
  [davisagli]

- Avoid a test dependency on zope.app.testing.
  [davisagli]


1.1.1 (2012-04-15)
------------------

- Fix a packaging error.
  [esteele]

1.1 (2012-04-15)
----------------

- Support i18n:domain and i18n:translate for internationalization.
  [davisagli]

- When an error is encountered while parsing a supermodel, the exception
  now provides the filename, line number, and source of the part of the
  model that was being processed. Inclusion of the line number and source
  requires lxml.
  [davisagli]

- Add model.Schema and directives to avoid grok dependency.
  [elro]

1.0.4 - 2012-02-20
------------------

- When syncing to a schema that inherits fields from a base, include fields
  with the same names as the inherited fields even when overwrite is False.
  This fixes http://code.google.com/p/dexterity/issues/detail?id=253
  [davisagli]

1.0.3 - 2011-05-20
------------------

- Relicense under BSD license.
  See http://plone.org/foundation/materials/foundation-resolutions/plone-framework-components-relicensing-policy
  [davisagli]

1.0.2 - 2011-05-02
------------------

- Only convert Choice field ``values`` attribute into a vocabulary when it is
  necessary to handle unicode values. This fixes a regression in compatibility
  with plone.registry.
  [davisagli]

1.0.1 - 2011-04-30
------------------

- Adjust manifest to exclude .pyc files.
  [davisagli]

1.0 - 2011-04-30
----------------

- Handle serializing tokenized vocabularies with unicode values as long as the
  terms' tokens are equal to the utf8-encoded values.
  [davisagli]


1.0b8 - 2011-03-18
------------------

- Add MANIFEST.in.
  [WouterVH]

- Field names should be strings, not unicode.
  [elro]


1.0b7 - 2011-03-03
------------------

- Support serialization of nested dicts/lists.
  [elro]


1.0b6 - 2011-01-04
------------------

- Declare zope.app.testing as a test dependency for Zope 2.13 compatibility.
  [esteele]

- Fix namespace bug which could prevent loading Dict and Collection elements.
  [davisagli]


1.0b5 - 2010-04-19
------------------

- Added support for zope.schema.Decimal fields.
  [optilude]


1.0b4 - 2009-11-17
------------------

- Ignored vocabularyName property when writing Choice fields. The constructor
  still uses they 'vocabulary' key in an overloaded capacity. We only support
  'vocabulary' with a named vocabulary, or 'values' with a list of values.
  This fixes test failures on Zope 2.12 / zope.schema 3.5.4.
  [optilude]


1.0b3 - 2009-09-28
------------------

- Add support for synchronising marker interfaces found on source fields
  to syncSchema().
  [optilude]


1.0b2 - 2009-07-12
------------------

- Changed API methods and arguments to mixedCase to be more consistent with
  the rest of Zope. This is a non-backwards-compatible change. Our profuse
  apologies, but it's now or never. :-/

  If you find that you get import errors or unknown keyword arguments in your
  code, please change names from foo_bar too fooBar, e.g. load_file() becomes
  loadFile().
  [optilude]

- No longer include name kwarg to Field constructor if no name was set
  [MatthewWilkes]


1.0b1 - 2009-04-17
------------------

- Initial release
