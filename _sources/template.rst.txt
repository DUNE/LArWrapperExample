Template for minimal metacat for a file
=======================================

Here is an example of minimal metadata for a raw data file.

You can add additional information to the metadata object.

.. code-block:: javascript

  {
      "checksums": {
          "adler32": "0e94618d"
      },
      "created_timestamp": 2018-10-10 17:38:27.681780+00:00,
      "creator": "dunepro",
      "fid": "6607416",  
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
      "name": "np04_raw_run005141_0015_dl3.root",
      "namespace": "protodune-sp",
  }
