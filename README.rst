Introduction
============

plone.supermodel provides XML import and export for schema interfaces based on
zope.schema fields. The principal use cases are:

 1. Define a schema interface in code based on an XML file. This can be done
 with syntax like::

  >>> from plone.supermodel import xmlSchema
  >>> IMySchema = xmlSchema("myschema.xml")

 2. Save and load interface definitions via an XML format. To turn a schema
 interface into XML, you can do::

  >>> from plone.supermodel import serializeSchema
  >>> xml_string = serializeSchema(IMySchema)

To get a schema from an XML file, you can use the xmlSchema() function above,
or you can use the more powerful spec() function, which turns a dict of all
schemata and widget hints in a given XML file.

See schema.txt and interfaces.py in the source code for more information,
including details on how to give widget hints for forms and how to keep
multiple schemata in the same XML file.

Supermodel vs. Userschema
-------------------------

This package is quite similar to Tres Seaver's "userschema" library, which
can be found at http://agendaless.com/Members/tseaver/software/userschema.

In fact, plone.supermodel was originally based on userschema. However, as the
package was refined and refactored, less and less of userschema remained,
to the point where we'd have needed to significantly refactor the latter to
keep using it.

The XML import/export code is currently based on algorithms that were written
for plone.app.portlets and plone.app.contentrules' GenericSetup handlers.

Some of the key differences between the two packages are:

 - userschema can create schema interfaces from HTML forms and CSV
   spreadsheets. plone.supermodel does not support such configuration.

 - Schemata created with userschema are typically loaded at startup, with
   a ZCML directive. plone.supermodel supports a "pseudo-base class" syntax,
   as seen above, to define interfaces in Python code. Beyond that, its API
   is more geared towards runtime configuration.

 - plone.supermodel supports serialisation of schemata to XML.

 - The plone.supermodel XML syntax is more directly tied to zope.schema
   fields, and infers most parameters from the schema interface declared by
   each zope.schema field. This has two advantages:

    - API documentation for zope.schema can be easily applied to <schema />
      blocks
    - New fields and obscure attributes are easier to support

 - plone.supermodel's XML schema is intended to support more schema metadata,
   including widget hints.

In the future, it may be possible to make userschema re-use part of
plone.supermodel or vice-a-versa, with more refactoring.

