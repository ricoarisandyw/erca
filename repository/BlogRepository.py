from repository.sql import Sql

class BlogRepository:
    def __init__(self):
        conn = Sql()
        self.connection = conn.getConnection()

    def insert(self,blog):
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `blog` (`title`, `content`) VALUES ('"+blog.title+"','"+blog.content+"')"
            cursor.execute(sql)
        self.connection.commit()

    def getAll(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `content` FROM `blog`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getByTitle(self,title):
         with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `title`, `content` FROM `blog` where `title`='"+title+"'"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
   