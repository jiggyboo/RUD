from textblob import TextBlob
from datetime import datetime, timedelta
import urllib.request as rq
import praw
from pandas_datareader import data as pdr
import json

class RSTWorker:
    def __init__(self, db_dao, praw_dao):
        self.db_dao = db_dao
        self.praw_dao = praw_dao
        self.now = datetime.now()
        self.postNo = 50
        self.wordList = {}
        self.time = 'day'
        self.reddits = ['stocks', 'pennystocks']
        self.tickers = {}
        self.tickersCache = []
        self.stocks = {}
        self.blacklist = ['the', 'and', 'of', 'in', 'for','I','i','DD','VERY','very','CEO', 'OUT', 
            'S', 'A', 'ONE', 'ARE', 'FOR', 'KEY', 'AN', 'BY', 'AM', 'W', 'GDP', 'C', 'D', 'PS', 
            'NOW', 'BEST', 'TURN', 'IMO', 'ANY', 'RE', 'NFT', 'LOVE', 'U', 'HAPPY', 'HAD', 'HAS',
            'IRS', 'TELL', 'tell', 'AR', 'MR', 'VALE']
        response = rq.urlopen("https://dumbstockapi.com/stock?format=json&countries=US")
        data = json.loads(response.read())
        for row in data:
            self.tickers[row['ticker']] = row['name']

        f = open("sicache.txt")
        text = f.read()
        if text == '':
            print("Empty Stock Info Cache")
        else:
            self.tickersCache = ast.literal_eval(text)
            f.close()
            print('Stock Cache useable')

    class Stock():
        def __init__(self, ticker, fullName, sentiment, subjectivity, count):
            self.ticker = ticker
            self.fullName = fullName
            self.sentiment = sentiment
            self.subjectivity = subjectivity
            self.count = count
            self.todayPrice = 0
            self.timestamp = 0

        def __str__(self):
            return self.ticker + " " + self.fullName + " " + str(self.sentiment) + " " + str(self.subjectivity) + " " + str(self.count) + " " + str(self.todayPrice) + " " + str(self.timestamp)

        def __repr__(self):
            return self.ticker + " " + self.fullName + " " + str(self.sentiment) + " " + str(self.subjectivity) + " " + str(self.count) + " " + str(self.todayPrice) + " " + str(self.timestamp)

        def __eq__(self, other):
            return self.ticker == other.ticker

        def __hash__(self):
            return hash(self.ticker)

        def toDict(self):
            return {"ticker":self.ticker, "fullName":self.fullName, "sentiment":self.sentiment, "subjectivity":self.subjectivity, "count":self.count, "price":self.todayPrice, "timestamp":self.timestamp}

    def scrape(self):
        start = datetime.now()
        praw = self.praw_dao.returnPraw()
        for sub in self.reddits:
            subreddit = praw.subreddit(sub)
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
            self.stocks[stock].timestamp = self.now
        self.updateTickers()
        print(f"Time took: {datetime.now() - start}")
        try:
            self.updateDB()
        except Exception as e:
            print(f"upload to DB failed: {e}")
        print(self.stocks)

    # Change sentiment and subjectivity of stock.
    def sentimeter(self, text) :
        senti = TextBlob(text).sentiment
        print(text)
        for word in text.split():
            if word in self.tickers :
                if word in self.tickersCache:
                    pass
                else:
                    self.tickersCache.append(word)
                if word in self.blacklist:
                    continue
                if word in self.stocks:
                    stock = self.stocks[word]
                    stock.sentiment += senti.polarity
                    stock.subjectivity += senti.subjectivity
                    stock.count += 1
                else:
                    stock = self.Stock(word, self.tickers[word], senti.polarity, senti.subjectivity, 1)
                    self.stocks[word] = stock
                if self.stocks[word].todayPrice == 0:
                    try:
                        self.stocks[word].todayPrice = pdr.DataReader(
                            word,
                            start=self.now-timedelta(days=1),
                            end=self.now,
                            data_source='yahoo')['Close'][-1]
                        print(self.stocks[word])
                    except:
                        print("No price data for " + word)

    # Insert Updated Stock Info to the database
    def updateDB(self) :
        dicts = []
        for stock in self.stocks:
            dicts.append(stock.toDict())
        self.db_dao.insertSI(dicts)

    # Update Local Tickers List
    def updateTickers(self):
        for ticker in self.tickersCache:
            if ticker in self.stocks:
                continue
            else:
                self.stocks[ticker] = self.Stock(ticker, self.tickers[ticker], 0, 0, 0)
                self.stocks[ticker].todayPrice = pdr.DataReader(
                    ticker,
                    start=self.now-timedelta(days=1),
                    end=self.now,
                    data_source='yahoo')['Close'][-1]
        f = open("sicache.txt", "w")
        f.write(str(self.tickersCache))

    # Cache for Daily Info to be served for RST
    def rstDCNT(self):

        return dcnt


