from data_functions_v3 import get_stats, get_buy_ct, get_buy_t

class team:

    def __init__(self, team, opp, mapp, v3, date):
        self.sites = ['A', 'B']
        self.equip = ['eco', 'force', 'full']
        self.data = get_stats(team, opp, mapp, date)
        self.playerscore = [0 for i in range(5)]
        self.teamscore = 0
        
        self.ctbuys = get_buy_ct(team)
        self.ctbuys.sort(key=lambda x: x[0])
        self.ctbuys = [[i for i in self.ctbuys if i[1] == x] for x in range(6)]
        self.ctmoneyspent = [[i[0] for i in x] for x in self.ctbuys]
        
        self.tbuys = get_buy_t(team)
        self.tbuys.sort(key=lambda x: x[0])
        self.tbuys = [[i for i in self.tbuys if i[1] == x] for x in range(6)]
        self.tmoneyspent = [[i[0] for i in x] for x in self.tbuys]
        
    def get_model(self, side, lose):
        if side == 'CT':
            return [self.ctbuys[lose], self.ctmoneyspent[lose]]
        else:
            return [self.tbuys[lose], self.tmoneyspent[lose]]
        
    def get_bombsite(self):
        return self.data[0]

    def ct_hold(self, site, equip):
        return self.data[1][ 3*self.sites.index(site) + self.equip.index(equip) ]

    def ct_retake(self, site, equip):
        return self.data[2][ 3*self.sites.index(site) + self.equip.index(equip) ]

    def t_take(self, site, equip):
        return self.data[3][ 3*self.sites.index(site) + self.equip.index(equip) ]

    def t_hold(self, site, equip):
        return self.data[4][ 3*self.sites.index(site) + self.equip.index(equip) ]

    def pistols(self, side):
        sides = ['CT', 'T'].index(side)
        return self.data[5][sides]

    def pistolplant(self):
        return self.data[11]
    
    def points(self, site, equip, side):
        sides = ['CT', 'T'].index(side)
        self.playerscore = [x+y for x,y in zip(self.playerscore, [a[sides][3*self.sites.index(site)+self.equip.index(equip)] for a in self.data[6]])]

    def pistolpoints(self, side):
        sides = ['CT', 'T'].index(side)
        self.playerscore = [x+y for x,y in zip(self.playerscore, [a[sides] for a in self.data[12]])]
        
    def teamscores(self, won, plant, defuse, side):
        if won:
            self.teamscore += 1
        else:
            self.teamscore -= 1
        if side == 'CT':
            self.teamscore += defuse*2
        else:
            self.teamscore += plant
        
    def survival(self, side, equip, won):
        if equip == 'pistol':
            return [1, 0]
        s = self.equip.index(equip)*6
        if won:
            if side == 'CT':
                return self.data[8][s:s+6]
            else:
                return self.data[10][s:s+6]
        else:
            if side == 'CT':
                return self.data[7][s:s+6]
            else:
                return self.data[9][s:s+6]
            
        
        
        
