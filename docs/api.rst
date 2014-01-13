API Documentation
========================

Spiff has had two separate APIs over its lifetime, a versioned cherrypy powered
one, and a hacked together homebrew one.

All active development continues on the versioned API, while the deprecated one
is scheduled for removal before the first full release. It is documented here
for posterity, as there already exist a number of experimental deployments.

REST API
--------

Documentation is forthcoming. Check out /v1/?format=json in your browser for
some hints.

General purpose information about the space is available by fetching
/status.json, as per the :doc:`spaceapi`.

.. toctree::
   :glob:

   spaceapi

Deprecated REST API
------------

Spiff's versioned API addresses a number of shortfalls in the previous API:

- It was a bear to maintain
- Didn't implement a number of important features, such as result pagination 
- POSTing updates had limited authentication control

Just about everything in Spiff is accessible through REST. It is as easy
as adding .json to the end of your URLs:

$ http://example.com/sensors/1.json curl
http://localhost:8000/sensors/1.json { "description": "A list of devices
in the space", "name": "pamela", "value": { "stamp":
"2012-10-31T15:28:53.901053+00:00", "sensor": "#Sensor#1", "id": 6,
"value": "{'test': true}" }, "id": 1

Due to the cyclic nature of the database, some values are references to
other objects. This is indicated by the syntax "#Type#ID", such as
"#Sensor#1".

Other serialization formats may be added later if there is enough
demand.

REST documentation pages
````````````````````````
.. toctree::
   :glob:
  
   oldapi/*
