from textblob import TextBlob
from datetime import datetime, timedelta, date
import urllib.request as rq
import praw
from pandas_datareader import data as pdr
import json
import sqlalchemy as sa
from praw_info import prawInfo
import config
import ast

class RSTWorker:

    def __init__(self):
        self.now = datetime.now()
        self.postNo = 10
        self.wordList = {}
        self.time = 'day'
        self.reddits = ['stocks', 'pennystocks']
        self.tickers = {}
        self.tickersCache = []
        self.stocks = {}
        self.blacklist = ['the', 'and', 'of', 'in', 'for','I','i','DD','VERY','very','CEO', 'OUT',
            'S', 'A', 'ONE', 'ARE', 'FOR', 'KEY', 'AN', 'BY', 'AM', 'W', 'GDP', 'C', 'D', 'PS',
            'NOW', 'BEST', 'TURN', 'IMO', 'ANY', 'RE', 'NFT', 'LOVE', 'U', 'HAPPY', 'HAD', 'HAS',
            'IRS', 'TELL', 'tell', 'AR', 'MR', 'VALE', 'UN', 'EV', 'PE', 'ATH', 'IP', 'IT', 'USA', 
            'Go', 'GO', 'COST', 'Cost', 'PM', 'It', 'it', 'TV', 'BIG', 'SHOP', 'REAL', 'GSAT', 'AT',
            'V', 'DL', 'PER']
        response = rq.urlopen("https://dumbstockapi.com/stock?format=json&countries=US")
        data = json.loads(response.read())
        for row in data:
            row['ticker'] = row['ticker'].replace('.','-')
        for row in data:
            self.tickers[row['ticker']] = row['name']

        #DB
        self.db = sa.create_engine(config.DB_URL, encoding = 'utf-8', max_overflow = 0)

        #Praw
        self.praw = praw.Reddit(client_id=prawInfo['client_id'], \
            client_secret=prawInfo['client_secret'], \
            user_agent=prawInfo['user_agent'], \
            username=prawInfo['username'], \
            password=prawInfo['password'])

        #Checking local cache for Ticker List
        f = open("/home/ubuntu/RUD/RUD/sicache.txt")
        text = f.read()
        if text == '':
            print("Empty Stock Info Cache")
        else:
            self.tickersCache = ast.literal_eval(text)
            f.close()
            print('Stock Cache useable')
        self.scrape()

        #Daily Content
        self.dailyContent = {'recent':[],'recentN':[],'pops':[],'popsN':[],'todays':[],'todaysN':[]}
        self.pastContent = {'yesterday':{'pops':[],'popsN':[],'todays':[],'todaysN':[]},'twodays':{'pops':[],'popsN':[],'todays':[],'todaysN':[]}}
        self.refresh_dcnt()

    class Stock():
        def __init__(self, ticker, fullName, sentiment, subjectivity, count):
            self.ticker = ticker
            self.fullName = fullName
            self.sentiment = sentiment
            self.subjectivity = subjectivity
            self.count = count
            self.todayPrice = 0
            self.timestamp = 0
            self.volume = 0

        def __str__(self):
            return self.ticker + " " + self.fullName + " " + str(self.sentiment) + " " + str(self.subjectivity) + " " + str(self.count) + " " + str(self.todayPrice) + " " + str(self.timestamp) + " " + str(self.volume)

        def __repr__(self):
            return self.ticker + " " + self.fullName + " " + str(self.sentiment) + " " + str(self.subjectivity) + " " + str(self.count) + " " + str(self.todayPrice) + " " + str(self.timestamp) + " " + str(self.volume)

        def __eq__(self, other):
            return self.ticker == other.ticker

        def __hash__(self):
            return hash(self.ticker)

        def toDict(self):
            return {"ticker":self.ticker, "fullName":self.fullName, "sentiment":self.sentiment, "subjectivity":self.subjectivity, "count":self.count, "todayPrice":self.todayPrice, "timestamp":self.timestamp, "volume":self.volume}

    def dateToDT(self):
        todate = str(date.today()-timedelta(days=29))
        tdate = str(date.today())
        dates = [todate+" 00:00:00", tdate+" 23:59:59"]
        return dates

    def scrape(self):
        start = datetime.now()
        for sub in self.reddits:
            subreddit = self.praw.subreddit(sub)
            topPosts = subreddit.top(time_filter=self.time, limit=self.postNo)
            for post in topPosts:
                self.sentimeter(post.title)
                self.sentimeter(post.selftext)
                post.comments.replace_more(limit=None)
                comment_queue = post.comments[:]
                while comment_queue:
                    comment = comment_queue.pop(0)
                    self.sentimeter(comment.body)
                    comment_queue.extend(comment.replies)
        for stock in self.stocks:
            count = self.stocks[stock].count
            self.stocks[stock].sentiment /= count
            self.stocks[stock].subjectivity /= count
            self.stocks[stock].sentiment = round(self.stocks[stock].sentiment, 2)
            self.stocks[stock].subjectivity = round(self.stocks[stock].subjectivity, 2)
        self.updateTickersBatch()
        print(f"Time took: {datetime.now() - start}")
        try:
            print(f"Upload successful, last row id: {self.insertSI()}")
        except Exception as e:
            print(f"upload to DB failed: {e}")
        print(self.stocks)
        print(self.fetchSI())


    # Check sentiment and subjectivity of stock.
    def sentimeter(self, text) :
        senti = TextBlob(text).sentiment
        print(text)
        for word in text.split():
            if word in self.tickers :
                if word in self.blacklist:
                    continue
                if word in self.tickersCache:
                    pass
                else:
                    self.tickersCache.append(word)
                if word in self.stocks:
                    stock = self.stocks[word]
                    stock.sentiment += senti.polarity
                    stock.subjectivity += senti.subjectivity
                    stock.count += 1
                else:
                    stock = self.Stock(word, self.tickers[word], senti.polarity, senti.subjectivity, 1)
                    stock.timestamp = self.now
                    self.stocks[word] = stock

    # Using Yahoo's finance API, updates closed price and volume for collected stocks in batch and saves list of tickers to sicache.txt
    def updateTickersBatch(self):
        try:
            tickerList = pdr.DataReader(
                self.tickersCache,
                start = self.now-timedelta(days=1),
                end = self.now,
                data_source='yahoo')

            # Replacing NaN with 0 to prevent error during DB Insertion
            tickerList = tickerList.fillna(0)

            weekday = date.today().weekday()
            print(f"Today's weekday number is:{weekday}. Start is:{self.now-timedelta(days=1)}")
            if weekday < 5:
                print("Not Weekend")
                for ticker in self.tickersCache:
                    if ticker in self.stocks:
                        self.stocks[ticker].volume = tickerList.iloc[0]['Volume'][ticker]
                        self.stocks[ticker].todayPrice = tickerList.iloc[0]['Adj Close'][ticker]
                        self.stocks[ticker].timestamp = self.now
                    else:
                        self.stocks[ticker] = self.Stock(ticker, self.tickers[ticker], 0, 0, 0)
                        self.stocks[ticker].volume = tickerList.iloc[0]['Volume'][ticker]
                        self.stocks[ticker].todayPrice = tickerList.iloc[0]['Adj Close'][ticker]
                        self.stocks[ticker].timestamp = self.now
            else:
                for ticker in self.tickersCache:
                    self.stocks[ticker].volume = 0
                    self.stocks[ticker].todayPrice = 0
        except Exception as e:
            print(f"Yahoo api error: {e}")
        print(tickerList)
        f = open("/home/ubuntu/RUD/RUD/sicache.txt", "w")
        f.write(str(self.tickersCache))
        f.close()

    ##DB Functions

        ###RST###

    # Multiple Stock rows Insertion
    def insertSI(self):
        dicts = []
        for stock in self.stocks:
            dicts.append(self.stocks[stock].toDict())
        with self.db.connect() as connection:
            return connection.execute(sa.text("""
                INSERT INTO stocks (
                    ticker,
                    fullName,
                    sentiment,
                    subjectivity,
                    count,
                    price,
                    timestamp,
                    volume
                ) VALUES (
                    :ticker,
                    :fullName,
                    :sentiment,
                    :subjectivity,
                    :count,
                    :todayPrice,
                    :timestamp,
                    :volume
                    )
            """), dicts).lastrowid

    # Grab a month long stock info
    def fetchSI(self):
        date = self.dateToDT()
        with self.db.connect() as connection:
            return connection.execute(sa.text("""
                SELECT
                    ticker,
                    fullName,
                    sentiment,
                    subjectivity,
                    count,
                    price,
                    volume,
                    timestamp
                FROM
                    stocks
                WHERE
                    timestamp >= :dateA AND timestamp <= :dateB
                ORDER BY
                    timestamp DESC
            """), {'dateA':date[0], 'dateB':date[1]}).fetchall()


        ###RUD###

    #Popular posts based on the popular subs. Grab 5 subs with most hits -> Grab the url with most hits of each.
    def populars(self, nsfw):
        populars = []

        pnsubs = self.db.execute(sa.text("""
            SELECT
                sub
            FROM
                subs
            WHERE
                nsfw = :pnsfw
            ORDER BY
                hits DESC
            LIMIT
                24
            """),{'pnsfw':nsfw}).fetchall()
        for pnsub in pnsubs:
            content = self.db.execute(sa.text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                sub = :subn
            ORDER BY
                hits DESC
            """),{'subn':pnsub['sub']}).fetchone()
            populars.append(content._asdict())
        return json.dumps(populars)

    #Recently Grab Recenly Added URLs
    def recents(self, nsfw):
        recents = []
        content = self.db.execute(sa.text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                nsfw = :pnsfw
            ORDER BY
                id DESC
            LIMIT
                8
        """),{'pnsfw':nsfw}).fetchall()
        for post in content:
            recents.append(post._asdict())
        return json.dumps(recents)

    #Looks for sub in DB
    def get_sub(self, sub):
        subn = self.db.execute(sa.text("""
        SELECT
            sub
        FROM subs
        WHERE sub = :sub_name
        """), {
            'sub_name' : sub
        }).fetchone()
        return subn

    def insert_sub(self, sub):
        return self.db.execute(sa.text("""
            INSERT INTO subs (
                sub,
                nsfw
            ) VALUES (
                :sub,
                :nsfw
            )
        """), sub).lastrowid

    def insert_url(self, url):
        return self.db.execute(sa.text("""
            INSERT INTO urls (
                urls,
                type,
                time,
                nump,
                sub,
                nsfw
            ) VALUES (
                :urls,
                :type,
                :time,
                :nump,
                :sub,
                :nsfw
            )
        """), url).lastrowid

    def get_url_id(self, id):
        content = self.db.execute(sa.text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM urls
            WHERE id = :pid
        """),{'pid':id}).fetchone()

        return content


    #Based on Reddit Ranking Website, search the list of popular subs using the API adds the content to DB
    def dayPop(self):
        dayPos = []
        dayNPos = []
        dc = self.downloadList()
        subs = dc['sfw']
        nSubs = dc['nsfw']
        for sub in subs:
            urls = self.search_sub(sub, 'day', 'top')
            if self.get_sub(sub) == None:
                self.insert_sub({'sub':sub,'nsfw':0})
            id = self.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':0,'nump':40})
            content = self.get_url_id(id)
            dayPos.append(content._asdict())

        for sub in nSubs:
            urls = self.search_sub(sub, 'day', 'top')
            if self.get_sub(sub) == None:
                self.insert_sub({'sub':sub,'nsfw':1})
            id = self.insert_url({'urls':str(urls), 'type':'top','time':'day','sub':sub,'nsfw':1,'nump':40})
            content = self.get_url_id(id)
            dayNPos.append(content._asdict())

        return  {'dayPos':json.dumps(dayPos),'daynPos': json.dumps(dayNPos)}

    #Finds top  5 of SFW and NSFW subs from Redditlist.
    def downloadList(self):
        sfw = str(rq.urlopen('http://redditlist.com/sfw').read())
        nsfw = str(rq.urlopen('http://redditlist.com/nsfw').read())

        sfwtemp = sfw.split('listing-header">Subscribers')
        sfwtemp = sfwtemp[1].split("data-target-subreddit=\\\'")
        sfws = []
        print(len(sfwtemp))
        for i in range(24):
            sfws.append(sfwtemp[i+2].split("\\\' data-target-filter")[0])

        nsfwtemp = nsfw.split('listing-header">Subscribers')
        nsfwtemp = nsfwtemp[1].split("data-target-subreddit=\\\'")
        nsfws = []
        for i in range(24):
            nsfws.append(nsfwtemp[i+1].split("\\\' data-target-filter")[0])

        sfwgtemp = sfw.split('listing-header">Growth')
        sfwgtemp = sfwgtemp[1].split("data-target-subreddit=\\\'")
        sfwg = []
        for i in range(24):
            sfwg.append(sfwgtemp[i+1].split("\\\' data-target-filter")[0])

        nsfwgtemp = nsfw.split('listing-header">Growth')
        nsfwgtemp = nsfwgtemp[1].split("data-target-subreddit=\\\'")
        nsfwg = []
        for i in range(24):
            nsfwg.append(nsfwgtemp[i+1].split("\\\' data-target-filter")[0])

        return {'sfw':sfws,'nsfw':nsfws, 'sfwg':sfwg, 'nsfwg':nsfwg}

    #Returns URLs of media in a subreddit
    def search_sub(self, sub, tim, type, num = 30):
        urls = []
        subred = self.praw.subreddit(sub)
        if type == 'top':
            posts = subred.top(time_filter=tim, limit=num)
        elif type == 'new':
            posts = subred.new(limit = num)
        elif type == 'hot':
            posts = subred.hot(limit = num)
        for post in posts:
            try:
                urls.append(post.url)
            except:
                print("failed")
                pass
        return urls

    #At the moment not using recents.
    def refresh_dcnt(self):
        with open("/home/ubuntu/RUD/RUD/past_content.json", "r") as file:
            self.pastContent = json.load(file)
        today = {'pops':[],'popsN':[],'todays':[],'todaysN':[]}

        self.dailyContent['pops'] = []
        subs = json.loads(self.populars(0))
        for sub in subs:
            if sub['sub'] not in self.pastContent['yesterday']['pops'] and sub['sub'] not in self.pastContent['twodays']['pops']:
                self.dailyContent['pops'].append(sub)
                today['pops'].append(sub['sub'])
                if self.dailyContent['pops'].__len__() == 8:
                    break

        self.dailyContent['popsN'] = []
        subs = json.loads(self.populars(1))
        for sub in subs:
            if sub['sub'] not in self.pastContent['yesterday']['popsN'] and sub['sub'] not in self.pastContent['twodays']['popsN']:
                self.dailyContent['popsN'].append(sub)
                today['popsN'].append(sub['sub'])
                if self.dailyContent['popsN'].__len__() == 8:
                    break

        dp = self.dayPop()
        self.dailyContent['todays'] = []
        dayPos = json.loads(dp['dayPos'])
        for sub in dayPos:
            if sub['sub'] not in self.pastContent['yesterday']['todays'] and sub['sub'] not in self.pastContent['twodays']['todays']:
                self.dailyContent['todays'].append(sub)
                today['todays'].append(sub['sub'])
                if self.dailyContent['todays'].__len__() == 8:
                    break

        self.dailyContent['todaysN'] = []
        daynPos = json.loads(dp['daynPos'])
        for sub in daynPos:
            if sub['sub'] not in self.pastContent['yesterday']['todaysN'] and sub['sub'] not in self.pastContent['twodays']['todaysN']:
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
        self.dailyContent['recent'] = self.recents(0)
        self.dailyContent['recentN'] = self.recents(1)
        with open("/home/ubuntu/RUD/RUD/past_content.json","w") as file:
            file.write(json.dumps(self.pastContent))
        with open("/home/ubuntu/var/www/rud.com/dcnt.json","w") as file:
            file.write(json.dumps(self.dailyContent))
        print(self.pastContent)

if __name__ == "__main__":
    RSTWorker()
