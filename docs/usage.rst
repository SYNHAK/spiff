Usage
=====

Resources
---------

In every hackerspace, theres a bunch of equipment sitting around that
not everyone might know how to use or even what it is called. Spiff
solves that problem.

You can create a Resource object in Spiff for each real-world resource.
After it is created, metadata can be attached to it and edited by users
with the correct permissions. Members can also keep track of their
training on the site. It works on an honor system that requires users
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

Membership
----------

Spiff provides a basic system for managing members.

Each member has a few basic fields that should be filled out:

-  Email
-  First Name
-  Last Name
-  Birthday
-  Profession

These fields are public to the general internet.

Administrators can add extra fields such as phone number, mailing
address, emergency contact information, etc. These extra fields have
three flags available:

-  Required - The profile will not save and a user can't register
   without this field being filled out.
-  Public - Other members can read the field, but not the entire
   internet. Members can edit their own public fields. Fields that are
   not public can still be read by those with the proper permission.
-  Protected - Only those with the proper permission can view and edit
   the field. Members can read the value of their own protected fields,
   but can't edit them.

Events
------

Spiff also allows for tracking of events. Anyone with a proper
permission can create an event (and later edit it). Members can easily
RSVP for an event with a link on the event page. There is no special
permission required to state that you are attending an event.

If an event requires the use of some resource (which could be a
classroom, or maybe its a class on using the lathe), it is possible to
reserve the use of a resource by adding it to the event.


