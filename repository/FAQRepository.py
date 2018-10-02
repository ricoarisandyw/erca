from repository.sql import Sql
from model.Faq import Faq

class FAQRepository:
    def __init__(self):
        conn = Sql()
        self.connection = conn.getConnection()

    def getAll(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `faq`"
            cursor.execute(sql)
            result = cursor.fetchall()
            faqs = []
            for f in result:
                faqs.append(Faq(f["id_faq"],f["question"],f["answer"]))
            return faqs

    def getByQuestion(self,question):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `faq` where `question`='"+question+"'"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result

    def getById(self,id):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `faq` where `id_faq`="+str(id)
            cursor.execute(sql)
            result = cursor.fetchall()
            f = result[0]
            return Faq(f["id_faq"],f["question"],f["answer"])

    def insert(self,faq):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "INSERT INTO `faq`(`question`,`answer`) VALUES('"+faq.question+"','"+faq.answer+"')"
            cursor.execute(sql)
        self.connection.commit()
        _catch = self.getByQuestion(faq.question)
        _first = _catch[0]
        _faq = Faq(_first["id_faq"],_first["question"],_first["answer"])
        return _faq

            
