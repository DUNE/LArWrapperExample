# template and checks for data collection tags

def DefineCollectionTags():
    CollectionTags = {
        "core.run_type":None,
        "core.file_type":None,
        "core.data_tier":None,
        "core.data_stream":None,
        "inputdataset":None,
        "DUNE.campaign":None,
        "core.application.family":None,
        "core.application.name":None,
        "core.application.version":None,
        "ordered":None,
        "skip":None,
        "limit":None,
        "time_var":None,
        "min_time":None,
        "max_time":None,
        "other":None
    }
    return CollectionTags


# create a mapping from the shortened args to real tags in metacat
def CollectionArgMap (tags):
    argmap={}
    for tag in tags:
        if "core" in tag:
            argmap[tag]=tag.replace("core.","")
            if "core.application" in tag:
                argmap[tag]=tag.split(".")[2]
            continue
        
        if "campaign" in tag:
            argmap[tag]=tag.replace("DUNE.campaign","campaign")
            continue
        argmap[tag]=tag
    print (argmap)
    return argmap
        
