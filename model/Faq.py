from sqlalchemy import Integer, Column, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

class Faq():

    def __init__(self,id_faq,question,answer):
        self.id_faq = id_faq
        self.question = question
        self.answer = answer

    def __str__(self):
        return str(self.id_faq)+self.question+str(self.answer)

