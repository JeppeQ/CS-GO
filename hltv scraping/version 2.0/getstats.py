from __future__ import division
import sqlite3
conn = sqlite3.connect('csstats.db')
conn.text_factory = str

def sl(s):
    s = s.split("-")
    return [int(i) for i in s]

def translate_stats(stats):
    ctkills = [0 for i in range(24)]
    tkills = [0 for i in range(24)]
    knife = 0
    ctrounds = [0 for i in range(4)]
    trounds = [0 for i in range(4)]
    bombs = [0 for i in range(4)]
    ctss = [0 for i in range(12)]
    tss = [0 for i in range(12)]
    totalrounds = [0 for i in range(8)]
    for i in stats:
        ctkills = [x+y for x,y in zip(ctkills, sl(i[3]))]
        tkills = [x+y for x,y in zip(tkills, sl(i[4]))]
        knife += int(i[5])
        ctrounds = [x+y for x,y in zip(ctrounds, sl(i[6]))]
        trounds = [x+y for x,y in zip(trounds, sl(i[7]))]
        bombs = [x+y for x,y in zip(bombs, sl(i[8]))]
        ctss = [x+y for x,y in zip(ctss, sl(i[9]))]
        tss = [x+y for x,y in zip(tss, sl(i[10]))]
        totalrounds = [x+y for x,y in zip(totalrounds, sl(i[11]))]
    return ctkills, tkills, knife, ctrounds, trounds, bombs, ctss, tss, totalrounds, len(stats)

def common_opp(team):
    matches = list()
    with conn:
        cur = conn.execute( "SELECT id, player, opp1, opp2, opp3, opp4, opp5 FROM \
                            players WHERE date(date) > date('now', '-2 months')")
        N = cur.fetchall()
    for i in N:
        if len(set(team) & set(i[2:])) > 2:
            matches.append(i[1])
    teams = [matches[i:i+5] for i in range(0, len(matches), 5)]
    for i in teams:
        i.sort()
    teams = [list(x) for x in set(tuple(x) for x in teams)]
    return teams

def playerdata(team, opp, cmap):
    total = list()
    for i in team:
        stats = list()
        cur = conn.execute( "SELECT * FROM players WHERE player = '"+i+"' AND \
                             date(date) > date('now', '-3 months')")
        N = cur.fetchall()
        for a in N:
            for b in opp:
                if len(set(a[12:17]) & set(b)) > 2:
                    stats.append(a)
                    if a[17] == cmap.lower():
                        stats.append(a)
        total.append( translate_stats(stats) )
    return total
        
def getstats(team1, team2, cmap):
    stats = list()
    t1opp = common_opp(team2)+[team2]
    t2opp = common_opp(team1)+[team1]
    team1 = playerdata(team1, t1opp, cmap)
    team2 = playerdata(team2, t2opp, cmap)
    return team1, team2, getknife(team1), getknife(team2), getrounds(team1), getrounds(team2), getbombs(team1), getbombs(team2)

def getknife(stats):
    won = sum([i[2] for i in stats])
    total = sum([i[-1] for i in stats])
    return won / total

def getrounds(stats):
    won = [0 for i in range(8)]
    total = [0 for i in range(8)]
    for i in stats:
        won = [x+y for x,y in zip(won, i[3]+i[4])]
        total = [x+y for x,y in zip(total, i[8])]
    return [round(x/y, 2) for x,y in zip(won, total)]

def getbombs(stats):
    bombs = [0 for i in range(4)]
    total = [0 for i in range(4)]
    for i in stats:
        bombs = [x+y for x,y in zip(bombs, i[5])]
        total = [x+y for x,y in zip(total, i[8][4:])]
    return [round(x/y, 2) for x,y in zip(bombs, total)]

    
