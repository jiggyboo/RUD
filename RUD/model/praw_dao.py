import praw
import requests
from praw_info import prawInfo

class PrawDao:
    def __init__(self):
        self.praw = praw.Reddit(client_id=prawInfo['client_id'], \
            client_secret=prawInfo['client_secret'], \
            user_agent=prawInfo['user_agent'], \
            username=prawInfo['username'], \
            password=prawInfo['password'])

    def is_18(self, sub):
        sub = self.praw.subreddit(sub)
        return sub.over18

    def returnPraw(self):
        return self.praw

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
                print("adding url failed")
                pass
        return str(urls)

    #Given the URL of Cyberdrop post, returns downloadable urls of each items in the gallery.
    def search_cd(self, url):
        print(f'title is {url}')
        r = requests.get(url).text
        try:
            title = r.split('" class="title has-text-centered" title="')[1].split('">')[0]
            urls = []
            pics = r.split('downloadUrl: "')
            for durl in pics[1:]:
                urls.append(durl.split('",\n')[0])
            vids = r.split('mp4" data-html')
            for vurl in vids[1:]:
                vvurl = vurl.split('href="')[1]
                url = vvurl.split('" target=')[0]
                urls.append(url)
            vids = r.split('<a class="image" href="')
            for vurl in vids[1:]:
                vvurl = vurl.split('" target="')[0]
                if vvurl[-3:] == 'mov':
                    urls.append(vvurl)
                if vvurl[-3:] == 'mp4' and vvurl not in urls:
                    urls.append(vvurl)
            print(len(urls))
        except:
            return "Page No Longer Available/Parsing Fail"

        return {'title':title,'urls':str(urls)}

    #Finds top 5 of non-NSFW and NSFW subs from the currently hot subs on reddit.
    def topFive(self):
        all = self.praw.subreddit('all').hot(limit=100)
        subs = set()
        nSubs = set()
        for post in all:
            sub = post.subreddit
            if sub.over18:
                if len(nSubs)<5:
                    nSubs.add(str(sub))
            elif len(subs)<5:
                subs.add(str(sub))
            if len(subs) == 5 and len(nSubs) == 5:
                break

        return {'subs':list(subs),'nSubs':list(nSubs)}

    #Finds top  5 of SFW and NSFW subs from Redditlist.
    def downloadList(self):
        sfw = requests.get('http://redditlist.com/sfw').text
        nsfw = requests.get('http://redditlist.com/nsfw').text

        sfwtemp = sfw.split('listing-header">Subscribers')
        sfwtemp = sfwtemp[1].split("data-target-subreddit='")
        sfws = []
        for i in range(24):
            sfws.append(sfwtemp[i+2].split("' data-target-filter")[0])

        nsfwtemp = nsfw.split('listing-header">Subscribers')
        nsfwtemp = nsfwtemp[1].split("data-target-subreddit='")
        nsfws = []
        for i in range(24):
            nsfws.append(nsfwtemp[i+1].split("' data-target-filter")[0])

        sfwgtemp = sfw.split('listing-header">Growth')
        sfwgtemp = sfwgtemp[1].split("data-target-subreddit='")
        sfwg = []
        for i in range(24):
            sfwg.append(sfwgtemp[i+1].split("' data-target-filter")[0])

        nsfwgtemp = nsfw.split('listing-header">Growth')
        nsfwgtemp = nsfwgtemp[1].split("data-target-subreddit='")
        nsfwg = []
        for i in range(24):
            nsfwg.append(nsfwgtemp[i+1].split("' data-target-filter")[0])

        return {'sfw':sfws,'nsfw':nsfws, 'sfwg':sfwg, 'nsfwg':nsfwg}

