from __future__ import division
import numpy as np
import random
from simfunctions import *
from getstats import getstats
        
        
def simulation(stats):
    dt = ['pistol', 'eco', 'force', 'full']
    score = [0,0]
    sim = 20000
    for i in range(sim):
        wins = [0,0]
        knife = marco([stats[2], stats[3]])
        sides = [1-knife, knife]
        for rounds in range(100):
            if rounds == 14:
                types = ['force' if i == 'eco' else i for i in types]
            if wins[0] == 15 and types[1] == 'eco':
                types[1] = 'force'
            if wins[1] == 15 and types[0] == 'eco':
                types[0] = 'force'
            if max(wins) == 16 and rounds < 30:
                break
            elif rounds == 30:
                sides = [sides[1], sides[0]]
            elif rounds > 30:
                if max(wins) > min(wins)+3:
                    break
            if rounds == 0 or rounds == 15:
                sides = [sides[1], sides[0]]
                types = ['pistol', 'pistol']
                money = [0, 0]
                lose = [0, 0]
            #Overtime
            if rounds > 29 and rounds % 6 == 0:
                if wins[0] == wins[1]:
                    sides = [sides[1], sides[0]]
                    money = [6000, 6000]
                    types = ['full', 'full']
                    lose = [0, 0]
                else:
                    break

            t1 = getkills(stats[0], sides[0], types[0])
            t2 = getkills(stats[1], sides[1], types[1])
            if t1 > t2:
                winner = 0
            elif t2 > t1:
                winner = 1
            else:
                winner = marco( [stats[4][sides[0]*4+dt.index(types[0])],
                              stats[5][sides[1]*4+dt.index(types[1])]] )
            wins[winner] += 1
            #Find buy for next round
            plant = marco( [stats[7-sides[0]][dt.index(types[sides.index(1)])], 1.0] )
            types[0], money[0], lose[0] = buy(sides[0], sides[winner], plant, types[0], money[0], lose[0], 5-t2)
            types[1], money[1], lose[1] = buy(sides[1], sides[winner], plant, types[1], money[1], lose[1], 5-t1)
        score[winner] += 1
    return [round(i/sim,2) for i in score]

###print simulation(getstats ([u'FalleN', u'TACO', u'fer', u'coldzera', u'fnx'],
##                     [u'flusha', u'KRIMZ', u'dennis', u'olofmeister', u'JW']))
##
##           
