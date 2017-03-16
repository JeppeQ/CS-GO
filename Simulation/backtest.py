import sqlite3
from datetime import datetime, timedelta
from simulation import complete_sim, run_simulation, hmm_sim
import traceback
statsdb = sqlite3.connect('csgostats.db')
oddsdb = sqlite3.connect('C:/Users/QQ/Dropbox/Fantasy League/esportodds.db')
oddsportal = sqlite3.connect('C:/Users/QQ/Dropbox/csgo stats/Odds/oddsportal.db')
ranks = sqlite3.connect('rating.db')
pinnacle = sqlite3.connect('pinnacleodds.db')

def get_winner(match):
    sm = statsdb.execute("SELECT map, team_won, number FROM Round WHERE match_id = %s" % (str(match))).fetchall()
    maps = list(set( [i[0] for i in sm] ) )
    maxes = [max([i[2] for i in sm if i[0] == m]) for m in maps]
    winners = [ [i[1] for i in sm if i[0] == maps[x] and i[2] == maxes[x]][0] for x in range(len(maps))]
    teams = list(set(winners))
    if len(teams) < 1:
        return 0
    elif len(teams) < 2:
        return teams[0]
    elif teams.count(teams[0]) > teams.count(teams[1]):
        return teams[0]
    elif teams.count(teams[0]) < teams.count(teams[1]):
        return teams[1]
    else:
        return 0
    
def profit(win, odds):
        if float(odds)*float(win) > 1.2:
            return 1
        else:
            return 0

def test_all_system():
    money = 0
    betcount = 0
    won = 0
    count = 0
    allodds = pinnacle.execute("SELECT * FROM csgo").fetchall()
    for i in allodds:
        if (float(i[4])-1)*(float(i[5])-1) > 1:
            continue
        i = list(i)
        if i[2] == 'Virtus Pro':
            i[2] = 'Virtus.Pro'
        elif i[3] == 'Virtus Pro':
            i[3] = 'Virtus.Pro'
            
        times = [ (datetime.strptime(i[1], '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10], (datetime.strptime(i[1], '%Y-%m-%d')+timedelta(days=1)).isoformat()[:10] ]
        matches = statsdb.execute("SELECT * FROM Match WHERE date = '%s'" % (i[1]))
        for match in matches:
            team1 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[2]))).fetchone()[0]
            team2 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[3]))).fetchone()[0]
            if set([team1.lower(), team2.lower()]) == set([i[2].lower(), i[3].lower()]):
                if team1.lower() == i[2].lower():
                    team1 = match[6:11]
                    team2 = match[11:16]
                else:
                    team1 = match[11:16]
                    team2 = match[6:11]
                
                winner = get_winner(match[0])
                if winner:
                    try:
                        winrate = run_simulation('all', team1, team2, True, i[1])
                    except Exception:
                        traceback.print_exc()
                        continue
                    
                    if winrate[0] != 0:
                        try:
                            print i[2], get_players(team1), winrate[0], i[4]
                            print i[3], get_players(team2), winrate[1], i[5]
                        except:
                            pass
                        
                    if profit(winrate[0], i[4]):
                        betcount += 1
                        money -= 200
                        if winner == match[2]:
                            won += 1
                            money += 200*float(i[4])
                    elif profit(winrate[1], i[5]):
                        betcount += 1
                        money -= 200
                        if winner == match[3]:
                            won += 1
                            money += 200*float(i[5])
                        
                break
                
        print betcount, money
    print float(money)/(betcount*200)

def get_players(players):
    pl = list()
    for p in players:
        pl.append( statsdb.execute("SELECT alias FROM Player WHERE player_id = %s" % (p)).fetchone()[0] )
    return pl
    
