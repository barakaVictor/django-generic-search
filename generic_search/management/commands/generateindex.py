import os, json, pickle, math, logging, string, nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from django.conf import settings
from django.core.management.base import BaseCommand
from generic_search.utils import pos_tagger

logger = logging.getLogger(__name__)

nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')

class Command(BaseCommand):
    help = 'Compute TF-IDF value for each word in each document relative to the entire document corpus'

    def generate_tfidf_index(self, data):
        """
        Compute TF-IDF value for each word in each document relative to the entire document corpus
        """
        tfidf = {}
        try:
            os.remove(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'))
        except OSError:
            pass

        corpus_size = len(data)

        for index, document in enumerate(data):

            words_in_doc = document['contents'].lower().split()

            for word in set(words_in_doc):
                if word not in tfidf.keys():
                    tfidf[word] = []
                tf = words_in_doc.count(word)/ len(words_in_doc)
                idf = self.compute_idf(word, data, corpus_size)
                tfidf[word].append({
                    'title': document['title'],
                    'description': document['description'],
                    'url': document['url'],
                    'index': index,
                    'rank': document['rank'],
                    'tfidf': tf * idf
                })
                tfidf[word].sort(key=lambda k: k['tfidf'], reverse=True)
        with open(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'), 'wb') as f:
            pickle.dump(tfidf, f)
            self.stdout.write("Completed indexing")

    def compute_idf(self, word: str, corpus: list, corpus_size: int) -> float:
        """Compute the Inverse Document Frequency of the given word in the provided corpus"""
        corpus_items_with_word = [
            document for document in corpus
            if
            word in str(document['contents']).lower().translate(str.maketrans('', '', string.punctuation))
        ]
        try:
            return math.log10(corpus_size / (len(corpus_items_with_word) + 1))
        except Exception as e:
            self.stderr.write(e)
            raise

    def clean_data(self):
        """Expects a list of json objects"""
        # load data from file
        self.stdout.write("Loading data....")
        data = []
        with open(os.path.join(settings.BASE_DIR, 'crawled_pages/discovered_pages.json'), encoding="utf8") as f:
            try:
                data = json.loads(f.read())
            except json.JSONDecodeError:
                data = json.loads('[]')
            except Exception as e:
                self.stderr.write(e)
                raise

            self.stdout.write("Cleaning data....")

            # Remove punctuations, stopwords, lemmatize and convert to lower case
            for i in range(len(data)):
                # data[i]['title'] =' '.join([' '.join(x) for x in [
                #     [
                #         (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                #         for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                #         if not word_tag[0] in stopwords.words()
                #     ] for sent in nltk.sent_tokenize(data[i]['title'])
                # ]]).translate(str.maketrans('', '', string.punctuation))

                # data[i]['description'] =' '.join([' '.join(x) for x in [
                #     [
                #         (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                #         for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                #         if not word_tag[0] in stopwords.words()
                #     ] for sent in nltk.sent_tokenize(data[i]['description'] if data[i]['description'] else "")
                # ]]).translate(str.maketrans('', '', string.punctuation))

                # data[i]['keywords'] = ' '.join(
                #     [
                #         WordNetLemmatizer().lemmatize(word.translate(str.maketrans('', '', string.punctuation)))
                #         for word in nltk.word_tokenize(data[i]['keywords'] if data[i]['keywords'] else "")
                #         if not word in stopwords.words()
                #     ]
                # ).lower()

                data[i]['contents'] = ' '.join(
                    [' '.join(x) for x in [
                        [
                            (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                            for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                            if not word_tag[0] in stopwords.words()
                        ] for sent in nltk.sent_tokenize(data[i]['contents'])
                    ]
                ]).translate(str.maketrans('', '', string.punctuation))
        # with open(os.path.join(settings.BASE_DIR, 'crawled_pages/clean_ranked_data.json'), 'w', encoding="utf8") as f:
        #     json.dump(data, f, indent=4)
        #     self.stdout.write(f"Completed cleaning data. clean data at : {os.path.join(settings.BASE_DIR, 'crawled_pages/clean_data.json')}")
        return data

    def handle(self, *args, **kwargs):

        self.generate_tfidf_index(self.clean_data())