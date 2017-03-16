import sqlite3
import datetime
from datetime import datetime, timedelta
conn = sqlite3.connect('csgostats.db')

def get_matches(p, dato, dayk = 360):
    times = [ (datetime.strptime(dato, '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10],
              (datetime.strptime(dato, '%Y-%m-%d')-timedelta(days=dayk)).isoformat()[:10] ]
    cur = conn.execute("SELECT match_id FROM Match WHERE date BETWEEN '"+times[1]+"' AND '"+times[0]+"' AND \
                       (player1_id == %d OR player2_id == %d OR player3_id == %d OR player4_id == %d OR \
                       player5_id == %d OR player6_id == %d OR player7_id == %d OR player8_id == %d OR \
                       player9_id == %d OR player10_id == %d)" % tuple(p for i in range(10)) ) 
    res = cur.fetchall()
    return [i[0] for i in res]

def get_shared_matches(matches):
    shared_matches = [i for i in matches if matches.count(i) > 2]
    return sorted(list(set(shared_matches)))

def common_matches_v2(matches, common_opp):
    common_matches = list()
    for match in matches:
        cur = conn.execute("SELECT map FROM Round WHERE match_id == " + str(match))
        catch = cur.fetchall()
        if len(catch) > 0:
            cur = conn.execute("SELECT * FROM Match where match_id == " + str(match))
            res = cur.fetchall()[0]
            if True in [len(set(res[6:16]) & set(opp)) > 2 for opp in common_opp]:
                common_matches.append(match)
    if len(common_matches) < 2:
        return 0
    return common_matches

def get_round_seq(team, matches):
    sequences = list()
    for match in matches:
        teamid = get_team_id(team[0], match)
        cur = conn.execute("SELECT DISTINCT map FROM Round WHERE match_id == " + str(match))
        catch = cur.fetchall()
        for map in catch:
            seq = list()
            cur = conn.execute("SELECT * FROM Round WHERE match_id = %s and map='%s'" % (str(match), map[0]))
            for i in cur.fetchall():
                if i[4] == teamid:
                    seq.append(1)
                else:
                    seq.append(0)
            sequences.append( seq )
    return sequences

def hmm_seq(team, opp, date):
    matches = [get_matches(p, date) for p in team]
    matches = get_shared_matches([item for sublist in matches for item in sublist])
    common_opponents = get_common_opp(team, date)
    return get_round_seq(team, common_matches_v2(matches, common_opponents))


def get_player_ids(hltv_ids):
    ids = list()
    for _id in hltv_ids:
        cur = conn.execute("SELECT player_id FROM Player2 WHERE hltv_id = %s" % (str(_id)) )
        ids.append( cur.fetchone()[0] )
    return ids

def get_common_opp(team1, date, dayk = 360):
    times = [ (datetime.strptime(date, '%Y-%m-%d')-timedelta(days=1)).isoformat()[:10],
              (datetime.strptime(date, '%Y-%m-%d')-timedelta(days=dayk)).isoformat()[:10] ]
    
    common_opp = list()
    cur = conn.execute("SELECT match_id FROM Match WHERE date BETWEEN '%s' AND '%s'" % (times[1], times[0]))
    allmatches = cur.fetchall()
    for match in allmatches:
        cur = conn.execute("SELECT * FROM Match where match_id == "+str(match[0]))
        res = cur.fetchall()[0]
        if len(set(team1) & set(res[6:11])) > 2:
            common_opp.append( res[11:16] )
        elif len(set(team1) & set(res[11:16])) > 2:
            common_opp.append( res[6:11] )
    return common_opp
    
def get_common_matches(player, common_opp, days = 180):
    common_matches = list()
    matches = get_matches(player, days)
    for match in matches:
        cur = conn.execute("SELECT map FROM Round WHERE match_id == "+str(match))
        catch = cur.fetchall()
        if len(catch) > 0:
            cur = conn.execute("SELECT * FROM Match where match_id == "+str(match))
            res = cur.fetchall()[0]
            if player in res[6:11]:
                if True in [len(set(res[11:16]) & set(opp)) > 2 for opp in common_opp]:
                    common_matches.append( match )                          
            elif player in res[11:16]:
                if True in [len(set(res[6:11]) & set(opp)) > 2 for opp in common_opp]:
                    common_matches.append( match )

    if len(set(common_matches)) < 2:
        if days < 360:
            return get_common_matches(player, common_opp, days+5)
        else:
            return 0

    return common_matches

def get_team_id(player, match):
    cur = conn.execute("SELECT * FROM Match where match_id == "+str(match))
    res = cur.fetchall()[0]
    if player in res[6:11]:
        return res[2]
    elif player in res[11:16]:
        return res[3]
    
def get_rounds(player, one, two, common_opp):
    rounds = []
    matches = get_common_matches(player, common_opp)
    for match in matches:
        teamid = get_team_id(player, match)
        cur = conn.execute("SELECT * FROM Round WHERE match_id = "+str(match)+" AND \
                            ((team_won = "+str(teamid)+" AND side_won = '"+one+"') OR (team_won != "+str(teamid)+" AND side_won = '"+two+"'))")
        res = cur.fetchall()
        rounds += res
    return rounds

def get_all_rounds(player, one, two):
    rounds = []
    matches = get_matches(player)
    for match in matches:
        teamid = get_team_id(player, match)
        cur = conn.execute("SELECT * FROM Round WHERE match_id = "+str(match)+" AND \
                            ((team_won = "+str(teamid)+" AND side_won = '"+one+"') OR (team_won != "+str(teamid)+" AND side_won = '"+two+"'))")
        res = cur.fetchall()
        rounds += res
    return rounds
                   
def get_weakness(full, force, eco, equip, win, side):
    buys = [ [18000, 8000], [18000, 8000] ]
    if win:
        if equip > buys[side][0]:
            full = [q+1 for q in full]
        elif equip > buys[side][1]:
            force = [q+1 for q in force]
        else:
            eco = [q+1 for q in eco]
    else:
        if equip > buys[side][0]:
            full[1] += 1
        elif equip > buys[side][1]:
            force[1] += 1
        else:
            eco[1] += 1
    return full, force, eco
    
def equip_stat(mapp, targetmap, mapstat_a, mapstat_b, full, force, eco, equip, win, site, side):
    buys = [ [18000, 8000], [18000, 8000] ]
    if win:
        if equip > buys[side][0]:
            full = [q+1 for q in full]
            if mapp == targetmap:
                if site == 'A':
                    mapstat_a = [q+1 for q in mapstat_a]
                elif site == 'B':
                    mapstat_b = [q+1 for q in mapstat_b]
        elif equip > buys[side][1]:
            force = [q+1 for q in force]
        else:
            eco = [q+1 for q in eco]
    else:
        if equip > buys[side][0]:
            full[1] += 1
            if mapp == targetmap:
                if site == 'A':
                    mapstat_a[1] += 1
                elif site == 'B':
                    mapstat_b[1] += 1
        elif equip > buys[side][1]:
            force[1] += 1
        else:
            eco[1] += 1
    return mapstat_a, mapstat_b, full, force, eco

def pistol(rounds, side):
    pistol = list([1.0, 1.0001])
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            if i[3] == side:
                pistol[0] += 1
            pistol[1] += 1
    return pistol[0]/pistol[1]
    
def pistolplant(rounds):
    plant = [1.0, 1.0001]
    for i in rounds:
        if (i[2] == 0 or i[2] == 15):
            if i[15]:
                plant[0] += 1
            plant[1] += 1
    return plant[0]/plant[1]

def pistolpoint(player, rounds):
    return 1
    points = [0, 0]
    for r in rounds:
        if r[2] == 0 or r[2] == 15:
            cur = conn.execute( "SELECT * FROM Playerstats WHERE player_id == "+str(player)+" AND match_id == "+str(r[0])+" AND \
                                round == "+str(r[2]) )
            res = cur.fetchone()
            points[0] += res[4]*2 + res[5] - res[6]
            points[1] += 1
    return points[0]/points[1]
 
def t_take(rounds, mapp, ar):
    take_a = list([1.0, 1.0001])
    take_b = list([1.0, 1.0001])
    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            take_a, take_b, full, force, eco = equip_stat(i[1], mapp, take_a, take_b, full, force, eco, i[10], 1, i[17], 1)
        else:
            take_a, take_b, full, force, eco = equip_stat(i[1], mapp, take_a, take_b, full, force, eco, i[10], 0, i[17], 1)

    take_a = full
    take_b = full

    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])

    for i in ar:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            full, force, eco = get_weakness(full, force, eco, i[10], 1, 1)
        else:
            full, force, eco = get_weakness(full, force, eco, i[10], 0, 1)

    ecoweak = full[0]/full[1] - eco[0]/eco[1]
    forceweak = full[0]/full[1] - force[0]/force[1]
    hold_a = take_a[0]/take_a[1]
    hold_b = take_b[0]/take_b[1]
    return [hold_a-ecoweak, hold_a-forceweak, hold_a, hold_b-ecoweak, hold_b-forceweak, hold_b]

