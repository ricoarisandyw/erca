
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from textblob import TextBlob as tb

class PreProcessing:
    def process(text):
        # Normalizing
        _query = text.replace("'", "")

        # ***PRE-PROCESSING***
        # Stopword
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        _query = stopword.remove(_query)

        # Stemming
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        _query = stemmer.stem(_query)
        
        return _query
