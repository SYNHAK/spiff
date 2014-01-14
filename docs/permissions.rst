Permissions
===========

Spiff has a set of permissions that say who can do what on the
site.

It is recommended to create a general purpose "Active Member" rank to
keep track of who is and isn't a member and to provide a base set of
permissions that apply to all members. Afterwards, you can create new
ranks for each membership level in your hackerspace.

.. note::

    Run ./manage.py permission_list to retrieve a list of permissions and
    brief descriptions. Only permissions used in Spiff codebase are
    documented. See the `Django auth reference`_ for information about
    how permissions work inside Django.

.. _`Django auth reference`: https://docs.djangoproject.com/en/1.6/topics/auth/

auth.change\_user
~~~~~~~~~~~~~~~~~~~~~~

The user can edit the profiles of other users.

auth.delete\_user
~~~~~~~~~~~~~~~~~

The user can delete other users.

events.add\_event
~~~~~~~~~~~~~~~~~~~~~~

The user can create events and edit their own events.

events.can\_reserve\_resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can attach resources to their own events.

events.change\_event
~~~~~~~~~~~~~~~~~~~~~~~~~

The user can edit other user's events. This along with can\_reserve\_resource is required for being able
to attach resources to events that they don't own.

inventory.certify
~~~~~~~~~~~~~~~~~

The user may grant and remove certifications for resources from members.

inventory.change\_resource
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can add and modify resource metadata.add\_metadata,
change\_metadata, etc are not used at all in Spiff.

inventory.can\_train
~~~~~~~~~~~~~~~~~~~~

The user can promote other users' trainings and add themselves to a
resource at the lowest level.

membership.add\_duepayment
~~~~~~~~~~~~~~~~~~~~~~~~~~

The user may add previous due payments to Spiff.


membership.can\_change\_member\_rank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user may view modify the ranks a member belongs to.

membership.can\_edit\_protected\_fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can edit and view profile fields that are protected.

membership.can\_view\_hidden\_members
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user is able to view members that have the hidden flag set.

membership.can\_view\_member\_rank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user is able to view another user's ranks.

membership.can\_view\_private\_fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user can view any field that does not have the Public flag set.
