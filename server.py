from flask import Flask, url_for, send_from_directory, request, render_template
import logging
import os
import heapq
import json
from werkzeug import secure_filename
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from textblob import TextBlob as tb
from tfidf2 import tf, idf, n_containing
from scipy import spatial
from helper.PreProcessing import PreProcessing
# Model
from model.Blog import Blog
from model.Tf import Tf
from model.Faq import Faq
from model.Keyword import Keyword
# Repository
from repository.BlogRepository import BlogRepository
from repository.TfRepository import TfRepository
from repository.FAQRepository import FAQRepository
from repository.KeywordRepository import KeywordRepository
# Assembler
from assembler.BlogAssembler import BlogAssembler
from assembler.TfAssembler import TfAssembler

from collections import defaultdict
from helper.tesaurus import getSinonim

import os.path

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)


@app.route('/faq', methods=['POST'])
def blogging():
    # Insert to Blog DB
    _question = request.form["question"]
    _answer = request.form["answer"]
    faq = FAQRepository().insert(Faq(0, _question, _answer))

    # Normalizing
    _question = _question.replace("'", "")
    _answer = _answer.replace("'", "")

    # ***PRE-PROCESSING***
    # Stopword
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    _question = stopword.remove(_question)
    _answer = stopword.remove(_answer)

    # Stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    _question = stemmer.stem(_question)
    _answer = stemmer.stem(_answer)

    # Get all unique word from question
    blob = tb(_question)
    uniqWord = list(set(blob.words))

    # Count all unique word in question
    sumOfWord = 0
    for word in uniqWord:
        _n = blob.words.count(word)
        sumOfWord += _n

    # Get Average
    average = sumOfWord/len(blob)

    # Get Over Average Word
    for word in uniqWord:
        n = blob.words.count(word)
        if(n > average):
            # Insert to Keyword DB
            KeywordRepository().insert(Keyword(faq.id_faq, word, n))

    return render_template('faq.html')


@app.route('/')
def upload_file():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat_post():
    log = defaultdict(dict)
    _function = request.form["function"]
    # print("Function :" + _function)
    if(_function == "getState"):
        if(os.path.isfile("chat.txt")):
            chat_file = open("chat.txt").readlines()
        log["state"] = len(chat_file)
    if(_function == "update"):
        state = request.form["state"]

        # Open File
        if(os.path.isfile("chat.txt")):
            chat_file = open("chat.txt").readlines()

        count = len(chat_file)
        if(int(state) == count):
            log["state"] = state
            log["text"] = False
        else:
            text = []
            chat_file = open("chat.txt").readlines()
            # Ambil seluruh Chat.txt
            log["state"] = len(chat_file)
            for idx, lin in enumerate(chat_file):
                # lenLin = int(len(lin))
                # Jika panjang chat dulu < panjang chat sekarang
                if(idx >= int(state)):
                    text.append(lin)
        
            log["text"] = text

    if(_function == 'send'):
        _nickname = request.form["nickname"]
        _message = request.form["message"]
        _file = open("chat.txt", "a")
        _file.write("<span>" + _nickname+"</span>" + _message)
        _answer = matcher(_message)
        _file.write("<span>Ercha Bot</span>" + _answer + "\n")

    js = json.dumps(log)
    return js


@app.route('/chat')
def chat():
    return render_template('chat.html')

def matcher(query):
    # PreProcessing
    query = PreProcessing.process(query)
    bQuery = tb(query)
    queryLen = len(bQuery)
    uniqQuery = list(set(bQuery.words)) 

    # Mapping the result
    storage = defaultdict(dict)
    _nUQ = []
    faqs = []
    rank = []
    for uQ in uniqQuery:
        _nUQ.append(bQuery.words.count(uQ))
        keywords = KeywordRepository().getByKeyword(uQ)
        for key in keywords:
            storage[key.id_faq][key.word] = key.n
            faqs.append(key.id_faq)

    if(len(faqs)<=0):
        return "I don't understand"

    faqs = list(set(faqs))

    # **SCORING**
    # Treshold = 50%
    # Cosine Simliarity them
    print("-----------------------")
    print("Question :",query)
    score = []
    for faq in faqs:
        _nFAQ = []
        for uQ in uniqQuery:
            try:
                _nFAQ.append(storage[faq][uQ])
            except:
                # print(uQ+" not found")
                _nFAQ.append(0)
        print(_nUQ)
        print(_nFAQ)
        result = 1 - spatial.distance.cosine(_nUQ, _nFAQ)
        faq_temp = FAQRepository().getById(faq)
        print(faq_temp.question)
        print("FAQ-",faq," : ",result)
        score.append(result)
    
    bestIndex = score.index(max(score))
    _answer = FAQRepository().getById(faqs[bestIndex])
    print(max(score))
    if(max(score)<0.5):
        return "I don't understand"

    return _answer.answer

@app.route('/faq')
def upload_blog():
    return render_template('faq.html')


@app.route('/find')
def read_blog():
    return render_template('test.html')


@app.route('/detail')
def detail_blog():
    _title = request.args.get('title')
    blog = BlogRepository().getByTitle(_title)
    return render_template('detail.html', r=blog)


@app.route('/table')
def table():
    print("Open : Table . . ")
    keywords = KeywordRepository().getAll()
    faqs = FAQRepository().getAll()
    # List of Keywords
    aggregate = defaultdict(dict)
    for f in faqs:
        for kw in keywords:
            # If keyword has data in that FAQ
            if(f.id_faq == kw.id_faq):
                aggregate[f.id_faq][kw.word] = kw.n
            # If keyword not in that faq
            else:
                aggregate[f.id_faq][kw.word] = 0

    return render_template('table.html', keywords=keywords, agg=aggregate, faqs=faqs)


@app.route('/cosine', methods=["POST"])
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
            print(word, "not available")

    if(len(listTitleBlog) == 0):
        return render_template("result.html", rank=rank, query=query)

    listTitleBlog = list(set(listTitleBlog))  # Unique Blog Title

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
        result = 1 - spatial.distance.cosine(cQuery, cBlog)
        score.append(result)
    lenScore = len(score)
    while(lenScore > 0):
        bestIndex = score.index(max(score))
        rank.append(blogAll[bestIndex])
        del score[bestIndex]
        del blogAll[bestIndex]
        lenScore = len(score)

    return render_template("result.html", rank=rank, query=query)


@app.route('/find', methods=['POST'])
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
        listTf.append(Tf("query", word, _n))

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
            print(word, "not available")

    if(len(listTitleBlog) == 0):
        return render_template("result.html", rank=rank, query=query)

    listTitleBlog = list(set(listTitleBlog))  # Unique Blog Title

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
        idfList.append(idf(word, blobList))

    # Scoring
    for title in listTitleBlog:
        result = 0
        for i, word in enumerate(uniqWord):
            try:
                # if word available
                # Counting Word
                blogData = BlogRepository().getByTitle(title)
                _content = blogData["tf"]
                blob = tb(_content)
                _n = blob.words.count(word)
                result = result+(idfList[i]*_n)
            except:
                print(word, "not available")
        score.append(result)
    lenScore = len(score)
    while(lenScore > 0):
        bestIndex = score.index(max(score))
        rank.append(listBlog[bestIndex])
        del score[bestIndex]
        del listBlog[bestIndex]
        lenScore = len(score)
    # print(rank)
    return render_template("result.html", rank=rank, query=query)


if __name__ == '__main__':
    app.run(host='localhost', debug=False, port=3000)
