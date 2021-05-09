import pymysql
from CaptionInformation import *


class MemorizeDB:

    def __init__(self, user, passwd, host):
        self.user = user
        self.passwd = passwd
        self.host = host

    def setInit(self, user, passwd, host):
        self.user = user
        self.passwd = passwd
        self.host = host

    def connect(self):
        self.connection = pymysql.connect(
            user=self.user,
            passwd=self.passwd,
            host=self.host,
            db='memorize',
            charset='utf8')
        self.cursor = self.connection.cursor(pymysql.cursors.Cursor)

    def insertMovie(self, movie):
        sql = '''INSERT INTO movie (k_title,e_title, filepath, thumbnail) VALUES (%s,%s,%s,%s)'''
        self.cursor.execute(sql, (movie.k_title, movie.e_title, movie.filepath, movie.thumbnail))
        self.connection.commit()

    def insertCaption(self, captionInfo):
        sql = '''INSERT INTO caption(movie_id, start_second, end_second, caption, thumbnail) VALUES (%s, %s, %s, %s, %s)'''
        self.cursor.execute(sql,
                            (captionInfo.movie_id, captionInfo.startSecond, captionInfo.endSecond, captionInfo.caption, captionInfo.thumbnail))
        self.connection.commit()

    def getMovieIdByk_title(self, k_title):
        sql = '''SELECT id FROM movie WHERE k_title = %s'''
        self.cursor.execute(sql, k_title)
        row = self.cursor.fetchall()
        return row[0][0]

    def checkMovieByE_title(self, e_title):
        sql = '''SELECT * FROM movie WHERE e_title = %s'''
        self.cursor.execute(sql, e_title)
        row = self.cursor.fetchall()
        if len(row) > 0:
            return True
        else:
            return False

    def dbClose(self):
        self.connection.close()
