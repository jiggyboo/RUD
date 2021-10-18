from datetime import date
from flask import jsonify

class DatabaseWork:

    def __init__(self, db_dao, praw_dao):
        self.db_dao = db_dao
        self.praw_dao = praw_dao

    def search(self, sub, num, tim, typ, dated):
        rurl = {}
        if tim == '':
            url = self.db_dao.get_url({'sub':sub,'stype':typ,'sdate':dated})
        else:
            url = self.db_dao.getT_url({'sub':sub,'stype':typ,'sdate':dated,'stim':tim})
        if url == None:
            print("URL NOT FOUND")
            if self.db_dao.get_sub(sub) == None:
                print("SUB NOT FOUND")
                self.db_dao.insert_sub(jsonify({'sub':sub,'nsfw':int(self.praw_dao.is_18(sub))}))
            else:
                print("SUB FOUND")
                self.db_dao.increment_hits_sub(sub)
            rurl = self.db_dao.search_sub(sub, tim, num, typ)
            self.db_dao.insert_url({'urls':rurl,'type':typ,'time':tim,'nump':num,'sub':sub,'nsfw':int(self.praw_dao.is_18(sub))})
        else:
            print("URL FOUND, sub and url hitcounts incremented")
            rurl = url['urls']
            self.db_dao.increment_hits_sub(sub)
            self.db_dao.increment_hits_url(rurl['id'])

        return jsonify({'url':rurl})

