import requests
import re
from selenium import webdriver
from bs4 import BeautifulSoup

def getinfo(match, t1, t2, o1, o2):
    teamnames = list()
    r = requests.get(match)
    soup = BeautifulSoup(r.text, 'html.parser')
    #div = soup.find("div", {"class" : "hotmatchbox"})
    #form = 'bo'+str(div.findAll(text=re.compile('Best of'))[0].split()[-1])
    a = soup.findAll("a", {"class" : "nolinkstyle"})
    team1, team2 = a[0].text, a[1].text
    div = soup.find_all("div", {"class" : "hotmatchbox"})
    t1players, t2players = div[7].text.split(), div[8].text.split()
    for i in div:
        links = i.findAll('a')
        for a in links:
            if "playerid" in a['href']:
                teamnames.append( a.text.lower() )
    if t1.lower() == team1.lower() or t2.lower() == team1.lower():
        if t1.lower() == team1.lower():
            return [team1, orderteam(o1, teamnames[:5]), team2, teamnames[5:], o1, 1]
        else:
            return [team1, orderteam(o2, teamnames[:5]), team2, teamnames[5:], o2, 1]
    elif t2.lower() == team2.lower() or t1.lower() == team2.lower():
        if t2.lower() == team2.lower():
            return [team2, orderteam(o2, teamnames[5:]), team1, teamnames[:5], o2, 2]
        else:
            return [team2, orderteam(o1, teamnames[5:]), team1, teamnames[:5], o1, 2]

def getteamsplaying(match):
    teamnames = list()
    r = requests.get(match)
    maps = list()
    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find("div", {"class" : "hotmatchbox"})
    try:
        form = 'bo'+str(div.findAll(text=re.compile('Best of'))[0].split()[-1])
    except:
        form = 'bo3'
        print "No bo defined"
    img = soup.findAll('img', {'src':re.compile('hotmatch')})
    for i in img:
        try:
            maps.append(str(i['src'])[40:-4].title())
        except:
            continue
    a = soup.findAll("a", {"class" : "nolinkstyle"})
    team1, team2 = a[0].text, a[1].text
    div = soup.find_all("div", {"class" : "hotmatchbox"})
    t1players, t2players = div[7].text.split(), div[8].text.split()
    for i in div:
        links = i.findAll('a')
        for a in links:
            if "playerid" in a['href']:
                teamnames.append( a.text )
    return [team1, teamnames[:5], team2, teamnames[5:], form, maps]

def orderteam(team1, team2):
    team = list()
    for i in team1:
        if i in team2:
            team.append(i)
        else:
            try:
                team.append([i for i in team2 if i not in team1][0])
                team2.remove(team[-1])
            except:
                pass
                #print "Error in ordering team", team1, team2
    return team

def uniquefy(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]
##teams = getteamsplaying('http://www.hltv.org/match/2298603-titan-mousesports-cevo-professional-season-8')
##print getinfo('http://www.hltv.org/match/2298603-titan-mousesports-cevo-professional-season-8', teams[0], teams[2], [u'Hodor', u'smithzz', u'QQ', u'scream', u'rpk'], teams[3])
##
