from textblob import TextBlob
from datetime import datetime, timedelta
import urllib.request as rq
from pandas_datareader import data as pdr
import praw
import json

class RST():

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

        def intoJson(self):
            return (self.ticker, self.fullName, self.sentiment, self.subjectivity, self.count, self.todayPrice, self.timestamp)

    def __init__(self):
        self.now = datetime.now()
        self.postNo = 50
        self.wordList = {}
        self.time = 'day' # all, hour, day, week, month, year
        self.reddits = ['stocks','pennystocks'] # Stocks to search for e.g. pennystocks, wallstreetbets, stocks
        self.tickers = {}
        self.stocks = {}
        self.blacklist = ['the', 'and', 'of', 'in', 'for','I','i','DD','VERY','very','CEO', 'OUT', 
            'S', 'A', 'ONE', 'ARE', 'FOR', 'KEY', 'AN', 'BY', 'AM', 'W', 'GDP', 'C', 'D', 'PS', 
            'NOW', 'BEST', 'TURN', 'IMO', 'ANY', 'RE', 'NFT', 'LOVE', 'U', 'HAPPY', 'HAD', 'HAS',
            'IRS', 'TELL', 'tell', 'AR', 'MR', 'VALE']
        # self.database = mysql.connector.connect(
        #     host="localhost",
        #     user="root",
        #     passwd="",
        #     database="stock_data"
        # )
        self.reddit = praw.Reddit(
        )
        response = rq.urlopen("https://dumbstockapi.com/stock?format=json&countries=US")
        data = json.loads(response.read())
        for row in data:
            self.tickers[row['ticker']] = row['name']
        print(f"searching subs: {self.reddits}")
        self.scrape()
        print(self.stocks)


    # Scrape Reddit for posts/comments for mentions of stocks and sentiment related to it.
    def scrape(self):
        start = datetime.now()
        for sub in self.reddits:
            subreddit = self.reddit.subreddit(sub)
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
        print(f"Time taken: {datetime.now() - start}")

    # Change sentiment and subjectivity of stock.
    def sentimeter(self, text) :
        senti = TextBlob(text).sentiment
        print(text)
        for word in text.split():
            if word in self.tickers :
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

            


    def updateInfo(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        insert_query = """INSERT INTO stocks () VALUES ($s, $s, $s, $s, $s)"""

if __name__== '__main__':
    rst = RST()
