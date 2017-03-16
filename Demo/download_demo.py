import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import csv
import re
import datetime
import difflib
import urllib2
import sqlite3
import patoolib
import os
import traceback
from os import listdir
from os.path import isfile, join
import subprocess

conn = sqlite3.connect('csgostats.db')

def uniquefy(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def get_matches(day):
    matchlinks = list()
    browser = webdriver.PhantomJS('phantomjs')
    browser.set_page_load_timeout(500)
    browser.get('http://www.hltv.org/matches/archive/')
    sleep(1)
    browser.find_element_by_id("hasDemo").click()
    date = browser.find_element_by_id("calendar")
    date.clear()
    date.send_keys(day+" to "+day)
    browser.find_element_by_id("search").click()
    sleep(2)
    soup = BeautifulSoup(browser.page_source, 'html.parser')

    links = soup.find("div", {"id" : "matches"})
    links = links.findAll('a')
    for i in links:
        try:
            matchlinks.append( 'http://www.hltv.org' + i['href'] )
        except:
            continue
    matchlinks = uniquefy(matchlinks)
    browser.close()
    return matchlinks

def get_info(match):
    
    matchid = match.split('-')[0].split('/')[-1]
    maptypes = ['Mirage', 'Cache', 'Cobblestone', 'Nuke', 'Overpass', 'Train', 'Inferno', 'Dust2', 'Season', 'Cbble', '??']
    
    teamnames = list()
    hltv_ids = list()
    r = requests.get(match)
    maps = list()
    soup = BeautifulSoup(r.text, 'html.parser')
        
    #Team, maps, players, format
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
    for part in a[0]['href'].split('&'):
        if 'teamid=' in part:
            team1id = part[7:]
    for part in a[1]['href'].split('&'):
        if 'teamid=' in part:
            team2id = part[7:]

    team1, team2 = a[0].text, a[1].text
    if team1[0] == ' ':
        team1 = team1[1:]
    if team2[0] == ' ':
        team2 = team2[1:]

    winner = soup.findAll("span", {"class" : "matchScore"})
    if winner[0] > winner[1]:
        matchwinner = team2
    elif winner[1] > winner[0]:
        matchwinner = team1
    else:
        matchwinner = 'Draw'
    
    div = soup.find_all("div", {"class" : "hotmatchbox"})
    
    for i in div:
        links = i.findAll('a')
        for a in links:
            if "demoid" in a['href']:
                demoid = a['href']
            if "player" in a['href']:
                if "playerid" in a['href']:
                    hltv_ids.append( a['href'].split("playerid")[1][1:] )
                else:
                    hltv_ids.append( a['href'].split("player")[1].split("-")[0][1:] )
                teamnames.append( a.text.lower() )

    if len(hltv_ids) < 10:
        return 0
    
    if len(set(teamnames)) < 10:
        for i in range(4, len(div)-1):
            if len(div[i].text.split()) == 5 and len(div[i+1].text.split()) == 5:
                boo = div[i].find_all("div")
                boo2 = div[i+1].find_all("div")
                t1players = uniquefy([i.text.lstrip().lower() for i in boo if "%" not in i.text and len(i.text) > 0 and i.text != u'\xa0'])
                t2players = uniquefy([i.text.lstrip().lower() for i in boo2 if "%" not in i.text and len(i.text) > 0 and i.text != u'\xa0'])
                teamnames = t1players + t2players
                break
        
    #BANS, PICKS
    allstuff = ""
    div = soup.find("div", {"class" : "hotmatchbox"})
    gem = [d.text.split(" ") for d in div.find_all("div")]
    gem = [g for g in gem if len(g) < 8 and ("picked" in g or "removed" in g)]
    team1picks = [[m for m in maptypes if m in t][0] for t in [i for i in gem if "picked" in i and team1.split(" ")[0] in i]]
    team2picks = [[m for m in maptypes if m in t][0] for t in [i for i in gem if "picked" in i and team2.split(" ")[0] in i]]
    team1removes = [[m for m in maptypes if m in t][0] for t in [i for i in gem if "removed" in i and team1.split(" ")[0] in i]]
    team2removes = [[m for m in maptypes if m in t][0] for t in [i for i in gem if "removed" in i and team2.split(" ")[0] in i]]

    if len(team1picks) < 1 or len(team2picks) < 1:
        div = soup.find("div", {"id" : "mapformatbox"})
        team1picks = [[m for m in maptypes if m in t][0] for t in [x.split(" ")+['??'] for x in [i for i in div if "picked" in i and team1 in i]]]
        team2picks = [[m for m in maptypes if m in t][0] for t in [x.split(" ")+['??'] for x in [i for i in div if "picked" in i and team2 in i]]]
        team1removes = [[m for m in maptypes if m in t][0] for t in [x.split(" ")+['??'] for x in [i for i in div if "removed" in i and team1 in i]]]
        team2removes = [[m for m in maptypes if m in t][0] for t in [x.split(" ")+['??'] for x in [i for i in div if "removed" in i and team2 in i]]]

    return [team1, teamnames[:5], team2, teamnames[5:], form, maps, matchid, matchwinner, demoid, team1picks, team2picks, team1removes, team2removes, [i for i in hltv_ids if len(i) > 0]]

def download_demo(demoid):
    url = 'http://www.hltv.org/interfaces/download.php?demoid='+demoid.split("=")[-1]
    req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
    print "Downloading demo..."
    data = urllib2.urlopen( req )
    with open("downloads/demo.rar", "wb") as f:
        while True:
            tmp = data.read(1024)
            if not tmp:
                break
            f.write(tmp)
    f.close()
    return 

def extract_demo():
    print "Extracting demo..."
    FNULL = open(os.devnull, 'w')
    args = "7z e downloads\demo.rar -odemofiles\\"
    subprocess.call(args, creationflags=0x08000000)
    return 0

def get_file_names(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    return onlyfiles

def analyze_demo(filename):
    print "Analyzing demo..."
    FNULL = open(os.devnull, 'w')    #use this if you want to suppress output to stdout from the subprocess
    args = "demo_analyzer.exe " + filename
    subprocess.call(args, creationflags=0x08000000)
    
def get_team_id(name):
    name = name.replace("'", "''")
    cur = conn.execute("SELECT team_id FROM Team WHERE hltv_alias = '"+name+"'")
    N = cur.fetchall()
    if len(N) > 0:
        return str(N[0][0])
    else:
        cur = conn.execute("SELECT team_id FROM Team")
        N = cur.fetchall()
        conn.execute("INSERT OR IGNORE INTO Team VALUES("+str(max(N)[0]+1)+", '"+name+"', '"+name+"', '"+name+"')")
        conn.commit()
        return str(max(N)[0]+1)

def get_player_id(players, ids):
    playerids = list()
    for x in range(len(ids)):
        players[x] = players[x].replace("'", "''")
        cur = conn.execute("SELECT player_id FROM Player2 WHERE hltv_id = %s" % (ids[x]))
        N = cur.fetchall()
        if len(N) > 0:
            playerids.append( str(N[0][0]) )
        else:
            cur = conn.execute("SELECT player_id FROM Player2")
            N = cur.fetchall()
            conn.execute("INSERT INTO Player2 VALUES("+str(max(N)[0]+1)+", '"+players[x]+"', "+ids[x]+")")
            conn.commit()
            playerids.append( str(max(N)[0]+1) )
    return playerids

def read_csv(filename):
    rounds = list()
    players = list()
    game_started = False
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        data = list(reader)
    for i in data:
        cur = i[0].split(";")
        if i[0][0] == '9':
            game_started = True
        if i[0][0] == '0' and not game_started:
            players = list()
        if len(cur) > 24:
            for player in cur[22:24][0].split(":"):
                if player not in players and len(player) > 0:
                    players.append(player)
    game_started = False
    for i in data:
        if i[0][0] == '9':
            game_started = True
        if i[0][0] == '0' and not game_started:
            rounds = list()
        elif i[0][0] == '0' and game_started:
            return players, rounds
        rounds.append( i[0].split(";") )
    return players, rounds

def assign_players(names, team):
    """
    names: demo names
    team: original
    """
    names = [i.lower() for i in names]
    team = [i.lower() for i in team]
    
    teammatches = list()
    namesmatches = list()
    sets = list()
    for i in team:
        teammatches.append([names.index(x) for x in difflib.get_close_matches(i, names, len(names), 0)])
    for i in names:
        namesmatches.append([team.index(x) for x in difflib.get_close_matches(i, team, len(team), 0)])
    test = [i[0] for i in teammatches]
    while(len(set(test)) < 10):
        for i in set([x for x in test if test.count(x) > 1]):
            for z in [n for n in namesmatches[i] if test[n] == i][1:]:
                if teammatches[z].index(i)+1 > 9:
                    test[z] = teammatches[z][0]
                else:
                    test[z] = teammatches[z][teammatches[z].index(i)+1]
    return [names[i] for i in test]

def create_string(l):
    end = ""
    for s in l:
        end += s + ":"
    return end[:-1]
    
def insertdata(data, date):
    team1 = data[0]
    team1_id = get_team_id(team1)
    team1_players = data[1]
    team1_players_id = [str(i) for i in get_player_id(team1_players, data[13][:5])]
    
    team2 = data[2]
    team2_id = get_team_id(team2)
    team2_players = data[3]
    team2_players_id = [str(i) for i in get_player_id(team2_players, data[13][5:])]
    
    form = data[4]
    matchid = data[6]
    winner = data[7]
    
    #INSERT Match
    conn.execute("INSERT OR IGNORE INTO Match VALUES("+matchid+", '"+date+"', "+team1_id+", "+team2_id+", '"+winner.replace("'", "''")+"', '"+form+"', \
                  '"+team1_players_id[0]+"', '"+team1_players_id[1]+"', '"+team1_players_id[2]+"', '"+team1_players_id[3]+"', '"+team1_players_id[4]+"', \
                  '"+team2_players_id[0]+"', '"+team2_players_id[1]+"', '"+team2_players_id[2]+"', '"+team2_players_id[3]+"', '"+team2_players_id[4]+"', \
                    '"+create_string(data[9])+"', '"+create_string(data[10])+"','"+create_string(data[11])+"','"+create_string(data[12])+"')")

    for csv in get_file_names('C:\Users\QQ\Dropbox\csgo stats\database\csv'):
        #INSERT Round
        Map = csv.split("_")[1].split(".")[0]
        demo_data = read_csv('csv/'+csv)
        if len(demo_data[0]) < 10:
            continue
        
        demo_team = assign_players(demo_data[0], data[1]+data[3])
        demo_team1, demo_team2 = demo_team[:5], demo_team[5:]
        for row in demo_data[1]:
            if row[0] != '0' and int(row[5]) == 0 and int(row[6]) == 0:
                continue
            if row[26].lower() in demo_team1:
                team_won = team1_id
            elif row[26].lower() in demo_team2:
                team_won = team2_id
            else:
                print "UNABLE TO RECOGNIZE WINNING TEAM!"
                team_won = '-1'
            conn.execute("INSERT OR IGNORE INTO Round VALUES("+matchid+", '"+Map+"', '"+row[0]+"', '"+row[25]+"', "+team_won+",\
                        "+row[3]+", "+row[4]+", "+row[5]+", "+row[6]+", "+row[7]+", "+row[8]+", "+row[9]+", "+row[10]+","+row[11]+","+row[12]+", "+row[19]+","+row[20]+", '"+row[21]+"')") 
    
            #INSERT Playerstats
            pkills = [i.lower() for i in row[22].split(":")]
            pdeaths = [i.lower() for i in row[23].split(":")]
            passists = [i.lower() for i in row[24].split(":")]
            for p in range(5):
                conn.execute("INSERT OR IGNORE INTO Playerstats VALUES("+team1_players_id[p]+", "+matchid+", '"+Map+"', '"+row[0]+"', \
                            "+str(pkills.count( demo_team1[p] ))+","+str(pdeaths.count( demo_team1[p] ))+", "+str(passists.count( demo_team1[p] ))+")" ) 
                conn.execute("INSERT OR IGNORE INTO Playerstats VALUES("+team2_players_id[p]+", "+matchid+", '"+Map+"', '"+row[0]+"', \
                            "+str(pkills.count( demo_team2[p] ))+","+str(pdeaths.count( demo_team2[p] ))+", "+str(passists.count( demo_team2[p] ))+")" )
    conn.commit()

def clean_up():
    dirs = ['csv', 'demofiles', 'downloads']
    for d in dirs:
        for f in os.listdir(d+ "/."):
            os.remove(d+"/"+f)

def here(id):
    with conn:
        cur = conn.execute("SELECT * FROM Round WHERE match_id == "+id+"")
        res = cur.fetchall()
    return len(res) > 0
        
if __name__ == '__main__':
##    with open("brokenmatches.txt", "r") as f:
##        matches = f.read().splitlines()
    for day in range(2, 3):
        date = (datetime.datetime.now() - datetime.timedelta(days=day)).isoformat()[:10]
        print date
        matches = get_matches(date)
        for match in matches: 
##            match = qq.split(",")[0]
##            date = qq.split(",")[1]
##            if here(match.split('-')[0].split('/')[-1]):
##                continue
##            print match, date
##            for demos in get_file_names('C:\Users\QQ\Dropbox\csgo stats\database\demofiles'):
##                os.rename('C:\Users\QQ\Dropbox\csgo stats\database\demofiles\\'+demos, 'C:\Users\QQ\Dropbox\csgo stats\database\demofiles\\'+demos.replace(" ", ""))
##            for demos in get_file_names('C:\Users\QQ\Dropbox\csgo stats\database\demofiles'):
##                analyze_demo('demofiles/'+demos) 
##            data = get_info(match)
##            insertdata(data, date)
##            break
          
            print match, date
            try:
                if here(match.split('-')[0].split('/')[-1]) or match.split('-')[0].split('/')[-1] == '2297896' or match.split('-')[0].split('/')[-1] == '2302562':
                    continue
                clean_up()
                data = get_info(match)
                print data[13]
                download_demo(data[8])
                extract_demo()
                for demos in get_file_names('C:\Users\QQ\Dropbox\csgo stats\database\demofiles'):
                    os.rename('C:\Users\QQ\Dropbox\csgo stats\database\demofiles\\'+demos, 'C:\Users\QQ\Dropbox\csgo stats\database\demofiles\\'+demos.replace(" ", ""))
                for demos in get_file_names('C:\Users\QQ\Dropbox\csgo stats\database\demofiles'):
                    analyze_demo('demofiles/'+demos) 
                insertdata(data, date)
                print "Inserted succesfully"
            except Exception:
                print(traceback.format_exc())
                with open("brokenmatches.txt", "a") as myfile:
                    myfile.write(match+","+date+"\n")
            
        
        




    
