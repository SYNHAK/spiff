Permissions
===========

Spiff has a small set of permissions that say who can do what on the
site.

It is recommended to create a general purpose "Active Member" group to
keep track of who is and isn't a member and to provide a base set of
permissions that apply to all members. Afterwards, you can create new
groups for each membership level in your hackerspace.

membership.can\_view\_private\_fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can view any field that does not have the Public flag set.

membership.can\_edit\_protected\_fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can edit and view profile fields that are protected.

auth.can\_change\_user
~~~~~~~~~~~~~~~~~~~~~~

The user can edit the profiles of other users.

inventory.can\_change\_resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can add and modify resource metadata. can\_add\_metadata,
can\_change\_metadata, etc are not used at all in Spiff.

inventory.can\_train
~~~~~~~~~~~~~~~~~~~~

The user can promote other users' trainings and add themselves to a
resource at the lowest level.

events.can\_add\_event
~~~~~~~~~~~~~~~~~~~~~~

The user can create events and edit their own events.

events.can\_reserve\_resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can attach resources to their own events.

events.can\_change\_event
~~~~~~~~~~~~~~~~~~~~~~~~~

The user can edit other user's events. This is required for being able
to attach resources to events that they don't own.


