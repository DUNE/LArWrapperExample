Metadata categories and samweb->metacat conversion
--------------------------------------------------

Samweb and metacat turn out to need quite a lot of information to describe a file.

There is

* basic information about the file as a file - size, creation, creator, checksum
* core information about the file  contents such as run_number, data tier, and trigger stream that are needed to define data samples.  Most of these are now in the core category in metacat.  If it is a core item, you probably should be filling it.
* data that is useful to know - provenance (what was it created from, how, who did it)

* additional information that may be specific to a given physics group or extra details on reconstruction/simulation parameters.

:doc:`template` shows a metacat and samweb example for a raw data file

Both sam and metacat put the more detailed information in objects with <type>.<subtype> format.  Metacat extends this to <category>.<sub>.<sub ...>.<name>

Here is a table to convert fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table:: metacat equivalents for sam fields
   :file: conversion.csv
   :widths: 30,30,40
   :header-rows: 1

Here is a table of common command translations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. csv-table:: metacat equivalents for sam commands
   :file: commands.csv
   :widths: 40,40,20
   :header-rows: 1
