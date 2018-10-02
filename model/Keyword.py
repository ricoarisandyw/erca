class Keyword:
    def __init__(self,id_faq,word,n):
        self.id_faq = id_faq
        self.word = word
        self.n = n

    def __str__(self):
        return str(self.id_faq)+self.word+str(self.n)