def test_odds_portal():
    money = 0
    betcount = 0
    won = 0
    count = 0
    allodds = oddsportal.execute("SELECT * FROM csgo").fetchall()
    for i in allodds:
        if (float(i[3])-1)*(float(i[4])-1) > 1:
            continue
        times = [ (datetime.strptime(i[0], '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10], (datetime.strptime(i[0], '%Y-%m-%d')+timedelta(days=10)).isoformat()[:10] ]
        matches = statsdb.execute("SELECT * FROM Match WHERE date BETWEEN '%s' AND '%s'" % (times[0], times[1]))
        for match in matches:
            team1 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[2]))).fetchone()[0]
            team2 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[3]))).fetchone()[0]
            if set([team1.lower(), team2.lower()]) == set([i[1].lower(), i[2].lower()]):
                if team1 == i[1]:
                    team1 = match[6:11]
                    team2 = match[11:16]
                else:
                    team1 = match[11:16]
                    team2 = match[6:11]

                    try:
                        winner = hmm_sim(team1, team2, i[0])
                    except:
                        break

                    print "Winner:", i[5]
                    print i[1], get_players(team1), i[3]
                    print i[2], get_players(team2), i[4]

                    if (winner==0 and float(i[3]) < 1.3) or (winner==1 and float(i[4])<1.3):
                        break

                    betcount += 1
                    money -= 200
                    if winner==0 and i[5]==1:
                        won += 1
                        money += 200*float(i[3])
                    elif winner==1 and i[5]==2:
                        won += 1
                        money += 200*float(i[4])


                #     try:
                #         winrate = run_simulation('all', team1, team2, True, i[0])
                #     except Exception:
                #         continue
                #
                #     if i[5] == 3:
                #         winrate[0] = winrate[0]**2*(2*winrate[1]+1)
                #         winrate[1] = winrate[1]**2*(2*winrate[0]+1)
                #     elif i[5] == 5:
                #         winrate[0] = winrate[0]**3*(6*winrate[1]**2+3*winrate[1]+1)
                #         winrate[1] = winrate[1]**3*(6*winrate[0]**2+3*winrate[0]+1)
                #
                #     if winrate[0] != 0:
                #         try:
                #             print team1, team2, i[0]
                #             print i[1], get_players(team1), winrate[0], i[3]
                #             print i[2], get_players(team2), winrate[1], i[4]
                #         except:
                #             pass
                #
                #     if profit(winrate[0], i[3]):
                #         betcount += 1
                #         money -= 200
                #         if i[5] == 1:
                #             won += 1
                #             money += 200*float(i[3])
                #     elif profit(winrate[1], i[4]):
                #         betcount += 1
                #         money -= 200
                #         if i[5] == 2:
                #             won += 1
                #             money += 200*float(i[4])
                #
                break

        print betcount, money
    print float(money)/(betcount*200)

def test_random_stuff():
    money = 0
    betcount = 0
    won = 0
    count = 0
    test = [0, 0, 0, 0]
    allodds = oddsportal.execute("SELECT * FROM csgo").fetchall()
    for i in allodds:
        if (float(i[3])-1)*(float(i[4])-1) > 1:
            continue
        matches = statsdb.execute("SELECT * FROM Match WHERE date = '%s'" % (i[0]))
        money = 0
        current = 0
        for match in matches:
            team1 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[2]))).fetchone()[0]
            team2 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[3]))).fetchone()[0]
            if set([team1.lower(), team2.lower()]) == set([i[1].lower(), i[2].lower()]):
                if money > 0:
                    if (i[3] > i[4] and i[5] == 1) or (i[4] > i[3] and i[5] == 2):
                        test[1] += 1
                        test[2] += current
                        
                if (i[3] > i[4] and i[5] == 1) or (i[4] > i[3] and i[5] == 2):
                    current = 1
                won += 1
                money = 1
                
        
        count += 1
    print won, count, test

def teamrating(team, date):
    rating = 0
    for p in team:
        res = ranks.execute("SELECT rating FROM d%s WHERE player_id = %s" % (date.replace("-", ""), str(p))).fetchone()[0]
        rating += res
    return rating/5.0

def checkplayers(players, date):
    for p in players:
        res = ranks.execute("SELECT games FROM d%s WHERE player_id = %s" % (date.replace("-", ""), str(p))).fetchone()[0]
        if res < 1:
            return 0
    return 1