def ct_hold(rounds, mapp, ar):
    hold_a = list([1.0, 1.0001])
    hold_b = list([1.0, 1.0001])
    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 0 and i[3] == 'CT':
            hold_a, hold_b, full, force, eco = equip_stat(i[1], mapp, hold_a, hold_b, full, force, eco, i[9], 1, i[17], 0)
        else:
            hold_a, hold_b, full, force, eco = equip_stat(i[1], mapp, hold_a, hold_b, full, force, eco, i[9], 0, i[17], 0)

    hold_a = full
    hold_b = full

    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])

    for i in ar:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 0 and i[3] == 'CT':
            full, force, eco = get_weakness(full, force, eco, i[9], 1, 0)
        else:
            full, force, eco = get_weakness(full, force, eco, i[9], 0, 0)
                
    ecoweak = full[0]/full[1] - eco[0]/eco[1]
    forceweak = full[0]/full[1] - force[0]/force[1]
    hold_a = hold_a[0]/hold_a[1]
    hold_b = hold_b[0]/hold_b[1]
    return [hold_a-ecoweak, hold_a-forceweak, hold_a, hold_b-ecoweak, hold_b-forceweak, hold_b]

def ct_retake(rounds, mapp, ar):
    retake_a = list([1.0, 1.0001])
    retake_b = list([1.0, 1.0001])
    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            if i[3] == 'CT':
                retake_a, retake_b, full, force, eco = equip_stat(i[1], mapp, retake_a, retake_b, full, force, eco, i[9], 1, i[17], 0)
            else:
                retake_a, retake_b, full, force, eco = equip_stat(i[1], mapp, retake_a, retake_b, full, force, eco, i[9], 0, i[17], 0)

    retake_a = full
    retake_b = full

    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])

    for i in ar:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            if i[3] == 'CT':
                full, force, eco = get_weakness(full, force, eco, i[9], 1, 0)
            else:
                full, force, eco = get_weakness(full, force, eco, i[9], 0, 0)

    ecoweak = full[0]/full[1] - eco[0]/eco[1]
    forceweak = full[0]/full[1] - force[0]/force[1]
    retake_a = retake_a[0]/retake_a[1]
    retake_b = retake_b[0]/retake_b[1]
    return [retake_a-ecoweak, retake_a-forceweak, retake_a, retake_b-ecoweak, retake_b-forceweak, retake_b]

