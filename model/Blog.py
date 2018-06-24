class Blog:
    def __init__(self,title,content,link,tf,date):
        self.title = title
        self.content = content
        self.link = link
        self.tf = tf
        self.date = date

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{title:"+self.title+",content:"+self.content+"}"
        