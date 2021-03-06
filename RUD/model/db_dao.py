import json
from sqlalchemy import text
from datetime import date, timedelta

class DatabaseDao:
    def __init__(self, database):
        self.db = database

    def dateToDT(self):
        tdate = str(date.today())
        dates = [tdate+" 00:00:00", tdate+" 23:59:59"]
        return dates

    def getToDate(self):
        tdate = date.today()
        todate = str(tdate-timedelta(days=29))
        dates = [todate+" 00:00:00", str(tdate)+" 23:59:59"]
        return dates
        
    def getT_url(self, url):
        sdate = self.dateToDT()
        rurl = self.db.execute(text("""
            SELECT
                id,
                urls
            FROM urls
            WHERE sub = :sub_name AND type = :url_type AND created_at >= :url_dateA AND created_at <= :url_dateB AND time = :url_time
            """), {
                'sub_name' : url['sub'],
                'url_type' : url['stype'],
                'url_dateA' : sdate[0],
                'url_dateB' : sdate[1],
                'url_time' : url['stim']
            }).fetchone()

        return {
            'id' : rurl['id'],
            'sub' : url['sub'],
            'urls' : rurl['urls']
        } if rurl else None

    def get_url(self, url):
        sdate = self.dateToDT()
        rurl = self.db.execute(text("""
            SELECT
                id,
                urls
            FROM urls
            WHERE sub = :sub_name AND type = :url_type AND created_at >= :url_dateA AND created_at <= :url_dateB
            """), {
                'sub_name' : url['sub'],
                'url_type' : url['stype'],
                'url_dateA' : sdate[0],
                'url_dateB' : sdate[1]
            }).fetchone()

        return {
            'id' : rurl['id'],
            'sub' : url['sub'],
            'urls' : rurl['urls']
        } if rurl else None

    def get_url_id(self, id):
        content = self.db.execute(text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                id = :pid
        """),{'pid':id}).fetchone()

        return content

    def get_sub(self, sub):
        subn = self.db.execute(text("""
        SELECT
            sub
        FROM subs
        WHERE sub = :sub_name
        """), {
            'sub_name' : sub
        }).fetchone()
        return subn

    def get_cd(self, url):
        content = self.db.execute(text("""
            SELECT
                id,
                title,
                urls
            FROM cds
            WHERE url = :url
        """),{'url':url}).fetchone()
        return content

    def insert_url(self, url):
        return self.db.execute(text("""
            INSERT INTO urls (
                urls,
                type,
                time,
                nump,
                sub,
                nsfw
            ) VALUES (
                :urls,
                :type,
                :time,
                :nump,
                :sub,
                :nsfw
            )
        """), url).lastrowid

    def insert_sub(self, sub):
        return self.db.execute(text("""
            INSERT INTO subs (
                sub,
                nsfw
            ) VALUES (
                :sub,
                :nsfw
            )
        """), sub).lastrowid

    def insert_cd(self, cd):
        return self.db.execute(text("""
            INSERT INTO cds (
                url,
                title,
                urls
            ) VALUES (
                :url,
                :title,
                :urls
            )
        """), cd).lastrowid

    # Increasing hits/viewcount to play with statistics.
    def increment_hits_sub(self, subname):
        self.db.execute(text("""
        UPDATE subs
            SET hits = hits + 1
            WHERE sub = :subname
        """), {
            'subname' : subname
        })

    def increment_hits_url(self, id):
        self.db.execute(text("""
        UPDATE urls
        SET hits = hits + 1
        WHERE id = :sub_id
        """), {
            'sub_id' : id
        })

    def increment_vc_sub(self, subname):
            self.db.execute(text("""
            UPDATE subs
                    SET viewcount = viewcount + 1
                    WHERE sub = :subname
            """), {
                    'subname' : subname
            })

    def increment_vc_url(self, id):
            self.db.execute(text("""
            UPDATE urls
                    SET viewcount = viewcount + 1
                    WHERE id = :sub_id
            """), {
                    'sub_id' : id
            })

    def increment_hits_cd(self, id):
        self.db.execute(text("""
        UPDATE cds
        SET hits = hits + 1
        WHERE id = :cd_id
        """), {
            'cd_id' : id
        })

    #Recently Added URLs
    def recents(self, nsfw):
        recents = []
        content = self.db.execute(text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                nsfw = :pnsfw
            ORDER BY
                id DESC
            LIMIT
                8
        """),{'pnsfw':nsfw}).fetchall()
        for post in content:
            recents.append(post._asdict())
        return json.dumps(recents)

    #Popular posts based on the popular subs. Grab 5 subs with most hits -> Grab the url with most hits of each.
    def populars(self, nsfw):
        populars = []

        pnsubs = self.db.execute(text("""
            SELECT
                sub
            FROM
                subs
            WHERE
                nsfw = :pnsfw
            ORDER BY
                hits DESC
            LIMIT
                24
            """),{'pnsfw':nsfw}).fetchall()
        for pnsub in pnsubs:
            content = self.db.execute(text("""
            SELECT
                id,
                sub,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                sub = :subn
            ORDER BY
                hits DESC
            """),{'subn':pnsub['sub']}).fetchone()
            populars.append(content._asdict())
        return json.dumps(populars)


    def topFive(self, sub):
        topFive = []
        content = self.db.execute(text("""
            SELECT
                id,
                urls,
                type,
                time
            FROM
                urls
            WHERE
                sub = :subn
            ORDER BY
                hits DESC
            LIMIT
                5
        """),{'subn':sub}).fetchall()
        for post in content:
            topFive.append(post._asdict())
        return json.dumps(topFive)

    def topFiveCD(self, sub):
        topFive = []
        content = self.db.execute(text("""
            SELECT
                id,
                title,
                urls,
                url
            FROM
                cds
            WHERE
                title
            LIKE :subn
            ORDER BY
                hits DESC
            LIMIT
                5
        """),{'subn':sub}).fetchall()
        for post in content:
            topFive.append(post._asdict())
        if len(topFive) == 0:
            return None
        return json.dumps(topFive)

    def recentCD(self):
        recent = []
        content = self.db.execute(text("""
            SELECT
                id,
                title,
                urls,
                url
            FROM
                cds
            ORDER BY
                id DESC
            LIMIT
                5
        """)).fetchall()
        for post in content:
            recent.append(post._asdict())
        return json.dumps(recent)


    ######### Reddit Stock Tracker Methods #########
    
    ## User Info Manipulation

    # Insert a new user into the database.
    def insert_user(self, user):
        with self.db.connect() as connection:
            return connection.execute(text("""
                INSERT INTO user (
                    email,
                    password,
                    name
                ) VALUES (
                    :email,
                    :password,
                    :name
                )
            """), user).lastrowid
    
    # Grab user information for user authentication.
    def get_user_id_password(self, email):
        with self.db.connect() as connection:
            row = connection.execute(text("""
                SELECT
                    id,
                    password
                FROM
                    user
                WHERE
                    email = :email
            """), {'email':email}).fetchone()
            return {
                'id': row['id'],
                'password': row['password']
            } if row else None

    ## Content Manipulation

    # Multiple Stock rows Insertion
    def insertSI(self, stocks):
        with self.db.connect() as connection:
            return connection.executemany(text("""
                INSERT INTO stocks (
                    ticker,
                    fullName,
                    sentiment,
                    subjectivity,
                    count,
                    todayPrice,
                    timestamp
                ) VALUES (
                    :ticker,
                    :fullName,
                    :sentiment,
                    :subjectivity,
                    :count,
                    :todayPrice,
                    :timestamp
                    )
            """), stocks).lastrowid

    # Grab a month long stock info
    def fetchSI(self, num):
        with self.db.connect() as connection:
            return connection.execute(text("""
                SELECT
                    ticker,
                    fullName,
                    sentiment,
                    subjectivity,
                    count,
                    todayPrice,
                    volume,
                    timestamp
                FROM
                    stocks
                ORDER BY
                    timestamp DESC
            """)).fetchall()

    # Follow a Ticker
    def follow(self, ticker, user_id):
        with self.db.connect() as connection:
            return connection.execute(text("""
                INSERT INTO following_ticker (
                    ticker,
                    user_id
                ) VALUES (
                    :ticker,
                    :user_id
                )
            """), {'ticker':ticker, 'user_id':user_id}).lastrowid

    # Unfollow a Ticker
    def unfollow(self, ticker, user_id):
        with self.db.connect() as connection:
            return connection.execute(text("""
                DELETE FROM following_ticker
                WHERE ticker = :ticker AND user_id = :user_id
                """), {'ticker':ticker, 'user_id':user_id}).lastrowid

    # Fetch All the following Tickers for certain user
    def fetchFollowing(self, user_id):
        content = []
        with self.db.connect() as connection:
            data = connection.execute(text("""
                SELECT
                    ticker
                FROM
                    following_ticker
                WHERE
                    user_id = :user_id
                """), {'user_id':user_id}).fetchall()
            for post in data:
                content.append(post['ticker'])

        return content

    # Grab stock info of all the stocks a user is following
    def fetchSI_personal(self, user_id):
        dates = self.getToDate()
        content = []
        with self.db.connect() as connection:
            data = connection.execute(text("""
                SELECT
                 *
                FROM
                    stocks
                WHERE
                    ticker IN (SELECT ticker FROM following_ticker WHERE user_id = :user_id)
                    AND timestamp >= :dateA AND timestamp <= :dateB
                ORDER BY
                    ticker, timestamp DESC
                """), {'user_id':user_id, 'dateA':dates[0], 'dateB':dates[1]}).fetchall()
            for post in data:
                content.append(post._asdict())
            
        return content
