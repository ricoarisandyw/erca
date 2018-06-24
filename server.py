from flask import Flask, url_for, send_from_directory, request, render_template
import logging, os
import heapq
import json
from werkzeug import secure_filename
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from textblob import TextBlob as tb
from tfidf2 import tf,idf,n_containing
from scipy import spatial
# Model
from model.Blog import Blog
from model.Tf import Tf
# Repository
from repository.BlogRepository import BlogRepository
from repository.TfRepository import TfRepository
# Assembler
from assembler.BlogAssembler import BlogAssembler
from assembler.TfAssembler import TfAssembler

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

@app.route('/blog', methods = ['POST'])
def blogging():
    # Insert to Blog DB
    _title = request.form["title"]
    _content = request.form["content"]
    _link = request.form["link"]
    _date = request.form["date"]
    # Normalizing
    _title = _title.replace("'","\"")
    _content2 = _content.replace("'","")
    _content = _content.replace("'","")

    # ***PRE-PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _content2 = stopword.remove(_content2)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _content2 = stemmer.stem(_content2)

    BlogRepository().insert(Blog(_title,_content,_link,_content2,_date))

    # Insert to Tf DB
    return render_template('index.html')

@app.route('/')
def upload_file():
   return render_template('index.html')

@app.route('/blog')
def upload_blog():
    return render_template('blog.html')

@app.route('/find')
def read_blog():
    return render_template('test.html')

@app.route('/detail')
def detail_blog():
    _title = request.args.get('title')
    blog = BlogRepository().getByTitle(_title)
    return render_template('detail.html',r = blog)

@app.route('/cosine', methods = ["POST"])
def cosine():
    rank = []
    score = []
    query = request.form["query"]
     # ***PRE PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _query = stopword.remove(query)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _query = stemmer.stem(_query)

    # TF Query
    listTf = []
    blob = tb(_query)
    uniqWord = list(set(blob.words))
    # Desc : GET BLOG TITLE WHICH THE CONTENT CONTAINT QUERY WORD
    listTitleBlog = []
    for word in uniqWord:
        try:
            blogList = BlogRepository().getByWord(word)
            for t in blogList:
                listTitleBlog.append(t["title"])
        except:
            print(word,"not available")

    if(len(listTitleBlog)==0):
        return render_template("result.html", rank = rank,query = query)

    listTitleBlog = list(set(listTitleBlog)) #Unique Blog Title
    
    blogAll = []
    for l in listTitleBlog:
        blogAll.append(BlogRepository().getByTitle(l))

    # *** COSINE SIMILIARITY ***
    # Scoring
    for blog in blogAll:        
        # Get Set of Article and Query
        combined = _query + blog["tf"]
        blob = tb(combined)
        uniqWord = list(set(blob.words))
        # Count on two array how many word over there
        bQuery = tb(_query)
        bBlog = tb(blog["tf"])
        cQuery = []
        cBlog = []
        for word in uniqWord:
            _nQ = bQuery.words.count(word)
            cQuery.append(_nQ)
            _nB = bBlog.words.count(word)
            cBlog.append(_nB)
        # print(blog["title"])
        # print(cQuery)
        # print(cBlog)
        result = 1 - spatial.distance.cosine(cQuery, cBlog)
        score.append(result)
    lenScore = len(score)
    while(lenScore>0):
        bestIndex = score.index(max(score))
        rank.append(blogAll[bestIndex])
        del score[bestIndex]
        del blogAll[bestIndex]
        lenScore = len(score)

    return render_template("result.html", rank = rank,query = query)

@app.route('/find', methods = ['POST'])
def result_blog():
    score = []
    rank = []

    query = request.form["query"]
    # ***PRE PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _query = stopword.remove(query)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _query = stemmer.stem(_query)

    # TF Query
    listTf = []
    blob = tb(_query)
    uniqWord = list(set(blob.words))
    for word in uniqWord:
        _n = blob.words.count(word)
        listTf.append(Tf("query",word,_n))

    # *** SCORING PROCESS ***
    # TF
    # Desc : GET BLOG TITLE WHICH THE CONTENT CONTAINT QUERY WORD
    listTitleBlog = []
    for word in uniqWord:
        try:
            blogList = BlogRepository().getByWord(word)
            for t in blogList:
                listTitleBlog.append(t["title"])
        except:
            print(word,"not available")

    if(len(listTitleBlog)==0):
        return render_template("result.html", rank = rank,query = query)

    listTitleBlog = list(set(listTitleBlog)) #Unique Blog Title

    listBlog = []
    for l in listTitleBlog:
        listBlog.append(BlogRepository().getByTitle(l))

    # IDF
    blobList = []
    for blog in listBlog:
        content = blog["content"]
        blobList.append(tb(content))

    idfList = []
    for word in uniqWord:
        idfList.append(idf(word,blobList))

    # Scoring
    for title in listTitleBlog:
        result = 0
        for i,word in enumerate(uniqWord):
            try:
                # if word available
                # Counting Word
                blogData = BlogRepository().getByTitle(title)
                _content = blogData["tf"]
                blob = tb(_content)
                _n = blob.words.count(word)
                result = result+(idfList[i]*_n)
            except:
                print(word,"not available")
        score.append(result)
    lenScore = len(score)
    while(lenScore>0):
        bestIndex = score.index(max(score))
        rank.append(listBlog[bestIndex])
        del score[bestIndex]
        del listBlog[bestIndex]
        lenScore = len(score)
    # print(rank)
    return render_template("result.html", rank = rank,query = query)

if __name__ == '__main__':
    app.run(host='localhost', debug=False)