from __future__ import division
import numpy as np
import random
from bs4 import BeautifulSoup
import requests
import re
from data_functions_v3 import get_player_ids
from bisect import bisect_left

def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

def marco(x):
    arr = np.array(x)
    cumsum = np.cumsum(arr)
    chain = np.array([i/cumsum[-1] for i in cumsum])
    return np.where(chain > random.random())[0][0]

def get_players(players):
    return get_player_ids(players)

def upcoming_matches():
        matches = list()
        r = requests.get('http://www.hltv.org/')
        soup = BeautifulSoup(r.text, 'html.parser')
        div = soup.find("li", {"id" : "boc1"})
        links = div.findAll('a')
        for i in links[1:-1]:
            url = 'http://www.hltv.org' + i['href']
            matches.append( url.split('-')[0].split('/')[-1] )       
        return matches
    
def getinfo(url):
    r = requests.get(url)
    maps = list()
    teamnames = list()
    soup = BeautifulSoup(r.text, 'html.parser')
    
    div = soup.find_all("div", {"class" : "hotmatchbox"})
    
    for i in div:
        links = i.findAll('a')
        for a in links:
            if "demoid" in a['href']:
                demoid = a['href']
            if "player" in a['href']:
                teamnames.append( a.text.lower() )

    img = soup.findAll('img', {'src':re.compile('hotmatch')})
    for i in img:
        try:
            maps.append(str(i['src'])[40:-4].title())
        except:
            continue

    return teamnames[:5], teamnames[5:], maps

def pistolround(CT, T):
    plant, defuse = 0, 0
    winner = marco( [CT.pistols('CT'), T.pistols('T')] )
    if winner:
        winner = 'T'
        if not marco( [T.pistolplant(), 1] ):
            plant = 1
    elif not winner:
        winner = 'CT'
        if not marco( [T.pistolplant(), 1] ):
            plant, defuse = 1, 1
    return winner, plant, defuse

    
def halftime(sides):
    sides = [sides[1], sides[0]]
    money = [500, 500]
    lose = [0, 0]
    return sides, money, lose, ['pistol', 'pistol']

def overtime(sides, number):
    money = [10000, 10000]
    lose = [0, 0]
    if number != 30:
        sides = [sides[1], sides[0]]
    return sides, money, lose

def get_buy(dat, money, lose, rn, oppwin):
    
    data = dat[0]
    moneyspent = dat[1]
    value = data[moneyspent.index(takeClosest(moneyspent, money))][2]
    
    #Force buy if it's last round
    if value < 8000 and rn == 14:
        value = money
    elif value < 8000 and rn < 29 and oppwin == 15:
        value = money
        
    if value < 8000:
        equip = 'eco'
    elif value < 18000:
        equip = 'force'
    else:
        equip = 'full'
        
##    if lose == 0 and equip == 'force' and (rn == 1 or rn == 16):
##        equip = 'full'
    
    return equip, money-value

def next_round(cts, ts, winner, sides, money, lose, plant, equip, wins):
    CT, T = sides.index('CT'), sides.index('T')
    #Kills gives a little, 200?
    money[CT] += 200*(5-ts)
    money[T] += 200*(5-cts)
    if winner == 'CT':
        if 'full' in equip:
            money[CT] += 4100*cts
        elif equip[CT] == 'force':
            money[CT] += 1700*cts
        
        if plant:
            money[CT] += 3500*5
            money[T] += ((lose[T]*500)+2200) *5
        else:
            money[CT] += 3250*5
            money[T] += ((lose[T]*500)+1400) *5

        wins[CT] += 1
        lose[CT] = 0
        if lose[T] < 5:
            lose[T] += 1
        
    elif winner == 'T':
        if 'full' in equip:
            money[T] += 3700*ts
            money[CT] += 4100*cts
        elif equip[T] == 'force':
            money[T] += 1700*ts
            
        if plant:
            money[T] += 3500*5
            money[CT] += ((lose[CT]*500)+1400) *5
        else:
            money[T] += 3250*5
            money[CT] += ((lose[CT]*500)+1400) *5
            
        wins[ T ] += 1
        lose[ T ] = 0
        if lose[ CT ] < 5:
            lose[ CT ] += 1
        
    return wins, lose, money
