class Blog:
    def __init__(self,title,content):
        self.title = title
        self.content = content

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{title:"+self.title+",content:"+self.content+"}"
        