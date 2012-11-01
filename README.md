# Spaceman Spiff Manages Spaces

Spiff is a Django application that helps you manage a hackerspace.

# Dependencies

* Django 1.4
* south
* django-gravatar

## Features

* Track member dues to see who is paid for the month
* Multiple ranks with independent monthly dues
* Keep track of space resources and metadata associated with each resource
* Generate QR codes to stick on things that link to Resource pages
* Create arbitrary membership fields with visibility settings such as "Door Keycode"
  (editing/viewing limited to officers), "Enjoys Smooth Jazz" (viewing
  limited to members only), or "Nobel Prizes Earned" (public to the internet).
* A simple REST api to access everything

# Installation

1. Create a local_settings.py that contains any values you want to override from
settings.py.

2.  $ ./manage.py syncdb --migrate

3. Go nuts.

The default settings use sqlite3 as the database, with
/path/to/spiff/spiff.sqlite3 as the file.

## Apache

This section is included as an example to get Spiff and Apache to work together
in harmony. It is more or less exactly how we run things at synhak.org

First, decide where you're going to serve up spiff. Keep in mind: this URL
should probably never ever ever change in your space's lifetime. QR codes,
hardware sensors, door swipes, and whatever else you have talking to Spiff will
need reconfigured if things ever move. We run our instance at
http://synhak.org/auth/

Our git clone of Spiff is located in /usr/share/spiff/.

  $ git clone git://github.com/SYNHAK/spiff.git /usr/share/spiff/
  $ cd /usr/share/spiff/
    _Configure your local_settings.py here_
  $ ./manage.py syncdb --migrate

In /etc/httpd/conf.d/synhak.org.conf:

    <VirtualHost *:80>
      LoadModule wsgi_module modules/mod_wsgi.so
      WSGIScriptAliasMatch ^/auth(/([^~].*)?)$ /usr/share/spiff/spiff/wsgi.py$1
      Alias /auth/static /usr/share/spiff/spiff/static
      WSGIPassAuthorization On
      WSGIDaemonProcess spiff-1 user=apache group=apache threads=25
      WSGIProcessGroup spiff-1
    </VirtualHost>

That is all you need. You may then access spiff at http://your-space.org/auth/

# Usage

## Resources

In every hackerspace, theres a bunch of equipment sitting around that not
everyone might know how to use or even what it is called. Spiff solves that
problem.

You can create a Resource object in Spiff for each real-world resource. After it
is created, metadata can be attached to it and edited by users with the correct
permissions. Members can also keep track of their training on the site. It works
on an honor system that requires users undergo a vetting process by other users:

* Your hackerspace acquires a nice new lathe.
* A member adds the lathe to the database, prints out the QR code and sticks it
  on the machine.
* Another member who happens to be a master metalworker sees that there is a Lathe,
  scans the code (or visits the resource page) and clicks "I have used this!" to
  indicate that they have used a Lathe at some point in their life.
* A second member (who is a total newbie to metalworking) also clicks "I have used
  this!". Spiff says that both the newbie and the master are ranked at the same
  skill level, so they click "They are better than me".
* Spiff now indicates that the master is better trained at the lathe than the
  newbie and sorts them accordingly.

At no point can the newbie say that they are better than the master without the
master explicitly promoting the newbie to their level. Additionally, the newbie
can't demote the master. Members are ranked relative to each other based on this
feedback system.

Not all resources in a hackerspace are trainable! For instance, it makes no
sense to say that someone is more skilled at using the classroom or meeting
area. When creating a resource, you can specify if a resource can be trainable
or not.

## Membership

Spiff provides a basic system for managing members.

Each member has a few basic fields that should be filled out:

* Email
* First Name
* Last Name
* Birthday
* Profession

These fields are public to the general internet.

Administrators can add extra fields such as phone number, mailing address,
emergency contact information, etc. These extra fields have three flags
available:

