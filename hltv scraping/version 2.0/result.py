from __future__ import division
import numpy as np
import random

def marco(x):
    arr = np.array(x)
    cumsum = np.cumsum(arr)
    chain = np.array([i/cumsum[-1] for i in cumsum])
    return np.where(chain > random.random())[0][0]

def result(x):
    if len(x) == 3:
        print "#### BO3 ####"
        print "[Win, +1, -1]"
        final = [0,0,0]
        for i in range(20000):
            win = list()
            for i in x:
                win.append(marco(i))
            if sum(win)>1:
                final[0] += 1
            if sum(win[:2])>0:
                final[1] += 1
            if sum(win[:2])>1:
                final[2] += 1
        print [(20000-final[0])/200, (20000-final[2])/200, (20000-final[1])/200]
        print [i/200 for i in final]
            
