from repository.sql import Sql

class TfRepository:
    def __init__(self):
        conn = Sql()
        self.connection = conn.getConnection()

    def getFromTitle(self,title):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `word`, `n` FROM `tf` where `title`="+title
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getFromWord(self,word):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `word`, `n` FROM `tf` where `word`='"+word+"'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getFromWordAndTitle(self,word,title):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `word`, `n` FROM `tf` where `title`='"+title+"' AND `word`='"+word+"'"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

    def insert(self,tf):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "INSERT INTO `tf`(`title`,`word`, `n`) VALUES('"+tf.title+"','"+tf.word+"',"+str(tf.n)+")"
            cursor.execute(sql)
        self.connection.commit()
            
