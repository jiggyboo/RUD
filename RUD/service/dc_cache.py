from datetime import date
import json
import ast

class DailyContentCache:

    def __init__(self, db_dao, praw_dao):
        self.db_dao = db_dao
        self.praw_dao = praw_dao
        self.dailyContent = {'recent':[],'recentN':[],'pops':[],'popsN':[],'todays':[],'todaysN':[]}
        self.pastContent = {'yesterday':{'pops':[],'popsN':[],'todays':[],'todaysN':[]},'twodays':{'pops':[],'popsN':[],'todays':[],'todaysN':[]}}
        self.today = ""

        f = open("cache.txt")
        text = f.read()
        if text == '':
            self.refresh_dcnt()
            self.today = str(date.today())
        else:
            d = ast.literal_eval(text)
            today = str(date.today())
            if d['today'] == today:
                self.pastContent = d['pastContent']
                self.dailyContent = d['dailyContent']
                self.today = today
                f.close()
                print('Date Matching/Cache useable')
                print(self.today)
            else:
                print('Date Not Matching/Cache not useable')
                self.refresh_dcnt()


    def dailyPopRS(self):
        dayPos = []
        dayNPos = []
        tp = self.praw_dao.topFive()
        subs = tp['subs']
        nSubs = tp['nSubs']
        for sub in subs:
            urls = self.praw_dao.search_sub(sub, 'all', 'top')
            if self.db_dao.get_sub(sub) == None:
                self.db_dao.insert_sub({'sub':sub,'nsfw':0})
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'all','sub':sub,'nsfw':0,'nump':30})
            content = self.db_dao.get_url_id(id)
            dayPos.append(content)
        for sub in nSubs:
            urls = self.praw_dao.search_sub(sub, 'all', 'top')
            if self.db_dao.get_sub(sub) == None:
                self.db_dao.insert_sub({'sub':sub,'nsfw':1})
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'all','sub':sub,'nsfw':1,'nump':30})
            content = self.db_dao.get_url_id(id)
            dayNPos.append(content)

        return {'dayPos':str(dayPos),'dayNPos':str(dayNPos)}

    def dayPop(self):
        dayPos = []
        dayNPos = []
        dc = self.praw_dao.downloadList()
        subs = dc['sfw']
        nSubs = dc['nsfw']
        for sub in subs:
            urls = self.praw_dao.search_sub(sub, 'day', 'top')
            if self.db_dao.get_sub(sub) == None:
                self.db_dao.insert_sub({'sub':sub,'nsfw':0})
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':0,'nump':40})
            content = self.db_dao.get_url_id(id)
            dayPos.append(content._asdict())

        for sub in nSubs:
            urls = self.praw_dao.search_sub(sub, 'day', 'top')
            if self.db_dao.get_sub(sub) == None:
                self.db_dao.insert_sub({'sub':sub,'nsfw':1})
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':1,'nump':40})
            content = self.db_dao.get_url_id(id)
            dayNPos.append(content._asdict())

        return  {'dayPos':json.dumps(dayPos),'daynPos': json.dumps(dayNPos)}

    #At the moment not using recents.
    def refresh_dcnt(self):
        today = {'pops':[],'popsN':[],'todays':[],'todaysN':[]}

        self.dailyContent['pops'] = []
        subs = json.loads(self.db_dao.populars(0))
        for sub in subs:
            if sub['sub'] not in self.pastContent['yesterday']['pops'] and sub['sub'] not in self.pastContent['twodays']['>
                self.dailyContent['pops'].append(sub)
                today['pops'].append(sub['sub'])
                if self.dailyContent['pops'].__len__() == 8:
                    break

        self.dailyContent['popsN'] = []
        subs = json.loads(self.db_dao.populars(1))
        for sub in subs:
            if sub['sub'] not in self.pastContent['yesterday']['popsN'] and sub['sub'] not in self.pastContent['twodays'][>
                self.dailyContent['popsN'].append(sub)
                today['popsN'].append(sub['sub'])
                if self.dailyContent['popsN'].__len__() == 8:
                    break

        self.dailyContent['todays'] = []
        dp = self.dayPop()
        dayPos = json.loads(dp['dayPos'])
        for sub in dayPos:
            if sub['sub'] not in self.pastContent['yesterday']['todays'] and sub['sub'] not in self.pastContent['twodays']>
                self.dailyContent['todays'].append(sub)
                today['todays'].append(sub['sub'])
                if self.dailyContent['todays'].__len__() == 8:
                    break

        self.dailyContent['todaysN'] = []
        daynPos = json.loads(dp['daynPos'])
        for sub in daynPos:
            if sub['sub'] not in self.pastContent['yesterday']['todaysN'] and sub['sub'] not in self.pastContent['twodays'>
                self.dailyContent['todaysN'].append(sub)
                today['todaysN'].append(sub['sub'])
                if self.dailyContent['todaysN'].__len__() == 8:
                    break

        self.dailyContent['pops'] = json.dumps(self.dailyContent['pops'])
        self.dailyContent['popsN'] = json.dumps(self.dailyContent['popsN'])
        self.dailyContent['todays'] = json.dumps(self.dailyContent['todays'])
        self.dailyContent['todaysN'] = json.dumps(self.dailyContent['todaysN'])
        self.pastContent['twodays'] = self.pastContent['yesterday']
        self.pastContent['yesterday'] = today
        self.dailyContent['recent'] = self.db_dao.recents(0)
        self.dailyContent['recentN'] = self.db_dao.recents(1)
        print(self.pastContent)

    def dcnt(self):
        today = str(date.today())
        if self.today != today:
            self.refresh_dcnt()
            self.today = today
            f = open("cache.txt", "w")
            new = {'today':str(today),'pastContent':self.pastContent,'dailyContent':self.dailyContent}
            f.write(str(new))
            f.close()

        return self.dailyContent