def test_rating_odds():
    money = 0
    betcount = 0
    won = 0
    count = 0
    allodds = oddsportal.execute("SELECT * FROM csgo").fetchall()
    for i in allodds:
        if (float(i[3])-1)*(float(i[4])-1) > 1:
            continue
        times = [ (datetime.strptime(i[0], '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10], (datetime.strptime(i[0], '%Y-%m-%d')+timedelta(days=1)).isoformat()[:10] ]
        matches = statsdb.execute("SELECT * FROM Match WHERE date BETWEEN '%s' AND '%s'" % (times[0], times[1]))
        for match in matches:
            team1 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[2]))).fetchone()[0]
            team2 = statsdb.execute("SELECT hltv_alias FROM Team WHERE team_id = %s" % (str(match[3]))).fetchone()[0]
            if set([team1.lower(), team2.lower()]) == set([i[1].lower(), i[2].lower()]):
                if not checkplayers(match[6:16], match[1]):
                    continue
                    
                if team1 == i[1]:
                    team1 = match[6:11]
                    team2 = match[11:16]
                else:
                    team1 = match[11:16]
                    team2 = match[6:11]

                t1odds = teamrating(team1, match[1])
                t2odds = teamrating(team2, match[1])

                #print t1odds, t2odds
                #print 0.5+(0.001 * (t1odds-t2odds)), 0.5+(0.001 * (t2odds-t1odds))
                #print i[3], i[4]
                #print "------------------------------------------------------"
                if profit(0.5+(0.0015 * (t1odds-t2odds)), i[3]):
                    betcount += 1
                    money -= 200
                    if i[5] == 1:
                        won += 1
                        money += 200*float(i[3])
                elif profit(0.5+(0.0015 * (t2odds-t1odds)), i[4]):
                    betcount += 1
                    money -= 200
                    if i[5] == 2:
                        won += 1
                        money += 200*float(i[4])

                break
        print money, betcount
    print float(money)/(betcount*200)

def getprev(team, alls, odds1, odds2):
    allodds = oddsportal.execute("SELECT * FROM csgo WHERE team1 = '%s' or team2 = '%s'" % (team, team)).fetchall()
    try:
        m = allodds[ allodds.index(alls)+1 ]
    except:
        return 0

    if odds1 > odds2:
        if ((m[1] == team and m[3] > m[4] and m[5] == 1) or (m[2] == team and m[4] > m[3] and m[5] == 2)):
            return 1
        else:
            return 4
    elif odds1 < odds2:
        if ((m[1] == team and m[3] < m[4] and m[5] == 1) or (m[2] == team and m[4] < m[3] and m[5] == 2)):
            return 2
        else:
            return 3
    else:
        return 0
    
def test_Q_algorithm():
    money = 0
    betcount = 0
    won = 0
    count = 0
    allodds = oddsportal.execute("SELECT * FROM csgo").fetchall()
    for i in allodds:
        if (float(i[3])-1)*(float(i[4])-1) > 1:
            continue
        team1prev = getprev(i[1], i, i[3], i[4]) 
        team2prev = getprev(i[2], i, i[4], i[3])
        if i[3] > i[4] and team1prev == 1 and team2prev in [3, 4]:
            betcount += 1
            money -= 200
            if i[5] == 1:
                won += 1
                money += 200*float(i[3])
        elif i[4] > i[3] and team2prev == 1 and team1prev in [3, 4]:
            betcount += 1
            money -= 200
            if i[5] == 2:
                won += 1
                money += 200*float(i[4])
##        elif i[3] < i[4] and team1prev == 2 and team2prev == 3:
##            betcount += 1
##            money -= 200
##            if i[5] == 1:
##                won += 1
##                money += 200*float(i[3])
##        elif i[4] < i[3] and team2prev == 2 and team1prev == 3:
##            betcount += 1
##            money -= 200
##            if i[5] == 2:
##                won += 1
##                money += 200*float(i[4])
                
        print money, betcount
    print float(money)/(betcount*200)

    
def test_rating_system():
    count, predict = 0, 0
    dato = "2016-09-14"
    times = [ (datetime.strptime(dato, '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10],
              (datetime.strptime(dato, '%Y-%m-%d')-timedelta(days=720)).isoformat()[:10] ]
    cur = statsdb.execute("SELECT * FROM Match WHERE date BETWEEN '"+times[1]+"' AND '"+times[0]+"'")
    res = cur.fetchall()
    for i in res:
        winner = get_winner(i[0])
        if winner and checkplayers(i[6:16], i[1]):
            if teamrating(i[6:11], i[1]) > teamrating(i[11:16], i[1]):
                team = i[2]
            else:
                team = i[3]
            if winner == team:
                predict += 1
            count += 1
            
    return predict, count, predict/float(count)
        
#test_all_system()
test_odds_portal()
#print test_rating_system()
#test_rating_odds()
#test_random_stuff()
#test_Q_algorithm()
