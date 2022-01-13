from flask import jsonify
import json

class DatabaseWork:

    def __init__(self, db_dao, praw_dao):
        self.db_dao = db_dao
        self.praw_dao = praw_dao

    def search(self, sub, num, tim, typ):
        rurl = {}
        if tim == '':
            url = self.db_dao.get_url({'sub':sub,'stype':typ})
        else:
            url = self.db_dao.getT_url({'sub':sub,'stype':typ,'stim':tim})
        if url == None:
            print("URL NOT FOUND")
            if self.db_dao.get_sub(sub) == None:
                print(f"SUB {sub} NOT FOUND")
                self.db_dao.insert_sub({'sub':sub,'nsfw':int(self.praw_dao.is_18(sub))})
            else:
                print("SUB FOUND")
                self.db_dao.increment_hits_sub(sub)
            rurl = self.praw_dao.search_sub(sub, tim, typ, num)
            id = self.db_dao.insert_url({'urls':str(rurl),'type':typ,'time':tim,'nump':num,'sub':sub,'nsfw':int(self.praw_dao.is_18(sub))})

        else:
            print("URL FOUND, sub and url hitcounts incremented")
            rurl = url['urls']
            self.db_dao.increment_hits_sub(sub)
            self.db_dao.increment_hits_url(url['id'])
            id = url['id']
        tf = self.db_dao.topFive(sub)

        return {'result':json.dumps({'id':id,'url':rurl}),'tf':tf}

    def cd(self, url):
        rurl = {}
        if url[0:4] == 'http':
            print("CD URL SEARCH")
            cdb = self.db_dao.get_cd(url)
            if cdb == None:
                print("URL NOT FOUND")
                rurl = self.praw_dao.search_cd(url)
                recent = self.db_dao.recentCD()
                if rurl == "Page No Longer Available/Parsing Fail":
                    return {'result':"Page No Longer Available", 'recent':recent}
                title = rurl['title']
                urls = rurl['urls']
                id = self.db_dao.insert_cd({'title':title, 'urls': urls, 'url': url})
                return {'result':json.dumps({'id':id, 'title':title,'url': urls}),'recent':recent}
            else:
                print("URL FOUND, cd hitcount incremented")
                id = cdb['id']
                self.db_dao.increment_hits_cd(id)
                title = cdb['title']
                urls = cdb['urls']
                recent = self.db_dao.recentCD()
                return {'result':json.dumps({'id':id, 'title':title,'urls': urls}),'recent':recent}

        else:
            print("CD TITLE SEARCH")
            cdb = self.db_dao.topFiveCD(url)
            if cdb == None:
                print("QUERY NOT FOUND")
                recent = self.db_dao.recentCD()
                return {'result':"QUERY NOT FOUND",'recent':recent}
            else:
                print("QUERY FOUND")
                recent = self.db_dao.recentCD()
                return {'result':cdb,'recent':recent}


                





