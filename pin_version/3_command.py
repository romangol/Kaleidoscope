# -*- coding: utf-8 -*- 
# 中文支持

import os
from ioAnalyzer import get_threads
os.system("sort ../data/instPool.out > tmp")
os.system("uniq tmp ../data/instPool.out")
os.system("del tmp")


if __name__=="__main__":
    ts = get_threads()
    for t in ts:
        cmd = "findstr \"|[RW]\" ..\\data\\mil"+ str(t) + ".log > ..\\data\\rw"+ str(t) + ".log"
        os.system(cmd)
