Spaceman Spiff Manages Spaces
=============================

:Author: Torrie Fischer <tdfischer@hackerbots.net>
:Contact: irc://chat.freenode.net/#synhak
:Date: |today|
:Version: |release|
:Copyright: Public Domain

Spaceman Spiff (or just Spiff) is a hackerspace management tool that helps
hackers manage a hackerspace. It comes with a builtin web interface for end
users, but is also exceptionally machine friendly.

Management of a hackerspace includes several topics:

- Membership
- Documentation
- Communication
- Infrastructure
- Governance

It is made available to the public under the AGPL.

Dependencies
============

.. include:: ../pip-requirements
   :literal:

Features
--------

-  Track member dues to see who is paid for the month
-  Multiple ranks with independent monthly dues
-  Keep track of space resources and metadata associated with each
   resource
-  Create arbitrary membership fields with visibility settings such as
   "Door Keycode" (editing/viewing limited to officers), "Enjoys Smooth
   Jazz" (viewing limited to members only), or "Nobel Prizes Earned"
   (public to the internet).
-  A thorough REST api to access everything
-  A skill tracking system
-  Simple interface to sensors
-  Perform actions when sensors are updated
-  An implementation of the SpaceAPI
-  Accept member dues through Stripe
-  Use of Django's builtin admin interface to provide low-level database editing.
-  Keep track of who is certified to use equipment
-  Merit based equipment skill level ranking system


Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   permissions
   sensors
   api
   development
   spaces

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

