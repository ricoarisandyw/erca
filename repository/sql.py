import pymysql.cursors

class Sql:
    def getConnection(self):
        return pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='textmining',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)