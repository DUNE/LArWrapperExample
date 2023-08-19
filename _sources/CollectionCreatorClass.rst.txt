CollectionCreatorClass
======================

Replaces CollectionCreator


Description
-----------

CollectionCreatorClass is a python script/class that takes a json specification for a dataset and makes both metacat datasets and sam definitions from it.

The query to create the dataset is the and of the keys in the json file, with some additional qualifiers.  They include the ability to add selections on the time range  and runs for the files and the addition of a tag so that you can version your datasets (for example as the Creator code changes).

samweb definitions are created with a name generated from the flags given in the json and command line.  They grow automatically as new fields meet the query criteria.

metacat datasets are created but do not grow unless you rerun the CollectionCreator code with the --did argumennt.  

The `--did` argument pulls the stored query from the pre-existing dataset and adds files matching that query. 

metacat datasets also contain the query used to make them and a metadata field that contains the items used to make the dataset query. 


CollectionCreatorClass arguments
--------------------------------

.. code-block:: bash

    usage: CollectionCreatorClass.py [-h] [--namespace NAMESPACE] [--user USER]
                                 [--ordered [ORDERED]] [--json JSON]
                                 [--did DID] [--test [TEST]]

        optional arguments:
        -h, --help            show this help message and exit
        --namespace NAMESPACE
                            metacat namespace for dataset
        --user USER           user name
        --ordered [ORDERED]   return list ordered for reproducibility
        --json JSON           filename for a json list of parameters to and
        --did DID             <namespace>:<name> for existing dataset to append to
        --test [TEST]         do in test mode

Example configuration file
--------------------------

Example dataset configuration json files are in directory datasets and look like:

For simulation
++++++++++++++

.. code-block:: json

    {
        "description":"mc files for HD",
        "defnamespace":"schellma",
        "defname":"%core.file_type%core.run_type%dune.campaign%core.application.version%core.data_tier%dune_mc.gen_fcl_filename%deftag",
        "core.application.version": "v09_75_03d00",
        "core.data_tier": "hit-reconstructed",
        "core.file_type": "mc",
        "core.run_type": "fardet-hd",
        "dune.campaign": "fd_mc_2023a",
        "dune.requestid": "ritm1780305",
        "dune_mc.beam_polarity": "fhc",
        "dune_mc.gen_fcl_filename": "prodgenie_nutau_dune10kt_1x2x6.fcl",
        "deftag": "testme"
    }   

For data:
+++++++++

.. code-block:: json

    {
        "description":"test of data with runs",
        "defname":"core.file_type%core.run_type%dune.campaign%core.data_tier%core.data_stream%min_time%max_time%deftag",
        "core.run_type": "protodune-sp",
        "core.file_type": "detector",
        "core.data_tier": "full-reconstructed",
        "core.data_stream": "physics",
        "dune.campaign": "PDSPProd4",
        "min_time":"2021-01-03",
        "max_time":"2022-10-03",
        "runs":"5141:5143",
        "deftag":"testme6"
    }

Special tags:
+++++++++++++

- Tags with "." in them are normal metacat tags and are anded together to make the query.  

- Tags such as `max_time`, `min_time` and `runs` have special metacat syntax so are flagged by the absence of a ".". 

- Special dataset tags include a `defname` template that allows you to build the dataset name from fields and a special tag `deftag`,

- There is a `description` tag that allows you to describe your dataset.

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
    
        python python/CollectionCreatorClass.py --json=datasets/fd_mc_2023a_prodgenie_nutau_dune10kt_1x2x6.json --deftag=v0

made a metacat dataset called:

`schellma:fardet-hd__fd_mc_2023a__mc__hit-reconstructed__prodgenie_nutau_dune10kt_1x2x6.fcl__v09_75_03d00__v0`

which you can find at:

https://metacat.fnal.gov:9443/dune_meta_prod/app/gui/dataset?namespace=schellma&name=fardet-hd__fd_mc_2023a__mc__hit-reconstructed__prodgenie_nutau_dune10kt_1x2x6.fcl__v09_75_03d00__v0

