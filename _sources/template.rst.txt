Template for minimal metadata for a file
----------------------------------------

Here is an example of minimal metadata for a raw data file.

You can add additional information to the metadata object.

Metacat version
^^^^^^^^^^^^^^^

.. code-block:: javascript

  {
      "name": "np04_raw_run005141_0015_dl3.root",
      "namespace": "protodune-sp",
      "checksums": {
          "adler32": "0e94618d"
      },
      "created_timestamp": 2018-10-10 17:38:27.681780+00:00,
      "creator": "dunepro",
      "size": 8289321123,
      "metadata": {
          "core.application.family": "art",
          "core.application.name": "dune-artdaq",
          "core.application.version": "v1_16_00b",
          "core.data_stream": "physics",
          "core.data_tier": "raw",
          "core.end_time": "2018-10-10 17:38:27.681780+00:00",
          "core.event_count": 108,
          "core.events": [1,2,3,4],
          "core.file_content_status": "good",
          "core.file_format": "hdf5",
          "core.file_type": "detector",
          "core.first_event_number": 20921,
          "core.last_event_number": 22349,
          "core.run_type": "protodune-sp",
          "core.runs": [
              5141
          ],
          "core.runs_subruns": [
              514100001
          ],
          "core.start_time": "2018-10-10 17:38:27.681780+00:00",
          "core.raw_timestamp": "2018-10-10 17:38:27.681780+00:00",
      },

  }

Additional information
----------------------

  This information allows files to be modified and retired

  .. code-block:: javascript

      {"retired": false,
      "retired_by": null,
      "retired_timestamp": null,
      "size": 8289321123,
      "updated_by": null,
      "updated_timestamp": null
      }

  There is also parentage information available.


Samweb version
^^^^^^^^^^^^^^

.. code-block:: javascript

  {
   "file_name": "filename",
   "file_id": 6607416,
   "create_date": "2018-10-10T17:38:27+00:00",
   "user": "dunepro",
   "file_size": 8289321123,
   "checksum": [ "adler32:0e94618d"],
   "content_status": "good",
   "file_type": "detector",
   "file_format": "root",
   "data_tier": "raw",
   "data_stream": "physics",
   "application": {
      "family": "art",
      "name": "dune-artdaq",
      "version": "v1_16_00b"
   },
   "event_count": 108,
   "first_event": 20921,
   "last_event": 22349,
   "start_time": "2018-10-10T17:25:01+00:00",
   "end_time": "2018-10-10T17:32:16+00:00",
   "runs": [ [ 5141, 1, "protodune-sp" ] ]
  }
