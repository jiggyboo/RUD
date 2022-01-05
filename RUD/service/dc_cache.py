from datetime import date
import json

class DailyContentCache:

    def __init__(self, db_dao, praw_dao):
        self.db_dao = db_dao
        self.praw_dao = praw_dao
        self.dailyContent = {'recent':[],'recentN':[],'pops':[],'popsN':[],'todays':[],'todaysN':[]}
        self.today = date.today()
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
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':0,'nump':30})
            content = self.db_dao.get_url_id(id)
            dayPos.append(content._asdict())

        for sub in nSubs:
            urls = self.praw_dao.search_sub(sub, 'day', 'top')
            if self.db_dao.get_sub(sub) == None:
                self.db_dao.insert_sub({'sub':sub,'nsfw':1})
            id = self.db_dao.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':1,'nump':30})
            content = self.db_dao.get_url_id(id)
            dayNPos.append(content._asdict())

        return  {'dayPos':json.dumps(dayPos),'daynPos': json.dumps(dayNPos)}

    def refresh_dcnt(self):
        self.dailyContent['recent'] = self.db_dao.recents(0)
        self.dailyContent['recentN'] = self.db_dao.recents(1)
        self.dailyContent['pops'] = self.db_dao.populars(0)
        self.dailyContent['popsN'] = self.db_dao.populars(1)
        dp = self.dayPop()
        self.dailyContent['todays'] = dp['dayPos']
        self.dailyContent['todaysN'] = dp['daynPos']

    def dcnt(self):
        self.refresh_dcnt() if self.today != date.today() else None
        self.today = date.today()
        print(self.dailyContent)
        return self.dailyContent
