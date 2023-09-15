CollectionCreatorClass
======================

Replaces CollectionCreator


Description
-----------

`CollectionCreatorClass` is a python script/class that takes a `json` specification for a dataset and makes both metacat datasets and sam definitions from it.

The query to create the dataset is the `AND` of the keys in the json file, with some additional qualifiers.  They include the ability to add selections on the time range  and runs and the addition of a tag so that you can version your datasets (for example as the Creator code changes).

samweb definitions are created with a name generated from the flags given in the json and command line.  They grow automatically as new fields meet the query criteria.

metacat datasets are created but do not grow unless you rerun the `CollectionCreatorClass` code with the `--did` argumennt.  

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
        --json JSON           filename for a json list of parameters to and
        --did DID             <namespace>:<name> for existing dataset to append to
        --test [TEST]         do in test mode

Example configuration files
---------------------------

Example dataset configuration json files are in directory `datasets` and look like:

For simulation
++++++++++++++

`datasets/mctest.json`

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
        "deftag": "testme7"
    }   

For data:
+++++++++

`datasets/pdtest.json`

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
        "deftag":"testme7"
    }

Special tags:
+++++++++++++

- metacat fields with  % in them are normal metacat tags and are anded together to make the query.  

- fields such as `max_time`, `min_time` and `runs` have special metacat syntax so are flagged by the absence of a "." and then interpreted by the script.

- Special dataset tags include a `defname` template that allows you to build the dataset name from fields and a special tag `deftag` to allow multiple versions. 

- There is a `description` tag that allows you to describe your dataset.

- the `defname` field allows you to specify a filename in which keys like `%dune.campaign` are replaced by the value of dune.campaign.  This allows you to avoid messing with defname every time you change a flag.


Making datasets
---------------

    a good way to make a dataset specification is to 

    - take metacat metadata from a file

    - strip out the selections that are not common to all files in the dataset

    - add a description, a name format and a deftag

    - store in new json file 

    - run CollectionCreatorClass 

    - the `--test` argument allows you to test without actually doing anything

The command 

.. code-block::
    
    python -m CollectionCreatorClass --json=datasets/pdtest.json

made a metacat dataset called:

`schellma:detector.protodune-sp.PDSPProd4.full-reconstructed.physics.5141-5143.2021-01-03.2022-10-03.testme7`

which you can find at:

https://metacat.fnal.gov:9443/dune_meta_prod/app/gui/dataset?namespace=schellma&name=schellma:detector.protodune-sp.PDSPProd4.full-reconstructed.physics.5141-5143.2021-01-03.2022-10-03.testme7

.. code-block::

    python -m CollectionCreatorClass --json=datasets/mctest.json

does similar for an mc sample and makes

`schellma:mc.fardet-hd.fd_mc_2023a.v09_75_03d00.hit-reconstructed.prodgenie_nutau_dune10kt_1x2x6.fcl.testme7`

https://metacat.fnal.gov:9443/dune_meta_prod/app/gui/dataset?namespace=schellma&name=mc.fardet-hd.fd_mc_2023a.v09_75_03d00.hit-reconstructed.prodgenie_nutau_dune10kt_1x2x6.fcl.testme7

Adding to datasets
------------------

`metacat` does not grow datasets automatically as `samweb` does, so if you want to add files to a dataset when new files arrive you can reuse the original query using the `--did` argument.  You can NOT do this by either never using the `--did` option or by using a date range in which case files created after a given date will not be added.

.. code-block::
    
    python -m CollectionCreatorClass --did=schellma:detector.protodune-sp.PDSPProd4.full-reconstructed.physics.2021-01-03.2022-10-03.testme7

Using the python API
--------------------

`fd_mc_2023a_create.py` in the `scripts` directory is an example of using the `CollectionCreatorClass` python api instead of the command line. 
   

Inspecting and finding datasets using the dataset metadata you created
----------------------------------------------------------------------



Finding
+++++++

.. code-block:: 

    metacat query datasets matching schellma:* having datasetpar.deftag=testme7

finds all the datasets in namespace `schellma` that have `deftag` `testme7`.  You can search for any of the other parameters. 


Inspecting
++++++++++

.. code-block:: 

    metacat dataset show schellma:mc.fardet-hd.fd_mc_2023a.v09_75_03d00.hit-reconstructed.prodgenie_nutau_dune10kt_1x2x6.fcl.testme7

produces

.. code-block:: 

    Namespace:             schellma
    Name:                  mc.fardet-hd.fd_mc_2023a.v09_75_03d00.hit-reconstructed.prodgenie_nutau_dune10kt_1x2x6.fcl.testme7
    Description:           mc files from fd_mc_2023a
    Creator:               schellma
    Created at:            2023-08-19 22:37:32 UTC
    Estimated file count:  20464 
    Restricted:            no
    Metadata:
    {
        "core.application.version": "v09_75_03d00",
        "core.data_tier": "hit-reconstructed",
        "core.file_type": "mc",
        "core.run_type": "fardet-hd",
        "datasetpar.defname": "%core.file_type%core.run_type%dune.campaign%core.application.version%core.data_tier%dune_mc.gen_fcl_filename%deftag",
        "datasetpar.defnamespace": "schellma",
        "datasetpar.deftag": "testme7",
        "datasetpar.ordered": true,
        "datasetpar.query": "files where core.application.version=v09_75_03d00 and core.data_tier='hit-reconstructed' and core.file_type=mc and core.run_type='fardet-hd' and dune.campaign=fd_mc_2023a and dune.requestid=ritm1780305 and dune_mc.beam_polarity=fhc and dune_mc.gen_fcl_filename=prodgenie_nutau_dune10kt_1x2x6.fcl ordered ",
        "dune.campaign": "fd_mc_2023a",
        "dune.requestid": "ritm1780305",
        "dune_mc.beam_polarity": "fhc",
        "dune_mc.gen_fcl_filename": "prodgenie_nutau_dune10kt_1x2x6.fcl"
    }
    Constraints: