Resources
~~~~~~~~~

* /resources/.json

  Returns a list of all resources

* /resources/{id}.json

  Returns data for the specific resource.

* /resources/{id}/meta

  .. autofunction:: spiff.inventory.views.addMeta

  Parameters:

  * name - The name of the metadata value
  * value - The value
  * type - The type of metadata.

    .. autodata:: spiff.inventory.models.META_TYPES

* /resources/{id}/train

  .. autofunction:: spiff.inventory.views.train

* /resources/{id}/promote

  .. autofunction:: spiff.inventory.views.promoteTraining
