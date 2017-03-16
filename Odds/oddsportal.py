# -*- coding: cp1252 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import difflib
import sqlite3

conn = sqlite3.connect('oddsportal.db')
statsdb = sqlite3.connect('C:\Users\QQ\Dropbox\csgo domination\csgostats.db')

class oddsportal:

    def __init__(self, sport):
        self.sport = sport
        self.browser = webdriver.PhantomJS('phantomjs')
        self.browser.set_page_load_timeout(500)
        self.namedict = dict({'NaVi':'Natus Vincere', 'G2 Esports':'G2', 'Titan CS.':'Titan',
                              'NRG Esports':'NRG', 'Ninjas in Pyjamas':'NiP', 'Penta Sports':'PENTA',
                              '3sUP Enterprises':'3sUP', 'Godsent':'GODSENT', 'SPLYCE':'Splyce',
                              'Follow eSports':'Splyce', 'Counter Logic Gaming':'CLG', 'Team Solomid':'TSM',
                              'Lounge Gaming':'Dobry&Gaming', 'EZG eSports':'EZG'})
        self.check = dict()
        
    def get_links(self):
        eventlinks = list()
        self.browser.get("http://www.oddsportal.com/results/#esports")

        soup = BeautifulSoup(self.browser.page_source, 'html.parser')
        links = soup.findAll('a')
        for i in links:
            try:
                if self.sport in i['href']:
                    eventlinks.append( 'http://www.oddsportal.com' + i['href'] )
            except:
                continue
        eventlinks[-1] = 'http://www.oddsportal.com/esports/world/counter-strike-esl-pro-league-season-4/results/'
        return eventlinks

    def get_hltv_name(self, name):
        if name in self.namedict:
            return self.namedict[name]
        name = name.replace("Esports", "").replace("Gaming", "").replace("Team", "").replace("eSports", "")
        teams = statsdb.execute("SELECT DISTINCT hltv_alias FROM Team").fetchall()
        teams = [i[0] for i in teams]
        return difflib.get_close_matches(name, teams, len(teams), 0)[0]
        
    def get_odds(self):
        events = self.get_links()
        events = ['http://www.oddsportal.com/esports/world/counter-strike-esl-pro-league-season-4/results/#/page/8/',
                  'http://www.oddsportal.com/esports/world/counter-strike-esl-pro-league-season-4/results/#/page/5/',
                  'http://www.oddsportal.com/esports/world/counter-strike-esl-pro-league-season-4/results/#/page/4/',
                  'http://www.oddsportal.com/esports/world/counter-strike-championship-series-season-1/results/#/page/2/',
                  'http://www.oddsportal.com/esports/usa/counter-strike-eleague-season-2/',
                  'http://www.oddsportal.com/esports/usa/counter-strike-intel-extreme-masters-oakland/results/']
                      
        for event in events:
            print event
            self.browser.get(event)
            self.browser.refresh()
            try:
                if event[-8:] == 'results/':
                    pages = self.browser.find_element_by_id('pagination')
                    for l in pages.text:
                        if l.isdigit():
                            if int(l) != 1:
                                print "page added"
                                events.append(event+'#/page/%s/' % (l))
            except:
                pass
        
            table = self.browser.find_element_by_id('tournamentTable')
            text = table.text.splitlines()
            for i in range(len(text)):
                if '2016' in text[i] or '2015' in text[i] and 'FACEIT League 2015-Stage 3' not in text[i]:
                    text = text[i:]
                    break
            for i in range(len(text)):
                if len(text[i]) < 6:
                    continue
                if '2016' in text[i] or '2015' in text[i]:
                    date = datetime.strptime(text[i][:11], "%d %b %Y").isoformat()[:10]
                    continue
                s = text[i].split("-")
                if u'|\xab\xab12' in s[0]:
                    continue
                elif len(s) != 2:
                    continue

                team1, team2 = s[0][6:-1], s[1][1:-4]
                team1 = self.get_hltv_name(team1)
                team2 = self.get_hltv_name(team2)
                odds1, odds2 = text[i+1], text[i+2]
                try:
                    float(odds1)
                    float(odds2)
                except:
                    continue

                
                if s[1].split()[-1] == 'canc.' or s[1].split()[-1] == 'award.':
                    continue
                try:
                    score = [0, int(s[1].split()[-1][0]), int(s[1].split()[-1][2])]
                except:
                    continue
                
                if score[1] == score[2]:
                    continue

                if sum(score) < 2:
                    form = 1
                elif sum(score) < 4 and max(score) != 3:
                    form = 3
                else:
                    form = 5
                    
                winner = score.index(max(score))
                print date, team1, team2, odds1, odds2, winner, form
                conn.execute("INSERT OR IGNORE INTO csgo VALUES('%s', '%s', '%s', %s, %s, %s, %s)" % (date, team1, team2, odds1, odds2, str(winner), str(form)))
                conn.commit()
       
            
            
op = oddsportal('counter-strike')
op.get_odds()
