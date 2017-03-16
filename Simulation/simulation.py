from random import shuffle
from teamclass import team
from sim_functions_v2 import *
from data_functions_v3 import get_common_opp, hmm_seq
import sqlite3
import datetime
import sys
import errno
import traceback
from time import sleep
import numpy as np
from hmmlearn import hmm
conn2 = sqlite3.connect('csgobets.db')
np.random.seed(42)

def here(id):
    cur = conn2.execute("SELECT * FROM simulation WHERE match_id == "+str(id)+"")
    res = cur.fetchall()
    return len(res) > 0
    
def run():
    maps = ['dust2', 'nuke', 'cache', 'cbble', 'mirage', 'overpass', 'train']  
    for match in upcoming_matches():
        if here(match):
            continue
        cur = conn2.execute("SELECT * FROM matches WHERE match_id = "+str(match))
        res = cur.fetchall()
        for i in res:
            print match
            if i[14] == 'tba':
                for mapp in maps:
                    winrate = run_simulation(mapp, i[4:9], i[9:14])
                    insert_simulation(match, mapp, i[2], winrate[0])
                    insert_simulation(match, mapp, i[3], winrate[1])
            else:
                for mapp in [x for x in i[14:21] if x != 'tba']:
                    winrate = run_simulation(mapp, i[4:9], i[9:14])
                    insert_simulation(match, mapp, i[2], winrate[0])
                    insert_simulation(match, mapp, i[3], winrate[1])
            insert_total(match, i[2])
            insert_total(match, i[3])

            #Insert all v3
            print "v3 TIME!"
            winrate = run_simulation('all', i[4:9], i[9:14], True)
            insert_simulation(match, 'all2', i[2], winrate[0])
            insert_simulation(match, 'all2', i[3], winrate[1])

def insert_total(match, t1):
    cur = conn2.execute("SELECT win FROM simulation WHERE match_id = %s AND team = '%s'" % (str(match), t1))
    N = sorted([x[0] for x in cur.fetchall()])
    insert_simulation(match, 'all', t1, round( sum(N[2:5])/3, 2 ))
    
def insert_simulation(match, mapp, team, win):
    conn2.execute("INSERT OR IGNORE INTO simulation VALUES("+match+", '"+mapp+"', '"+team+"', "+str(win)+")")
    conn2.commit()

def complete_sim(team1, team2, date):
    so = shared_opp(team1, team2, date)
    percent = [0, 0]
    for i in range(len(so)):
        t1 = run_simulation('all', team1, so[i], True, date)
        t2 = run_simulation('all', team2, so[i], True, date)
        if t1 != [0, 0] and t2 != [0, 0]:
            percent[0] += t1[0]
            percent[1] += t2[0]
    return [i/sum(percent) for i in percent]

def shared_opp(team1, team2, date):
    team1_opp = get_common_opp(team1, date)
    team2_opp = get_common_opp(team2, date)

    for t in [team1_opp, team2_opp]:
        same = list()
        for i in range(len(t)):
            for a in range(i+1, len(t)):
                if len(set(t[i]) & set(t[a])) > 2:
                    same.append(t[a])
        if t == team1_opp:
            t1_opp = [x for x in t if x not in same]
        else:
            t2_opp = [x for x in t if x not in same]
        
    shared = list()
    for i in t1_opp:
        for a in t2_opp:
            if len(set(i) & set(a)) > 2:
                shared.append(i)
                break
            
    return shared

def run_simulation(mapp, team1, team2, v3, date):
    team1_common_opp = get_common_opp(team1, date)
    team2_common_opp = get_common_opp(team2, date)

    try:
        team1 = team(team1, team2_common_opp, mapp, v3, date)
        team2 = team(team2, team1_common_opp, mapp, v3, date)
    except Exception:
        return [0, 0]

    score = [0.0, 0.0]
    simulations = 20000
    for sim in range(simulations):
        wins = [0,0]
        teams = [team1, team2]
        sides = ['CT', 'T']
        bomsites = ['A', 'B']
        shuffle(sides)

        #Start gamesim
        for roundnumber in range(100):
             
            plant, defuse = 0, 0
            #Game over
            if max(wins) == 16 and roundnumber < 30:
                break
            elif roundnumber > 30 and max(wins) > min(wins)+3:
                break
            #Overtime
            if roundnumber > 29 and roundnumber % 6 == 0:
                if wins[0] == wins[1]:
                    sides, money, lose = overtime(sides, roundnumber)
                else:
                    break
            
            #Halftime
            if roundnumber == 0 or roundnumber == 15:
                sides, money, lose, equip = halftime(sides)
            else:
                equip[0], money[0] = get_buy( team1.get_model(sides[0], lose[0]), money[0], lose[0], roundnumber, wins[1] )
                equip[1], money[1] = get_buy( team2.get_model(sides[1], lose[1]), money[1], lose[1], roundnumber, wins[0] )
            
            CT, T = teams[ sides.index('CT') ], teams[ sides.index('T') ]
            ct_equip, t_equip = equip[ sides.index('CT') ], equip[ sides.index('T') ]

            if equip[0] == 'pistol':
                winner, plant, defuse = pistolround(CT, T)
            else:
                site = bomsites[ marco(T.get_bombsite()) ]
                if marco( [T.t_take(site, t_equip), CT.ct_hold(site, ct_equip)] ):
                    winner = 'CT'
                elif marco( [T.t_hold(site, t_equip), CT.ct_retake(site, ct_equip)] ):
                    winner = 'CT'
                    plant, defuse = 1, 1
                else:
                    winner = 'T'
                    plant = 1

            if equip[0] == 'pistol':
                CT.pistolpoints('CT')
                T.pistolpoints('T')
            else:
                CT.points(site, ct_equip, 'CT')
                T.points(site, t_equip, 'T')
                
            CT.teamscores(winner=='CT', plant, defuse, 'CT')
            T.teamscores(winner=='T', plant, defuse, 'T')
            
            wins, lose, money = next_round( marco( CT.survival('CT', ct_equip, winner=='CT') ),
                                            marco( T.survival('T', t_equip, winner=='T') ),
                                           winner, sides, money, lose, plant, equip, wins)

        score[ wins.index(max(wins)) ] += 1
        
    return [round(i/simulations,4) for i in score]

def hidden_markov(team1, team2, date):
    seq1 = hmm(team1, team2, date)
    seq2 = hmm(team2, team1, date)

def create_model(team1, team2, date):
    sequences = hmm_seq(team1, team2, date)
    if len(sequences) < 2:
        print "Not Enough Data", team1, team2
        return 0
    lengths = [len(m) for m in sequences]
    X = [[i] for i in [item for sublist in sequences for item in sublist]]
    model = hmm.GaussianHMM(n_components=2, covariance_type="tied")
    model.fit(X, lengths)
    return model, X, lengths

def hmm_sim(team1, team2, date):
    model_1, X1, L1 = create_model(team1, team2, date)
    model_2, X2, L2 = create_model(team2, team1, date)
    high_score, high_team = 0, 0
    for n in range(5000):
        seq = list()
        for i in range(31):
            seq.append([random.randint(0, 1)])
            if seq.count([0]) > 15 or seq.count([1]) > 15:
                break

        rev = [[0] if i == [1] else [1] for i in seq]
        score = model_1.score(X1 + seq, L1 + [len(seq)]) + model_2.score(X2 + rev, L2 + [len(rev)])
        if score > high_score:
            high_score = score
            high_team = rev[-1][0]
    return high_team

if __name__ == '__main__':
    print hmm_sim((1,2,3,4,5), (1,2,3,4,5), "2018-12-22")

    
