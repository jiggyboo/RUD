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

    # Cache for Daily Info to be served for RST
    def rstDCNT(self):
        dcnt = self.db_dao.grabdata()
        return dcnt
