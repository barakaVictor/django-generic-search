import os, json, pickle, math, logging, string, nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import wordnet
from django.conf import settings

logger = logging.getLogger(__name__)

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')


def generate_tfidf_index():
    """Compute TFIDF value for each word in each document relative to the entire document corpus """
    tfidf = {}
    try:
        os.remove(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'))
    except OSError:
        pass
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/ranking_results.json'), 'r', encoding="utf8") as f:
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            data = json.loads('[]')
        except Exception as e:
            logger.error(e)
            raise
        corpus_size = len(data)
        for index, document in enumerate(data):
            bag_of_words = ""
            if document['title'] != None:
                bag_of_words = bag_of_words + document['title']
            if document['description'] != None:
                bag_of_words = bag_of_words + document['description']
            if document['keywords'] != None:
                bag_of_words = bag_of_words + document['keywords']
            if document['contents'] != None:
                bag_of_words = bag_of_words + document['contents']

            clean_bag_of_words = bag_of_words.lower().split()

            for word in set(clean_bag_of_words):
                if word not in tfidf.keys():
                    tfidf[word] = []
                tf = clean_bag_of_words.count(word)/ len(clean_bag_of_words)
                idf = compute_idf(word, data, corpus_size)
                tfidf[word].append({
                    'rank': document['rank'],
                    'title':  document['title'],
                    'description': document['description'],
                    'url': document['url'],
                    'index': index,
                    'tfidf': tf * idf
                })
                tfidf[word].sort(key=lambda k: k['tfidf'], reverse=True)
        with open(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'), 'wb') as f:
            pickle.dump(tfidf, f)
            logger.debug("Completed indexing exported data")

def compute_idf(word: str, corpus: list, corpus_size: int) -> float:
    """Compute the Inverse Document Frequency of the given word in the provided corpus"""
    corpus_items_with_word = [document for document in corpus if word in str(document['title']).lower().translate(str.maketrans('', '', string.punctuation)) or word in str(document['keywords']).lower().translate(str.maketrans('', '', string.punctuation))]
    try:
        return math.log10(corpus_size / (len(corpus_items_with_word) + 1))
    except Exception as e:
        logger.error(e)
        raise

def clean_data():
    """Expects a list of json objects"""
    # load data from file
    logger.debug("Loading data....")
    data = []
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/discovered_pages.json'), encoding="utf8") as f:
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            data = json.loads('[]')
        except Exception as e:
            logger.error(e)
            raise
        logger.debug("Cleaning data....")
        #remove links that do not point to any recorded page in the database and duplicates
        for index in range(len(data)):
            ok_links = []
            for link in data[index]['links']:
                for indx in range(len(data)):
                    if link == data[index]['url']:
                        continue
                    elif link == data[indx]['url']:
                        ok_links.append(link)
            data[index]['links'] = list(set(ok_links))
        # Remove punctuations, stopwords, lemmatize and convert to lower case
        for i in range(len(data)):
            data[i]['title'] =' '.join([' '.join(x) for x in [
                [
                    (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                    for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                    if not word_tag[0] in stopwords.words()
                ] for sent in sent_tokenize(data[i]['title'])
            ]]).translate(str.maketrans('', '', string.punctuation))

            data[i]['description'] =' '.join([' '.join(x) for x in [
                [
                    (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                    for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                    if not word_tag[0] in stopwords.words()
                ] for sent in sent_tokenize(data[i]['description'] if data[i]['description'] else "")
            ]]).translate(str.maketrans('', '', string.punctuation))

            data[i]['keywords'] = ' '.join(
                [
                    WordNetLemmatizer().lemmatize(word.translate(str.maketrans('', '', string.punctuation)))
                    for word in word_tokenize(data[i]['keywords'] if data[i]['keywords'] else "")
                    if not word in stopwords.words()
                ]
            ).lower()

            data[i]['contents'] = ' '.join(
                [' '.join(x) for x in [
                    [
                        (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                        for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                        if not word_tag[0] in stopwords.words()
                    ] for sent in sent_tokenize(data[i]['contents'])
                ]
            ]).translate(str.maketrans('', '', string.punctuation))
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/clean_data.json'), 'w', encoding="utf8") as f:
        json.dump(data, f, indent=4)
        logger.debug(f"Completed cleaning data. clean data at : {os.path.join(settings.BASE_DIR, 'crawled_pages/clean_data.json')}")

def pos_tagger(nltk_tag: str) -> str:
    """
    Maps NTLK POS(Parts of Speech) tags to wordnet POS tags

    wordnet valid POS tags are `"n"` for nouns,
    `"v"` for verbs, `"a"` for adjectives, `"r"`
    for adverbs and `"s"` for satellite adjectives
    """
    if nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    elif nltk_tag.startswith('J'):
        return wordnet.ADJ
    else:
        return wordnet.NOUN


def query_document_index(query: str) -> list:
    """
    Retrieve documents based on provided query
    """

    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/indexed_results'), 'rb') as dbindex:
        indexdata = pickle.load(dbindex)
        search_query = ' '.join(
            [' '.join(x) for x in [
                [
                    (lambda y: WordNetLemmatizer().lemmatize(y[0].lower(), pos_tagger(y[1])))(word_tag)
                    for word_tag in nltk.pos_tag(nltk.word_tokenize(sent))
                    if not word_tag[0] in stopwords.words()
                ]
                for sent in sent_tokenize(query)]
            ]).lower().translate(str.maketrans('', '', string.punctuation))

        return sorted([item for sublist in list(map(lambda q: indexdata[q] if q in indexdata.keys() else [], search_query.split())) for item in sublist], key=lambda x: x['rank'], reverse=True)
