from ctypes import alignment
from re import M, MULTILINE
import kivy
kivy.require('2.0.0') #kivy version
# from Scraper import Scraper
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.core.window import Window

import threading
import praw
import urllib.request as rq
import youtube_dl as ydl
import requests
import copy
from os import path
from os import makedirs

from praw.reddit import Subreddit

class MainCanvas(Widget):
    ydl_opts = {
        'outtmpl':'/'
    }
    location = '/Users/tkddu/Documents/PS/'
    # pbv = 0
       
    subreddit = ObjectProperty(None)
    subreddits = []
    loc = '/Users/tkddu/Documents/PS/'
    posNum = ObjectProperty(None)
    # time_filter for praw top posts('all', 'hour', 'day', 'week', 'month', 'year') 
    timeFilter = ObjectProperty(None)
    # pb = ProgressBar(value=0, max =100)
    
    def srUpdate(self, instance, value):
        self.subreddits = value.split(",")

    def numUpdate(self, instance, value):
        self.numPos = value

    def timeUpdate(self, instance, value):
        self.tiF = value

    def download(self, url, name):
        print(f"downloading {name}")
        url1 = url.split("?")[0]
        subf = name.split("/")[0]
        extens = url.split(".")[-1]

        if not path.exists(self.location+subf):
            makedirs(self.location+subf)

        if extens == 'gifv':
            print("found a gifv")
            try:
                mark = url.split('/')[-1].split('.')[0]
                cstmopt = copy.copy(self.ydl_opts)
                cstmopt['outtmpl'] = cstmopt['outtmpl']+mark+'.webm'
                with ydl.YoutubeDL(cstmopt) as yd:
                    yd.download([url])
            except:
                print(f"redgif {mark} download failed")            
        if url.split('/')[2] == 'redgifs.com':
            print("found a redgif")
            try:
                r = requests.get(url)
                spl = r.text.split('/')
                num = 88
                for i in range(5):
                    if spl[num+i].rfind('.mp4') != -1:
                        mark = spl[num+i].split('"')[0]
                print('this is url name: '+mark)
                cstmopt = copy.copy(self.ydl_opts)
                cstmopt['outtmpl'] = cstmopt['outtmpl']+mark
                with ydl.YoutubeDL(cstmopt) as yd:
                    yd.download(['https://thumbs2.redgifs.com/'+mark])
            except:
                print(f"redgif {mark} download failed")
        elif 'gallery' in url.split("/"):
            r = requests.get(url)
        else:
            try:
                rq.urlretrieve(url1,str(self.location)+str(name))
            except:
                print("download failed for "+name)

    def cSC1(self):
        self.subreddits = self.subreddit.text.split(",")
        self.ids.pb.max = len(self.subreddits)*int(self.posNum.text)
        reddit = praw.Reddit(client_id='z1eHTSoHlmqgkw', \
                     client_secret='Y3g69V7w6_drdPkfiFenPWb6azh2tQ', \
                     user_agent='stkRadar', \
                     username='Great-Practice3637', \
                     password='satrhdqn19')
        for sub in self.subreddits:
            subreddit = reddit.subreddit(sub)
            print(f"currently in {sub}")
            leng = len(self.ydl_opts['outtmpl'])
            self.ydl_opts['outtmpl'] = self.ydl_opts['outtmpl']+sub+'/'
            topPosts = subreddit.top(time_filter=self.timeFilter.text, limit=int(self.posNum.text))
            for post in topPosts:
                try:
                    url = post.url
                    name = url.split("/")[-1]
                    # name = post.title[:30].rstrip()
                    self.download(url, sub+"/"+name)
                    self.ids.pb.value = self.ids.pb.value + 1
                    print(self.ids.pb.value, self.ids.pb.max)
                except:
                    pass
            self.ydl_opts['outtmpl'] = self.ydl_opts['outtmpl'][0:leng]
            print(leng)

        print("Finished!")
        print("control back to main.py")

    def cSC(self):
        self.ids.pb.value = 0
        x = threading.Thread(target=self.cSC1)
        x.start()

# Instead of using the KV file.
    # def __init__(self, **kwargs):
    #     super(MainCanvas, self).__init__(**kwargs)
    #     self.cols = 1
    #     self.row_default_height = 60
    #     self.row_force_default = True
    #     self.inside = GridLayout(cols=3, row_force_default = True, row_default_height = 30, size_hint_y = .5)
    #     self.add_widget(self.inside)
    #     self.subName = Label(text='Name of Subreddit', size_hint_x=.2)
    #     self.inside.add_widget(self.subName)
    #     self.nofPost = Label(text='# of Posts',size_hint_x=.2)
    #     self.inside.add_widget(self.nofPost)
    #     self.tiFilter = Label(text='Time Filter',size_hint_x=.2)
    #     self.inside.add_widget(self.tiFilter)
    #     self.subreddit = TextInput(text='Earthporn', multiline=False, height = 20)
    #     self.subreddit.bind(text=self.srUpdate)
    #     self.inside.add_widget(self.subreddit)
    #     self.posNum = TextInput(text='30', multiline=False, height = 20)
    #     self.posNum.bind(text=self.numUpdate)
    #     self.inside.add_widget(self.posNum)
    #     self.timeFilter = TextInput(text='month', multiline=False, height = 20)
    #     self.timeFilter.bind(text=self.timeUpdate)
    #     self.inside.add_widget(self.timeFilter)
    #     self.commence = Button(text="Let's do it!")
    #     self.commence.bind(on_press=self.cSC)
    #     self.add_widget(self.pb)
    #     self.add_widget(self.commence)
        
        
    
class Prawscrape(App):
     
    def build(self):
        return MainCanvas()
    

if __name__ == '__main__':
        Prawscrape().run()
