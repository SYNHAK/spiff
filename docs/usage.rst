Usage
=====

.. warning:
   
   A much improved management interface is needed. There is very little
   high-level management functionality, and most administrative actions are
   handled via the builtin Django admin interface, unless otherwise noted.
   
   Patches and questions are welcome.

.. _space-config:

Configuring your Space
----------------------

To rename your hackerspace, configure the only available Site object in the
Django admin interface. If you have more than one Site object, configure one to
use the correct domain name, delete the others, and optionally let the
developers know how it got there since Spiff should only ever have one.

Other properties are configurable through the SpaceConfig object in the Django
admin UI:

:site:
    Refers to the Django object. This shouldn't be changed unless you've got a
    good reason to.
:logo:
    URL that points to your space's logo. It may be absolute, or relative to
    your Spiff URL.
:openIcon:
    Used as part of the :doc:`spaceapi` to indicate a graphic to display if the
    space is open.
:closedIcon:
    Same as the :kbd:`openIcon`.
:url:
    Your space's website.
:open:
    Determines if your space is currently open or closed. Also see `Open
    Sensor`_, which provides programatic access to this.
:lat and lon:
    Latitude and longitude
:address:
    Your space's physical location.
:status:
    A free-form field that is shown in the :doc:`spaceapi`. For example, "Open
    to members only", or "Closed due to inclement weather".
:openSensor:
    See `Open Sensor`_.

.. _open-sensor:

Open Sensor
```````````

It is possible to configure Spiff to automatically handle opening/closing your
space with the :doc:`sensors` system, for whatever definition of "open" or "closed"
you have. The associated sensor must be a boolean type. When it has a true
value, the space is reported as open through the :doc:`spaceapi`. It is reported
as closed for false values. Refer to the :doc:`sensors` chapter for details.

Membership
----------

Spiff provides a basic system for staff to manage a member database,
self-service membership management, and accepting dues via Stripe_.

Each member has a few basic fields that should be filled out:

-  Email
-  First Name
-  Last Name
-  Birthday
-  Profession

These fields are public to the general internet, except for hidden users.

Administrators can add extra fields such as phone number, mailing
address, emergency contact information, etc. These extra fields have
three flags available:

-  Required - The profile will not save and a user can't register
   without this field being filled out. Examples: emergency contact information,
   digital signature proving they read the rules, preferred objective description
   of the color #33ff62.
-  Public - Other members can read the field, but not the entire
   internet. Members can edit their own public fields. Fields that are
   not public can still be read by those with the :kbd:`can_view_private_fields` permission. Examples:
   IRC nickname, membership sponsors, or exact reasons for disliking ABBA.
-  Protected - Only those with the :kbd:`can_edit_protected_fields` permission can view and edit
   the field. Members can read the value of their own protected fields,
   but can't edit them. This is useful for things that members should know about
   themselves, but others shouldn't know about others, and members shouldn't be
   able to change. Examples: a key/RFID token ID number, a note proving that
   they signed a liability waiver, a third meta-item that points out this is the
   third item in the third `list of lists of threes`_ and thus three times as funny.

.. _`list of lists of threes`: http://en.wikipedia.org/wiki/Rule_of_three_(writing)
.. _`Stripe`: http://stripe.com/

Ranks
`````

Many spaces have a set of ranks, such as "Basic Membership", "Board Member",
etc. Spiff allows you to model this via Spiff's Ranks and Django's builtin groups.

To create a new rank, such as "Basic Membership", create a new Group object via
the Django admin interface. This automatically creates a Rank object, which has
several properties:

:monthlyDues:
    How much it costs per month for this rank, in USD.
:group:
    The Django group object this rank refers to. There shouldn't be a need to
    ever change this.
:isActiveMembership:
    If a member is in this rank, they are considered an active member. This
    property is used to determine if a user pays dues, and to show the list of
    active members.
:isKeyholder:
    If a member is in this rank, they are considered a keyholder. This property
    is used by the :doc:`spaceapi` to list keymasters.

Each underlying Django group object can have a set of permissions attached to
it, which grants all members of the group those permissions.

Those with the :kbd:`membership.can_change_member_rank` permission may edit a
user's ranks by visiting the user's profile page.

.. seealso:: :doc:`permissions`

Membership Dues
``````````````

Managing membership dues is fairly straightforward, and involves very little
usage of the confusing Django administration interface: Simply configure the
:kbd:`isActiveMembership` and :kbd:`monthlyDues` properties of your roles and
forget about the admin interface.

A member's profile page will list their recent due payments, along with an
option to record a payment that was not handled by Spiff, such as cash or some
other payment method.

Recording partial payments are supported. This is useful for instances such as a
member paying $10 in cash and the last $40 via Stripe, or forgetting that dues
are $35 and not $30.


Resources
---------

In every hackerspace, theres a bunch of equipment sitting around that
not everyone might know how to use or even what it is called. Spiff
solves that problem.

You can create a Resource object in Spiff for each real-world resource.
After it is created, metadata can be attached to it and edited by users
with the correct permissions. Members can also keep track of their
training on the site, along with their relative skill ranks.

Users require the inventory.certify permission to be able to add and remove
certifications from members.

Skill ranking works on an honor system that requires users
undergo a vetting process by other users:

-  Your hackerspace acquires a nice new lathe.
-  A member adds the lathe to the database, prints out the QR code and
   sticks it on the machine.
-  Another member who happens to be a master metalworker sees that there
   is a Lathe, scans the code (or visits the resource page) and clicks
   "I have used this!" to indicate that they have used a Lathe at some
   point in their life.
-  A second member (who is a total newbie to metalworking) also clicks
   "I have used this!". Spiff says that both the newbie and the master
   are ranked at the same skill level, so they click "They are better
   than me".
-  Spiff now indicates that the master is better trained at the lathe
   than the newbie and sorts them accordingly.

At no point can the newbie say that they are better than the master
without the master explicitly promoting the newbie to their level.
Additionally, the newbie can't demote the master. Members are ranked
relative to each other based on this feedback system.

Not all resources in a hackerspace are trainable! For instance, it makes
no sense to say that someone is more skilled at using the classroom or
meeting area. When creating a resource, you can specify if a resource
can be trainable or not.

Events
------

Spiff also allows for tracking of events. Anyone with a proper
permission can create an event (and later edit it). Members can easily
RSVP for an event with a link on the event page. There is no special
permission required to state that you are attending an event.

If an event requires the use of some resource (which could be a
classroom, or maybe its a class on using the lathe), it is possible to
reserve the use of a resource by adding it to the event. This reservation system
is purely an advisory one at the moment. Nothing will stop someone from
reserving an already reserved item, or physically blocking you from using it.

Sensors
-------

See :doc:`sensors` for complete documentation.


