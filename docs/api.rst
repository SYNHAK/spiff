API Documentation
========================

REST API
--------


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

General purpose information about the space is available by fetching
/status.json, as per the :doc:`spaceapi`.

REST documentation pages
````````````````````````
.. toctree::
   :glob:
  
   spaceapi
   api/*
