# -*- coding: utf-8 -*- 
#中文支持
import os
from ioAnalyzer import *
from math import log
from random import randint

ADDR_RE = '\[[a-z0-9]{8}\]'


def generate_graph( data ):
    fp = open( "../data/kscope.dot", 'w' )
    fp.write("graph kscope {\n")

    p = re.compile( ADDR_RE )
    for t in data:
        s = t.strip("\n")
        addr = s[0:8]
        relatedAddr = p.findall(s)
        if len(relatedAddr) == 1:
            continue
        for item in relatedAddr:
            if "0012fc44" in item or "0012fc54" in item or "0012fc50" in item:
                continue
            if "0012fc70" in item: continue
            fp.write( "\"%s\" -- \"%s\"\n"%(addr, item) )
    fp.write("}\n")
    fp.close()

    os.system("sort ../data/kscope.dot > ../data/kscope.tmp")
    os.system("uniq ../data/kscope.tmp ../data/kscope.dot")
    os.system("del ../data/kscope.tmp")

if __name__=="__main__":
    f = open( "../data/depend.log", 'r' )
    data = f.readlines()
    generate_graph( data )
    f.close()



