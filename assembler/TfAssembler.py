from model.Tf import Tf

class TfAssembler:
    def fromList(self,json):
        print("AssJson",json)
        listBlog = []
        for j in json:
            title = str(j['title'])
            word = str(j['word'])
            n = j["n"]
            print("Assembler",title,word,n)
            listBlog.append(Tf(title,word,n))
        return listBlog
    
    def fromObject(self,j):
        title = str(j['title'])
        word = str(j['word'])
        n = j["n"]
        return Tf(title,word,n)