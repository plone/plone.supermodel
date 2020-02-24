zope.interface master, upcoming v5.0, initializes ``_v_attrs`` with ``None`` to save memory and creates the dict upon first usage.
So we need to do so in order to support the new version.