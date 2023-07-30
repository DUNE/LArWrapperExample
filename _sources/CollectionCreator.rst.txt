CollectionCreator
=================

Description
-----------

CollectionCreator is a python script that takes a json specification for a dataset and makes both metacat datasets and sam definitions from it.

The query to create the dataset is the and of the keys in the json file, with some additional qualifiers.  They include the ability to add selections on the time range for the files and the addition of a tag so that you can version your datasets (for example as the Creator code changes).

samweb definitions are created with a name generated from the flags given in the json and command line.  They grow automatically as new fields meet the query criteria.

metacat datasets are created but do not grow unless you rerun the CollectionCreator code with the same json file and deftag arguments. [need to add an option that takes the dataset name and grows that from its stored query.]

metacat datasets also contain the query used to make them and a metadata field that contains the items used to make the dataset query. 

CollectionCreator arguments
---------------------------

.. code-block:: bash

    python python/CollectionCreator.py --help
    usage: CollectionCreator.py [-h] [--namespace NAMESPACE] [--time_var TIME_VAR]
                                [--min_time MIN_TIME] [--max_time MAX_TIME]
                                [--user USER] [--ordered [ORDERED]]
                                [--limit LIMIT] [--skip SKIP] [--json JSON]
                                [--test [TEST]]

    optional arguments:
    -h, --help            show this help message and exit
    --namespace NAMESPACE
                            metacat namespace for dataset
    --time_var TIME_VAR   creation time to select ['created'] or 'raw']
    --min_time MIN_TIME   min time range (inclusive) YYYY-MM-DD UTC
    --max_time MAX_TIME   end time range (inclusive) YYYY-MM-DD UTC
    --user USER           user name
    --ordered [ORDERED]   return list ordered for reproducibility
    --limit LIMIT         limit on # to return
    --skip SKIP           skip N files
    --json JSON           filename for a json list of parameters to and
    --deftag DEFTAG       tag to distinguish different runs of this script, default is test
    --test [TEST]         do in test mode

Example configuration file
--------------------------

Example dataset configuration json files are in directory datasets and look like:

.. code-block:: json

    {
            "core.application.version": "v09_75_03d00",
            "core.data_tier": "hit-reconstructed",
            "core.file_type": "mc",
            "core.run_type": "fardet-hd",
            "dune.campaign": "fd_mc_2023a",
            "dune.requestid": "ritm1780305",
            "dune_mc.beam_polarity": "fhc",
            "dune_mc.gen_fcl_filename": "prodgenie_nutau_dune10kt_1x2x6.fcl"
    }


Making datasets
---------------

    a good way to make a dataset specification is to 

    - take metacat metadata from a file

    - strip out the selections that are not common to all files in the dataset

    - store in a datasets directory

    - run CollectionCreator as above

    - the deftag argument allows you to test/make new versions

The command 

.. code-block::
    
        python python/CollectionCreator.py --json=datasets/fd_mc_2023a_prodgenie_nutau_dune10kt_1x2x6.json --deftag=v0

made a metacat dataset called:

`schellma:fardet-hd__fd_mc_2023a__mc__hit-reconstructed__prodgenie_nutau_dune10kt_1x2x6.fcl__v09_75_03d00__v0`

which you can find at:

https://metacat.fnal.gov:9443/dune_meta_prod/app/gui/dataset?namespace=schellma&name=fardet-hd__fd_mc_2023a__mc__hit-reconstructed__prodgenie_nutau_dune10kt_1x2x6.fcl__v09_75_03d00__v0