def t_hold(rounds, mapp, ar):
    hold_a = list([1.0, 1.0001])
    hold_b = list([1.0, 1.0001])
    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            if i[3] == 'T':
                hold_a, hold_b, full, force, eco = equip_stat(i[1], mapp, hold_a, hold_b, full, force, eco, i[10], 1, i[17], 1)
            else:
                hold_a, hold_b, full, force, eco = equip_stat(i[1], mapp, hold_a, hold_b, full, force, eco, i[10], 0, i[17], 1)

    hold_a = full
    hold_b = full

    full = list([1.0, 1.0001])
    force = list([1.0, 1.0001])
    eco = list([1.0, 1.0001])
    
    for i in ar:
        if i[2] == 0 or i[2] == 15:
            continue
        if i[15] == 1:
            if i[3] == 'T':
                full, force, eco = get_weakness(full, force, eco, i[10], 1, 1)
            else:
                full, force, eco = get_weakness(full, force, eco, i[10], 0, 1)

        
    ecoweak = full[0]/full[1] - eco[0]/eco[1]
    forceweak = full[0]/full[1] - force[0]/force[1]
    hold_a = hold_a[0]/hold_a[1]
    hold_b = hold_b[0]/hold_b[1]
    return [hold_a-ecoweak, hold_a-forceweak, hold_a, hold_b-ecoweak, hold_b-forceweak, hold_b]

