import praw
import urllib.request as rq
import youtube_dl as ydl
import requests
import copy
from os import path
from os import makedirs

from praw.reddit import Subreddit

class Scraper():
    ydl_opts = {
        'outtmpl':'/'
    }
    vids = []
    location = '/Users/tkddu/Documents/PS/'
    pbv = 0
    # time_filter for praw top posts('all', 'hour', 'day', 'week', 'month', 'year')    

    def scrape(self, subreddits, pb, numPost=10, time='day'):
        reddit = praw.Reddit(client_id='z1eHTSoHlmqgkw', \
                     client_secret='Y3g69V7w6_drdPkfiFenPWb6azh2tQ', \
                     user_agent='stkRadar', \
                     username='Great-Practice3637', \
                     password='satrhdqn19')
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            print(f"currently in {sub}")
            leng = len(self.ydl_opts['outtmpl'])
            self.ydl_opts['outtmpl'] = self.ydl_opts['outtmpl']+sub+'/'
            topPosts = subreddit.top(time_filter=time, limit=numPost)
            for post in topPosts:
                try:
                    url = post.url
                    name = url.split("/")[-1]
                    print(url)
                    # name = post.title[:30].rstrip()
                    self.download(url, sub+"/"+name)
                    self.pbv +=1
                    pb.value = pb.value + 1
                    print(pb.value, pb.max)
                except:
                    pass
            self.ydl_opts['outtmpl'] = self.ydl_opts['outtmpl'][0:leng]
            print(leng)

        print("Finished!")

    def download(self, url, name):
        url1 = url.split("?")[0]
        subf = name.split("/")[0]
        extens = url.split(".")[-1]
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
            if not path.exists(self.location+subf):
                makedirs(self.location+subf)
            try:
                rq.urlretrieve(url1,str(self.location)+str(name))
            except:
                print("download failed for "+name)
        

        
        