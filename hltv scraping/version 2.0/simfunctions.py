from __future__ import division
import numpy as np
import random

def vulcun(stats, side, rt, kills):
    dt = ['pistol', 'eco', 'force', 'full']
    points = [0 for i in range(5)]
    #Kills
    for i in range(len(stats)):
        index = dt.index(rt)*6
        points[i] += marco( stats[i][side][index:index+6] )
    #Headshots
    for i in range(len(stats)):
        index = dt.index(rt)*3 + 2
        hs = stats[i][6+side][index] / stats[i][8][side*4+dt.iindex(rt)]
        for i in range(points[i]):
            if marco( [hs, 1.0] ) == 0:
                points[i] += 0.5
    #Deaths
    if kills < 5:
        index = dt.index(rt)*3 + 1
        points = [x-y for x,y in zip( points, marcosplit([i[6+side][index] / i[8][side*4+dt.index(rt)] for i in stats], kills) )]
    else:
        points = [i-1 for i in points]
    #Assist
    for i in range(len(stats)):
        index = dt.index(rt)*3
        points[i] += marco( [stats[i][6+side][index] / stats[i][8][side*4+dt.index(rt)], 1.0] )
    return points
        

def marcosplit(x, antal):
    A = [0,0,0,0,0]
    for i in range(antal):
        marc = marco( x )
        A[marc] = 1
        x[marc] = 0
    return A
    
def getkills(stats, side, rt):
    dt = ['pistol', 'eco', 'force', 'full']
    pkill = 0
    for i in stats:
        index = dt.index(rt)*6
        pkill += marco( i[side][index:index+6] )
    return pkill

def buy(side, winner, plant, t, money, lose, deaths):
    if money < 0:
        money = 0
    if deaths < 0:
        deaths = 0
    if side == 0:
        if winner == 0:
            lose = 0
            if plant == 0:
                money += 3500*5
            else:
                money += 3250*5
            if t == 'pistol':
                return 'full', 0, lose
            else:
                money -= (4700*5) - (4100*deaths)
                return 'full', money, lose
        elif winner == 1:
            money += (1400 + (500*lose))*5
            lose += 1
            if lose > 4:
                lose = 4
            #if t == 'full':
                #money += 4100*deaths
            if money > 20500:
                money -= 4700*5
                return 'full', money, lose
            elif (money - 1400*5) + (1400+(500*(lose)))*5 > 20500:
                money -= 1400*5
                return 'force', money, lose
            elif money + (1400+(500*(lose)))*5 > 20500:
                return 'eco', money, lose
            else:
                money -= 1400*5
                return 'force', money, lose
    elif side == 1:
        #T-Side
        if winner == 1:
            lose = 0
            if plant == 0:
                money += 3500*5
            else:
                money += 3250*5
            money -= (4300*5)-(3700*deaths)
            if t == 'pistol':
                return 'full', 0, lose
            else:
                return 'full', money, lose
        elif winner == 0:
            money += (1400 + (500*lose))*5
            lose += 1
            if lose > 4:
                lose = 4
            if plant == 0:
                money += 800*5
            if t == 'pistol':
                if plant == 0:
                    return 'eco', money, lose
                else:
                    money -= 1400*5
                    return 'force', money, lose
            if money > 18500:
                money -= 4300*5
                return 'full', money, lose
            elif (money - 1400*5) + (1400+(500*(lose)))*5 > 18500:
                money -= 1400*5
                return 'force', money, lose
            elif money + (1400+(500*(lose)))*5 > 18500:
                return 'eco', money, lose
            else:
                money -= 1400*5
                return 'force', money, lose

def marco(x):
    arr = np.array(x)
    cumsum = np.cumsum(arr)
    chain = np.array([i/cumsum[-1] for i in cumsum])
    return np.where(chain > random.random())[0][0]
