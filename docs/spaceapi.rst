SpaceAPI
========

Spiff currently implements version 0.12 of the SpaceAPI. You can read
more about it at http://hackerspaces.nl/spaceapi/

You may access the SpaceAPI through /status.json, as per the standard. If your
spiff installation is accessed via a different url (eg: https://synhak.org/auth/),
status.json will be at /auth/status.json. 

.. seealso:: :ref:`space-config`

Spiff Extensions
----------------

Spiff adds a few minor extensions to the SpaceAPI:

:x-spiff-url:
    The URL used to access spiff. Can be used to build full REST urls, such as
    http://example.com/path/to/spiff/resources/1.json
:x-spiff-version:
    The version of the Spiff REST API. This is not the version of spiff
    installed!
:x-spiff-open-sensor:
    The ID of the sensor used to determine if the space is open or not. See
    :ref:`open-sensor` for details.