* Required - The profile will not save and a user can't register without this
  field being filled out.
* Public - Other members can read the field, but not the entire internet.
  Members can edit their own public fields. Fields that are not public can still
  be read by those with the proper permission.
* Protected - Only those with the proper permission can view and edit the field.
  Members can read the value of their own protected fields, but can't edit them.

## Events

Spiff also allows for tracking of events. Anyone with a proper permission can
create an event (and later edit it). Members can easily RSVP for an event with a
link on the event page. There is no special permission required to state that
you are attending an event.

If an event requires the use of some resource (which could be a classroom, or
maybe its a class on using the lathe), it is possible to reserve the use of a
resource by adding it to the event.

# Permissions

Spiff has a small set of permissions that say who can do what on the site.

It is recommended to create a general purpose "Active Member" group to keep
track of who is and isn't a member and to provide a base set of permissions that
apply to all members. Afterwards, you can create new groups for
each membership level in your hackerspace.

### membership.can_view_private_fields

The user can view any field that does not have the Public flag set.

### membership.can_edit_protected_fields

The user can edit and view profile fields that are protected.

### auth.can_change_user

The user can edit the profiles of other users.

### inventory.can_change_resource

The user can add and modify resource metadata. can_add_metadata,
can_change_metadata, etc are not used at all in Spiff.

### inventory.can_train

The user can promote other users' trainings and add themselves to a resource at
the lowest level.

### events.can_add_event

The user can create events and edit their own events.

### events.can_reserve_resource

The user can attach resources to their own events.

### events.can_change_event

The user can edit other user's events. This is required for being able to attach
resources to events that they don't own.

## Sensors

Spiff is intended to be the central brain of a hackerspace. As such, it includes
functionality for tracking various sensors in the space.

There are five basic types of sensors:

* number
* string
* binary
* json
* temp
* boolean

The type of sensor is just a hint to tell API users how to display the data if
the exact purpose of the sensor is unknown. For example, the spiff web UI will
show a history graph for number sensors. The sensor types adhere to the SpaceAPI
standard: http://hackerspaces.nl/spaceapi/

To update a sensor, send a POST request to the sensor's page (i.e. /sensors/1)
with a single 'data' parameter containing the new sensor data:

  $ curl --data "data={'test': true}" http://example.com/sensors/1

The data can be anything: an image, a number, a basic string that says "Hello!", more strutured JSON data,
or whatever else you want to put in there. Spiff doesn't care, it just stores
the data until someone else wants it.

### Pamela

Pamela is described as a "very cool way to visualize any kind of data". You can
find it at http://www.hackerspace.be/Pamela

Spiff is totally 100% compatible with Pamela's basic API.

To use pamela's ARP scanner with Spiff:

  $ ./pamela/scanner/pamela-scanner.sh -i "eth0" -o "http://example.com/sensors/1"  -t mac.csv -d "/var/lib/dhcpd/dhcpd.leases"

Please see Pamela's documentation for more details.

# REST API

Just about everything in Spiff is accessible through REST. It is as easy as
adding .json to the end of your URLs:

  $ http://example.com/sensors/1.json
  curl http://localhost:8000/sensors/1.json
  {
   "description": "A list of devices in the space", 
   "name": "pamela", 
   "value": {
    "stamp": "2012-10-31T15:28:53.901053+00:00", 
    "sensor": "#Sensor#1", 
    "id": 6, 
    "value": "{'test': true}"
   }, 
   "id": 1

Due to the cyclic nature of the database, some values are references to other objects. This is indicated by the syntax
"#Type#ID", such as "#Sensor#1".

Other serialization formats may be added later if there is enough demand.

# SpaceAPI

Spiff currently implements version 0.12 of the SpaceAPI. You can read more about
it at http://hackerspaces.nl/spaceapi/

You may access the SpaceAPI through /status.json, as per the standard.

Future versions of Spiff will permit more customization of the data in the API.
