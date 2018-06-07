from flask import Flask, url_for, send_from_directory, request, render_template
import logging, os
import heapq
import json
from werkzeug import secure_filename
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from textblob import TextBlob as tb
from tfidf2 import tf,idf,n_containing
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
    # Normalizing
    _content = _content.replace("'","")

    BlogRepository().insert(Blog(_title,_content))
    # ***PRE-PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _content = stopword.remove(_content)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _content = stemmer.stem(_content)

    # TF
    listTf = []
    blob = tb(_content)
    uniqWord = list(set(blob.words))
    for word in uniqWord:
        _n = blob.words.count(word)
        listTf.append(Tf(_title,word,_n))

    for tf in listTf:
        TfRepository().insert(tf)

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

@app.route('/find', methods = ['POST'])
def result_blog():
    _query = request.form["query"]
    # ***PRE PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _query = stopword.remove(_query)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _query = stemmer.stem(_query)

    print("Query",_query)

    # TF Query
    listTf = []
    blob = tb(_query)
    uniqWord = list(set(blob.words))
    for word in uniqWord:
        _n = blob.words.count(word)
        listTf.append(Tf("query",word,_n))

    # TF
    listTitleBlog = []
    for word in uniqWord:
        # Dapatkan Tf
        try:
            tfData = TfRepository().getFromWord(word)
            for t in tfData:
                listTitleBlog.append(t["title"])
        except:
            print(word,"not available")

    if(len(listTitleBlog)==0):
        return "Data Not Found"

    listTitleBlog = list(set(listTitleBlog))
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

    score = []
    for title in listTitleBlog:
        result = 0
        for i,word in enumerate(uniqWord):
            print("i",i)
            try:
                # if word available
                TFData = TfRepository().getFromWordAndTitle(word,title)
                result = result+(idfList[i]*TFData["n"])
            except:
                print(word,"not available")
        score.append(result)
    rank = []
    lenScore = len(score)
    while(lenScore>0):
        bestIndex = score.index(max(score))
        rank.append(listBlog[bestIndex])
        del score[bestIndex]
        del listBlog[bestIndex]
        lenScore = len(score)
    print(rank)
    return render_template("result.html", rank = rank)

if __name__ == '__main__':
    app.run(host='localhost', debug=False)