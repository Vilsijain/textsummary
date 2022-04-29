import trafilatura
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from flask import Flask, request, jsonify, Response
from ratelimit import limits
import nltk

nltk.download('punkt')

app = Flask(__name__)

@app.route('/url/', methods=['POST'])
@limits(calls=1, period=1)
def respond():    
    
    url = request.form.get("url", None)
    length = request.form.get("length", None)
    LANGUAGE = "english"
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    downloaded = trafilatura.fetch_url(url)
    y = trafilatura.process_record(downloaded, include_comments=False, include_tables=False, deduplicate=True, target_language="en", include_formatting=False)

    response = []

    if(y == None):        
        firstParagraph = ""
        l = len(parser.document.sentences)
        SENTENCES_COUNT = int(l*float(length))
    else:        
        firstParagraph = ""
        l = len(y.split("\n"))
        SENTENCES_COUNT = int(l*float(length))
        for p in y.split("\n"):
            if len(p) > 150:
                firstParagraph = p
                break

    if firstParagraph!="":
        response.append(firstParagraph+"\n\n")
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        if str(sentence) not in firstParagraph:
            response.append(str(sentence) + "  ")
    
    res = ""  
    
    for s in response:  
        res += s   
        
    return Response(res, mimetype="text/plain")


@app.route('/text/', methods=['POST'])
@limits(calls=1, period=1)
def respond_text():
    
    y = request.form.get("text", None)
    length = request.form.get("length", None)

    LANGUAGE = "english"
    parser = PlaintextParser.from_string(y,Tokenizer("english"))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    
    response = []
    l = len(y.split(". "))
    SENTENCES_COUNT = int(l*float(length))*2
      
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        response.append(str(sentence) + "  ")
    
    res = ""  

    for s in response:  
        res += s   
    
    return Response(res, mimetype="text/plain")



if __name__ == '__main__':
    
    app.run(threaded=True, port=5000)
