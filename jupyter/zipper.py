import os
import sys

import tarfile
import gzip
import shutil



filemax = 1000000



def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def compress_dir(dir,newpath):
    if not os.path.exists(dir):
        print dir, "is not a file or directory"
    
    else:
        print "look at ",dir
        tarname = os.path.join(newpath+".tar.gz")
        print " archive name is ", tarname
        archive = tarfile.open(tarname,mode='w:gz')
        
        handled = []
        thepath = dir
        print " the path = ", thepath
        for it in os.listdir(dir):
            fullpath = os.path.join(thepath,it)
            #print "look at ",fullpath," in ",dir
            if fullpath in handled:
                continue
            if os.path.isdir(fullpath):
                result = compress_dir(fullpath,os.path.join(newpath,it))
                print " result is ", result
                if get_size(result) < filemax:
                    archive.add(result)
                else:
                    print " copy ",result," to ", newpath
                    shutil.copyfile(result,newpath)
                    handled.append(fullpath)
            else:
                if get_size(it) < filemax:
                    print " add ",it
                    archive.add(fullpath)
                else:
                    apath = os.join(newpath,it,".gz")
                    f = gzip.open(apath,'wb')
                    f.write(it)
                    #print " copy ",fullpath," to ", newpath
                    #shutil.copyfile(fullpath+".gz",newpath)
                    handled.append(fullpath)
    return tarname

inputdir = "/Users/schellmh/compress"
outputdir = "/Users/schellmh/newcompress"

compress_dir(inputdir,outputdir)


