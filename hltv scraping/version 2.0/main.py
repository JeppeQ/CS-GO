from getstats import getstats
from getinfo import getteamsplaying
from simulation import simulation
from predictmap import predict_map
from result import result

def simulate(match):
    alldata = list()
    teams = getteamsplaying(match)
    team1, team2 = teams[0], teams[2]
    print "Teams:", team1, team2
    t1p, t2p = teams[1], teams[3]
    if teams[5][0] != 'Tba':
        maps = list(teams[5])
        print "Maps: ", maps
    else:
        #Predict Maps
        maps = predict_map(team1, team2, teams[4])
        print "Predicted maps: ", maps
    for i in maps:
        stats = simulation(getstats(t1p, t2p, i))
        print i, stats
        alldata.append(stats)
    result(alldata)

simulate('http://www.hltv.org/match/2300245-envyus-red-dot-invitational')
