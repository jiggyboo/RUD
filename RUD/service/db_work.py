from flask import jsonify
import json
import jwt
import bcrypt
from datetime import datetime, timedelta

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
                    return {'result':"Page No Longer Available",'recent':recent}
                title = rurl['title']
                urls = rurl['urls']
                id = self.db_dao.insert_cd({'title':title, 'urls': urls, 'url': url})
                return {'result':json.dumps({'id':id, 'title':title,'urls': urls}),'recent':recent}
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

    ## User Info Manipulation

    def create_user(self, user_info):
        hashed_password = bcrypt.hashpw(user_info['password'].encode('utf-8'), bcrypt.gensalt())
        user_id = self.db_dao.insert_user({
            'email': user_info['email'], 
            'password': hashed_password, 
            'name': user_info['name']
        })
        
        return user_id

    def login(self, credential):
        email = credential['email']
        password = credential['password']
        user_credential = self.db_dao.get_user_id_password(email)
        authorized = user_credential and bcrypt.checkpw(password.encode('utf-8'), user_credential['password'].encode('utf-8'))

        return authorized

    def generate_token(self, user_id):
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(minutes=60*24)
        }
        token = jwt.encode(payload, self.config['JWT_SECRET_KEY'], algorithm='HS256')

        return token.decode('utf-8')

    def get_user_id_and_password(self, email):

        return self.db_dao.get_user_id_password(email)

    def follow_stock(self, user_id, ticker):

        return self.db_dao.follow({'ticker': ticker, 'user_id': user_id})

    def unfollow_stock(self, user_id, ticker):

        return self.db_dao.unfollow({'ticker': ticker, 'user_id': user_id})
    
    def fetch_personal(self, user_id):
        
        follows = json.load(self.db_dao.fetchFollowing(user_id))
        self.personalContent = {}
        for f in follows:
            self.personalContent[f['ticker']] = []
        data = self.db_dao.fetchSI_personal(user_id)
        for d in data:
            self.personalContent[d['ticker']].append(d)

        return self.personalContent
