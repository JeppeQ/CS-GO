import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import requests
from bs4 import BeautifulSoup
from time import sleep
import difflib
import random
import re
from pinnacleAPI import get_lines

import sqlite3
import datetime
conn = sqlite3.connect('/root/simulation/csgobets.db')

def uniquefy(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if not (x in seen or seen_add(x))]

def get_info(match):
    
    matchid = match.split('-')[0].split('/')[-1]
    maptypes = ['Mirage', 'Cache', 'Cobblestone', 'Nuke', 'Overpass', 'Train', 'Inferno', 'Dust2', 'Season', 'Cbble', '??']
    
    teamnames = list()
    hltv_ids = list()
    egb, betway = 'None', 'None'
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
            maps.append(str(i['src'])[40:-4].title().lower())
            if maps[-1] == 'cobblestone':
                maps[-1] = 'cbble'
        except:
            continue

    for miss in range(7-len(maps)):
        maps.append('tba')
        
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

    for a in soup.find_all('a', href=True):
        if "egbaffiliates" in a['href']:
            egb = a['href']
        if "betway.com" in a['href']:
            betway = a['href']
    
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

    return [team1, teamnames[:5], team2, teamnames[5:], form, maps, matchid, egb, betway, hltv_ids]

class csbetting:

    def __init__(self):
       # self.egb = self.egb_browser()
       # self.mouse = webdriver.ActionChains(self.egb)
        self.pinnaclebetsize = 10
        self.egbetsize = 2
        
    def egb_browser(self):
        browser = webdriver.PhantomJS()
        browser.get('http://egb.com/')
        sleep(8)
        username = browser.find_element_by_id("user_name")
        username.send_keys('TheQ')
        passw = browser.find_element_by_id("user_password")
        passw.send_keys('l2pmorron')
        browser.find_element_by_xpath('//*[@id="session"]/table/tbody/tr[2]/td[3]/input').click()
        sleep(5)
        return browser

    def run(self):
        matches = self.upcoming_matches()
        matches = self.get_hltv_matches(matches)
        
    def upcoming_matches(self):
        matches = list()
        r = requests.get('http://www.hltv.org/')
        soup = BeautifulSoup(r.text, 'html.parser')
        div = soup.find("li", {"id" : "boc1"})
        links = div.findAll('a')
        for i in links[1:-1]:
            matches.append( 'http://www.hltv.org' + i['href'] )
        return matches

    def get_hltv_matches(self, matches):
        conn.execute("DELETE FROM matches")
        conn.commit()
        
        leg = list()
        for match in matches:
            sleep(1)
            try:
                data = get_info( match )
                if len(data[9]) < 10:
                    continue
            except:
                continue
                
            conn.execute("INSERT OR IGNORE INTO matches VALUES("+data[6]+", '"+datetime.datetime.now().isoformat()[:10]+"', '"+data[0]+"', '"+data[2]+"', \
                    '"+data[9][0]+"', '"+data[9][1]+"', '"+data[9][2]+"', '"+data[9][3]+"', '"+data[9][4]+"', \
                    '"+data[9][5]+"', '"+data[9][6]+"', '"+data[9][7]+"', '"+data[9][8]+"', '"+data[9][9]+"', \
                    '"+data[5][0]+"', '"+data[5][1]+"', '"+data[5][2]+"', '"+data[5][3]+"', '"+data[5][4]+"', '"+data[5][5]+"', '"+data[5][6]+"', \
                    '"+data[7]+"', 'None', 'None', '"+data[8]+"', 'None', 'None', 'None', 'None')")
            conn.commit()
            leg.append(match.split('-')[0].split('/')[-1])
        return leg
    
    def placebets(self, matches):
        for match in matches:
            cur = conn.execute("SELECT * FROM matches WHERE match_id = "+match)
            res = cur.fetchall()
            for i in res:
                if self.checksim(i[0]):
                    self.pinnacle(i[0], i[14:21])


    def insert_bet(self, match, mapp, team, win, odds, betsize, site):
        conn.execute("INSERT INTO bets VALUES(%s, '%s', '%s', %s, %s, %s, '%s')" %
                           (str(match), mapp, team, str(win), str(odds), str(betsize), site))
        conn.commit()

    def checksim(self, match):
        cur = conn.execute("SELECT * FROM simulation where match_id == "+str(match)+" AND map = 'all2'")
        res = cur.fetchall()
        return len(res) > 0
    
    def checkbet(self, match, mapp, site):
        cur = conn.execute("SELECT * FROM bets WHERE site = '"+site+"' and map = '"+mapp+"'")
        res = cur.fetchall()
        cur = conn.execute("SELECT * FROM bets WHERE match_id = '"+str(match)+"' and map = '"+mapp+"'")
        op = cur.fetchall()
        return len(res) > 0 or len(res) > 0
        
    def pinnacle(self, match, maps):
        cur = conn.execute("SELECT team FROM simulation WHERE match_id = "+str(match)).fetchall()
        teams = [a[0] for a in cur]  
        lines = get_lines('12') 
        for line in lines:
            if (line.home_odds-1) * (line.away_odds-1) >= 1.0:
                continue
            league = str(line.event_id)
            if "(map" not in line.home_team:
                #ALL BETTING SECOND VERSION
                if self.checkbet(match, 'all2', league):
                    continue
                pteams = [line.home_team, line.away_team]
                if set([t.lower() for t in pteams]) == set([t.lower() for t in teams]):
                    if pteams[0].lower() != teams[0].lower():
                        teams = [teams[1], teams[0]]
                    win = conn.execute("SELECT win FROM simulation WHERE match_id = %s AND map = 'all2' AND team = '%s'" % (str(match), teams[0])).fetchone()[0]
                    win2 = conn.execute("SELECT win FROM simulation WHERE match_id = %s AND map = 'all2' AND team = '%s'" % (str(match), teams[1])).fetchone()[0]
                    if self.profit(line.home_odds, win):
                        line.place_bet('TEAM1', self.pinnaclebetsize+1)
                        self.insert_bet(match, 'all2', pteams[0], win, line.home_odds, self.pinnaclebetsize+1, league)
                    elif self.profit(line.away_odds, win2):
                        line.place_bet('TEAM2', self.pinnaclebetsize+1)
                        self.insert_bet(match, 'all2', pteams[1], win2, line.away_odds, self.pinnaclebetsize+1, league)        
            
            
    def egaming(self, match, url, maps):
        self.egb.get(url)
        sleep(2)

        try:
            mapp = 'all'
            field = self.egb.find_element_by_xpath('//*[@id="bet-form"]/fieldset')
        except:
            return
        
        for i in field.find_elements_by_class_name("bet-block-title"):
            if "Map" in i.text:
                self.mouse.move_to_element(i).click().perform()
                box = self.egb.find_element_by_class_name("betsbox")
                mapp = maps[ int(i.text.split(" ")[1])-1 ]
                teams = [x.text for x in box.find_elements_by_class_name("s4")]
                odds = [x.text for x in box.find_elements_by_class_name("s3")]
                odds = [odds[0].split(" ")[1], odds[2].split(" ")[1]]
                break

        if not self.checkbet(match, mapp, 'egb') and mapp != 'all':
            cur = conn.execute("SELECT team, win FROM simulation WHERE match_id = "+str(match)+" AND map = '"+mapp+"'")
            res = cur.fetchall()
            win = [res[ teams.index( difflib.get_close_matches(res[0][0], teams, 1, 0)[0] ) ][1], res[ teams.index( difflib.get_close_matches(res[1][0], teams, 1, 0)[0] ) ][1] ]
            if win[0] == win[1] and win[0] != 0.5:
                print "error in recognizing team"
                return
            betbox = box.find_elements_by_class_name("bet-sum")
            if self.profit(odds[0], win[0]):    
                betbox[0].send_keys(str(self.egbetsize))
                self.insert_bet(match, mapp, teams[0], win[0], odds[0], self.egbetsize, 'egb')
                self.egb.find_element_by_xpath('//*[@id="betswindow186094"]/div/bet-form/div[1]/div[6]/button').click()
                sleep(1)
                self.egb.find_element_by_xpath('//*[@id="confirm_ok"]').click()        
            elif self.profit(odds[1], win[1]):
                betbox[1].send_keys(str(self.egbetsize))
                self.insert_bet(match, mapp, teams[1], win[1], odds[1], self.egbetsize, 'egb')
                self.egb.find_element_by_xpath('//*[@id="betswindow186094"]/div/bet-form/div[1]/div[6]/button').click()
                sleep(1)
                self.egb.find_element_by_xpath('//*[@id="confirm_ok"]').click()

        self.egb.get(url)
        sleep(2)
        box = self.egb.find_element_by_class_name("dialogbetsbox")
        teams = [x.text for x in box.find_elements_by_class_name("s4")]
        odds = [x.text for x in box.find_elements_by_class_name("s3")]
        odds = [odds[0].split(" ")[1], odds[2].split(" ")[1]]

        try:
            field = self.egb.find_element_by_xpath('//*[@id="bet-form"]/div/fieldset[1]')
        except:
            return
        
        for i in field.find_elements_by_class_name("bet-block-title"):
            if "place a bet" in i.text.lower():
                self.mouse.move_to_element(i).click().perform()
                break

        if self.checkbet(match, 'all', 'egb'):
            return
        
        cur = conn.execute("SELECT team, win FROM simulation WHERE match_id = "+str(match)+" AND map = 'all'")
        res = cur.fetchall()
        win = [res[ teams.index( difflib.get_close_matches(res[0][0], teams, 1, 0)[0] ) ][1], res[ teams.index( difflib.get_close_matches(res[1][0], teams, 1, 0)[0] ) ][1] ]
        if win[0] == win[1] and win[0] != 0.5:
            print "error in recognizing team"
            return
        betbox = box.find_elements_by_class_name("bet-sum")
        if self.profit(odds[0], win[0]):    
            betbox[0].send_keys(str(self.egbetsize))
            self.insert_bet(match, 'all', teams[0], win[0], odds[0], self.egbetsize, 'egb')
            self.egb.find_element_by_xpath('//*[@id="betswindow186094"]/div/bet-form/div[1]/div[6]/button').click()
            sleep(1)
            self.egb.find_element_by_xpath('//*[@id="confirm_ok"]').click()        
        elif self.profit(odds[1], win[1]):
            betbox[1].send_keys(str(self.egbetsize))
            self.insert_bet(match, 'all', teams[1], win[1], odds[1], self.egbetsize, 'egb')
            self.egb.find_element_by_xpath('//*[@id="betswindow186094"]/div/bet-form/div[1]/div[6]/button').click()
            sleep(1)
            self.egb.find_element_by_xpath('//*[@id="confirm_ok"]').click()

    def profit(self, odds, win):
        if float(odds)*float(win) > 1.01:
            return 1
        else:
            return 0

if __name__ == '__main__':
    cs = csbetting()
    cs.run()
