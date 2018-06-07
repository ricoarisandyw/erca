from model.Blog import Blog

class BlogAssembler:
    def fromList(self,json):
        listBlog = []
        for j in json:
            title = str(j['title'])
            content = str(j['content'])
            listBlog.append(Blog(title,content))
        return listBlog
    
    def fromObject(self,j):
        title = str(j['title'])
        content = str(j['content'])
        return Blog(title,content)