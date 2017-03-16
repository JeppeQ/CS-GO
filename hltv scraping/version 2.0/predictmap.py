from __future__ import division
import sqlite3
import heapq
conn = sqlite3.connect('csstats.db')
conn.text_factory = str

def sl(s):
    s = s.split("_")
    return [int(i) for i in s]


def getmaps(team):
    maps = [0 for i in range(7)]
    with conn:
        cur = conn.execute("SELECT picks FROM maps WHERE team = '"+team+"' ORDER BY id DESC LIMIT 30")
        N = cur.fetchall()
    for i in N:
        maps = [x+y for x,y in zip(maps, sl(i[0]))]
    return maps

def get_picks(mp1, mp2, n1, n2, n3 = 1):
    pool = ['Dust2', 'Inferno', 'Cache', 'Cobblestone', 'Overpass', 'Mirage', 'Train']
    picks = list()
    fp = [0, 0, 0, 0, 0, 0, 0]
    for i in range(n3):
        for i in range(7):
            s = heapq.nsmallest(i+1, mp1)[i]
            if fp[mp1.index(s)] == 0:
                fp[mp1.index(s)] = 1
                break
        for i in range(7):
            s = heapq.nsmallest(i+1, mp2)[i]
            if fp[mp2.index(s)] == 0:
                fp[mp2.index(s)] = 1
                break
    for i in range(n1):
        for i in range(7):
            s = heapq.nlargest(i+1, mp1)[i]
            if fp[mp1.index(s)] == 0:
                fp[mp1.index(s)] = 1
                picks.append(pool[mp1.index(s)])
                break
        for i in range(7):
            s = heapq.nlargest(i+1, mp2)[i]
            if fp[mp2.index(s)] == 0:
                fp[mp2.index(s)] = 1
                picks.append(pool[mp2.index(s)])
                break
    for i in range(n2):
        for i in range(7):
            s = heapq.nsmallest(i+1, mp1)[i]
            if fp[mp1.index(s)] == 0:
                fp[mp1.index(s)] = 1
                break
        for i in range(7):
            s = heapq.nsmallest(i+1, mp2)[i]
            if fp[mp2.index(s)] == 0:
                fp[mp2.index(s)] = 1
                break
    if n3 == 1:
        picks.append(pool[fp.index(0)])
    return picks

def predict_map(team1, team2, form):
    mp1 = getmaps(team1)
    mp2 = getmaps(team2)
    if form == 'bo5':
        return get_picks(mp1, mp2, 2, 0)
    elif form == 'bo3':
        return get_picks(mp1, mp2, 1, 1)
    elif form == 'bo2':
        return get_picks(mp1, mp2, 1, 0, 2)
    elif form == 'bo1':
        return get_picks(mp1, mp2, 0, 2)
    
