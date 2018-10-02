from repository.sql import Sql
from model.Keyword import Keyword

class KeywordRepository:
    def __init__(self):
        conn = Sql()
        self.connection = conn.getConnection()

    def getAll(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `keyword`"
            cursor.execute(sql)
            result = cursor.fetchall()
            keywords = []
            for kw in result:
                keywords.append(Keyword(kw["id_faq"],kw["word"],kw["n"]))
            return keywords

    def getByFaqId(self,id):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `keyword` where `id_faq`={{id}}"
            cursor.execute(sql)
            result = cursor.fetchall()
            keywords = []
            for kw in result:
                keywords.append(Keyword(kw["id_faq"],kw["word"],kw["n"]))
            return keywords

    def getByKeyword(self,word):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `keyword` where `word`='"+word+"'"
            cursor.execute(sql)
            result = cursor.fetchall()
            keywords = []
            for kw in result:
                keywords.append(Keyword(kw["id_faq"],kw["word"],kw["n"]))
            return keywords

    def insert(self,keyword):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "INSERT INTO `keyword`(`id_faq`,`word`, `n`) VALUES('"+str(keyword.id_faq)+"','"+keyword.word+"','"+str(keyword.n)+"')"
            cursor.execute(sql)
        self.connection.commit()
        return keyword
            
