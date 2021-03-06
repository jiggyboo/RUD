import praw
import requests
from praw_info import prawInfo



praw = praw.Reddit(client_id=prawInfo['client_id'], \
    client_secret=prawInfo['client_secret'], \
    user_agent=prawInfo['user_agent'], \
    username=prawInfo['username'], \
    password=prawInfo['password'])

def is_18(self, sub):
    sub = self.praw.subreddit(sub)
    return sub.over18

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
            url = post.url
            extens = url.split(".")[-1]
            if extens == 'jpg' or extens == 'png':
                urls.append(url)
            elif extens == 'gifv':
                urls.append(url)
            elif url.split('/')[2] == 'redgifs.com':
                try:
                    r = requests.get(url)
                    spl = r.text.split('/')
                    num = 88
                    for i in range(5):
                        if spl[num+i].rfind('.mp4') != -1:
                            mark = spl[num+i].split('"')[0]
                    url = 'https://thumbs2.redgifs.com/'+mark
                    urls.append(url)
                except:
                    pass
        except:
            print("failed")
            pass
    return urls

#Given the URL of Cyberdrop post, returns downloadable urls of each items in the gallery.
def downloadCD(url):
    r = requests.get(url).text
    urls = []
    pics = r.split('downloadUrl: "')
    for durl in pics[1:]:
        urls.append(durl.split('",\n')[0])
    vids = r.split('mp4" data-html')
    for vurl in vids[1:]:
        vvurl = vurl.split('href="')[1]
        url = vvurl.split('" target=')[0]
        urls.append(url)
    print(len(urls))

    return urls


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

    return {'subs':list(subs),'nSubs':list(nSubs)}


def downloadList():
    sfw = requests.get('http://redditlist.com/sfw').text
    nsfw = requests.get('http://redditlist.com/nsfw').text

    sfwtemp = sfw.split('listing-header">Subscribers')
    sfwtemp = sfwtemp[1].split("data-target-subreddit='")
    sfws = []
    print(len(sfwtemp))
    for i in range(5):
        sfws.append(sfwtemp[i+2].split("' data-target-filter")[0])

    nsfwtemp = nsfw.split('listing-header">Subscribers')
    nsfwtemp = nsfwtemp[1].split("data-target-subreddit='")
    nsfws = []
    print(len(nsfwtemp))
    for i in range(5):
        nsfws.append(nsfwtemp[i+1].split("' data-target-filter")[0])

    sfwgtemp = sfw.split('listing-header">Growth')
    sfwgtemp = sfwgtemp[1].split("data-target-subreddit='")
    sfwg = []
    print(len(sfwgtemp))
    for i in range(5):
        sfwg.append(sfwgtemp[i+1].split("' data-target-filter")[0])

    nsfwgtemp = nsfw.split('listing-header">Growth')
    nsfwgtemp = nsfwgtemp[1].split("data-target-subreddit='")
    nsfwg = []
    print(len(nsfwgtemp))
    for i in range(5):
        nsfwg.append(nsfwgtemp[i+1].split("' data-target-filter")[0])

    return {'sfw':sfws,'nsfw':nsfws, 'sfwg':sfwg, 'nsfwg':nsfwg}


print(downloadList())