def bombsite(rounds, mapp):
    sites = [ [i[17] for i in rounds if i[1] == mapp and i[10] > 12000].count("A"), [i[17] for i in rounds if i[1] == mapp and i[10] > 12000].count("B") ]
    if sum(sites) < 10:
        return [5, 5]
    else:
        return [i[17] for i in rounds if i[1] == mapp and i[10] > 12000].count("A"), [i[17] for i in rounds if i[1] == mapp and i[10] > 12000].count("B")

def survival(rounds, side, won):
    winner = ['CT', 'T'][side]
    buys = [ [22000, 12000], [19500, 10000] ]
    equip = [9, 10]

    full = [1 for i in range(6)]
    force = [1 for i in range(6)]
    eco = [1 for i in range(6)]
    
    for i in rounds:
        if i[2] == 0 or i[2] == 15:
            continue
        if (i[3] == winner and won) or (i[3] != winner and not won):
            if i[ equip[side] ] > buys[side][0]:
                full[i[5+side]] += 1
            elif i[ equip[side] ] > buys[side][1]:
                force[i[5+side]] += 1
            else:
                eco[i[5+side]] += 1
    return eco + force + full
        
def avg_points(player, rounds, mapp, side):
    buys = [ [22000, 12000], [19500, 10000] ]
    equip = [9, 10]
    
    mappoints = [0.0, 0.0, 0.0, 0.0]
    points = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    return [1, 1, 1, 1, 1, 1]
    for r in rounds:
        if r[2] == 0 or r[2] == 15:
            continue
        cur = conn.execute( "SELECT * FROM Playerstats WHERE player_id == "+str(player)+" AND match_id == "+str(r[0])+" AND \
                            round == "+str(r[2]) )
        res = cur.fetchone()
        if r[1] == mapp and r[ equip[side] ] > buys[side][0]:
            if r[17] == 'A':
                mappoints[0] += res[4]*2 + res[6] - res[5]
                mappoints[1] += 1
            if r[17] == 'B':
                mappoints[2] += res[4]*2 + res[6] - res[5]
                mappoints[3] += 1
                
        if r[ equip[side] ] > buys[side][0]:
            points[0] += res[4]*2 + res[6] - res[5]
            points[1] += 1
        elif r[ equip[side] ] > buys[side][1]:
            points[2] += res[4]*2 + res[6] - res[5]
            points[3] += 1
        else:
            points[4] += res[4]*2 + res[6] - res[5]
            points[5] += 1

        mappoints[0], mappoints[1] = points[0], points[1]
        mappoints[2], mappoints[3] = points[0], points[1]
        
    ecoweak = points[0]/points[1] - points[4]/points[5]
    forceweak = points[0]/points[1] - points[2]/points[3]
    points_a = mappoints[0]/mappoints[1]
    points_b = mappoints[2]/mappoints[3]
    
    return [points_a-ecoweak, points_a-forceweak, points_a, points_b-ecoweak, points_b-forceweak, points_b]

def get_stats(team, common_opp, mapp, d):
    global dato
    dato = d
    bombsites = list([0, 0])
    ct_holds = [0 for i in range(6)]
    ct_retakes = [0 for i in range(6)]
    t_takes = [0 for i in range(6)]
    t_holds = [0 for i in range(6)]
    pistols = [0, 0]
    survivors = [0 for i in range(18)]
    survivors1 = [0 for i in range(18)]
    survivors2 = [0 for i in range(18)]
    survivors3 = [0 for i in range(18)]
    pistolplants = 0 
    points = list()
    pistolpoints = list()
