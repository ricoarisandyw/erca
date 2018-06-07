class Tf:
    def __init__(self,title,word,n):
        self.title = title
        self.word = word
        self.n = n

    def __str__(self):
        return self.title+self.word+str(self.n)