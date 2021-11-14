from sqlalchemy import text

class DatabaseDao:
    def __init__(self, database):
        self.db = database

    def dateToDT(self, date):
        dates = [date+" 00:00:00", date+" 23:59:59"]
        return dates

    def getT_url(self, url):
        sdate = self.dateToDT(url['sdate'])
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
        sdate = self.dateToDT(url['sdate'])
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
                5
        """),{'pnsfw':nsfw}).fetchall()
        for post in content:
            recents.append(post)
        return recents

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
                5
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
            populars.append(content)
        return populars