##    eligible = [x for x in team if get_common_matches(x, common_opp) != 0]
##    if eligible < 4:
##        eligible[200]
    
    for player in team:
        e = len(team)
        ct_rounds = get_rounds(player, 'CT', 'T', common_opp)
        t_rounds = get_rounds(player, 'T', 'CT', common_opp)
        ct_allrounds = get_all_rounds(player, 'CT', 'T')
        t_allrounds = get_all_rounds(player, 'T', 'CT')
        
        bombsites = [5, 5]
        ct_holds = [x+y for x,y in zip(ct_holds, ct_hold(ct_rounds, mapp, ct_allrounds))]
        ct_retakes = [x+y for x,y in zip(ct_retakes, ct_retake(ct_rounds, mapp, ct_allrounds))]
        t_takes = [x+y for x,y in zip(t_takes, t_take(t_rounds, mapp, t_allrounds))]
        t_holds = [x+y for x,y in zip(t_holds, t_hold(t_rounds, mapp, t_allrounds))]
        pistols = [x+y for x,y in zip(pistols, [pistol(ct_rounds, 'CT'), pistol(t_rounds, 'T')])]
        points.append( [avg_points(player, ct_rounds, mapp, 0), avg_points(player, t_rounds, mapp, 1)] )
        survivors = [x+y for x,y in zip(survivors, survival(ct_rounds, 0, 0))]
        survivors1 = [x+y for x,y in zip(survivors1, survival(ct_rounds, 0, 1))]
        survivors2 = [x+y for x,y in zip(survivors2, survival(t_rounds, 1, 0))]
        survivors3 = [x+y for x,y in zip(survivors3, survival(t_rounds, 1, 1))]
        pistolplants += pistolplant(t_rounds)
        pistolpoints.append( [pistolpoint(player, ct_rounds), pistolpoint(player, t_rounds)] )
    return bombsites, [i/e for i in ct_holds], [i/e for i in ct_retakes], [i/e for i in t_takes], \
    [i/e for i in t_holds], [i/e for i in pistols], points, survivors, survivors1, survivors2, survivors3, \
    pistolplants/e, pistolpoints

def get_buy_ct(players):
    """
    returns CT buy data to fit.
    """
    data = list()
    target = list()
    for player in players:
        matches = get_matches(player, 365)
        for match in matches:
            teamid = get_team_id(player, match)
            cur = conn.execute("SELECT ct_startmoney, ct_saved, ctlosestreak, ct_equipvalue, side_won, team_won, number, map FROM Round WHERE match_id == "+str(match)+" AND number != 0 AND number != 14 AND number < 15")
            stuff = cur.fetchall()
            for res in stuff:
                try:
                    correctlose = conn.execute("SELECT ctlosestreak FROM Round WHERE match_id = %s AND number = %s and map = '%s'" % (str(match), str(res[6]-1), res[7])).fetchone()[0]
                    correctlose = min(correctlose, 5)
                except:
                    continue
                if (res[4] == 'CT' and teamid == res[5]) or (res[4] == 'T' and teamid != res[5]):
                    if res[0]+res[1] >= res[3]:
                        data.append([ res[0]+res[1], correctlose, res[3] ] )
    return data

def get_buy_t(players):
    """
    returns T buy data to fit.
    """
    data = list()
    target = list()
    for player in players:
        matches = get_matches(player, 365)
        for match in matches:
            teamid = get_team_id(player, match)
            cur = conn.execute("SELECT t_startmoney, t_saved, tlosestreak, t_equipvalue, side_won, team_won, number, map FROM Round WHERE match_id == "+str(match)+" AND number != 0 AND number != 14 AND number < 15")
            stuff = cur.fetchall()
            for res in stuff:
                try:
                    correctlose = conn.execute("SELECT tlosestreak FROM Round WHERE match_id = %s AND number = %s and map = '%s'" % (str(match), str(res[6]-1), res[7])).fetchone()[0]
                    correctlose = min(correctlose, 5)
                except:
                    continue
                if (res[4] == 'T' and teamid == res[5]) or (res[4] == 'CT' and teamid != res[5]):
                    if res[0]+res[1] >= res[3]:
                        data.append([ res[0]+res[1], correctlose, res[3] ] )
    return data
