Spaceman Spiff Manages Spaces
=============================

:Author: Trever Fischer <wm161@wm161.net>
:Contact: irc://chat.freenode.net/#synhak
:Date: |today|
:Version: |release|
:Copyright: Public Domain

Spiff is a Django API server that helps you manage a hackerspace. It comes with
a builtin web interface for end users, but is also exceptionally machine
friendly.

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
-  Generate QR codes to stick on things that link to Resource pages
-  Create arbitrary membership fields with visibility settings such as
   "Door Keycode" (editing/viewing limited to officers), "Enjoys Smooth
   Jazz" (viewing limited to members only), or "Nobel Prizes Earned"
   (public to the internet).
-  A simple REST api to access everything
-  A merit-based proficiency tracking system
-  Machine and user-friendly sensor tracking
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

