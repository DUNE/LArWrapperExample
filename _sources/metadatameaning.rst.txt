Metadata categories
===================

Samweb and metacat turn out to need quite a lot of information to describe a file.

There are

* there are core information about the file such as run_number, data tier, and trigger stream that are needed to define data samples.  Most of these are now in the core category in metacat.  If it is a core item, you probably should be filling it.
* data that is useful to know - provenance (what was it created from, how, who did it)

* additional information that may be specific to a given physics group or extra details on reconstruction/simulation parameters.

Both sam and metacat put the more detailed information in objects with <type>.<subtype> format.

.. csv-table:: metacat equivalents for sam fields
   :file: conversion.csv
   :widths: 30,30,40
   :header-rows: 1
