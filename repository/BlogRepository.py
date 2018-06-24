from repository.sql import Sql

class BlogRepository:
    def __init__(self):
        conn = Sql()
        self.connection = conn.getConnection()

    def insert(self,blog):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `blog` (`title`, `content`,`link`,`tf`,`date`) VALUES ('"+blog.title+"','"+blog.content+"','"+blog.link+"','"+blog.tf+"','"+blog.date+"')"
            cursor.execute(sql)
        self.connection.commit()

    def getAll(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `content`,`link`,`tf`,`date` FROM `blog`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getByTitle(self,title):
         with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `content`,`link`,`tf`,`date` FROM `blog` where `title`='"+title+"'"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result

    def getByWord(self,query):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `content`,`link`,`tf`,`date` FROM `blog` where `tf` LIKE '%"+query+"%'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
   