import os, pickle, string, nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from django.conf import settings

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
                for sent in nltk.sent_tokenize(query)]
            ]).lower().translate(str.maketrans('', '', string.punctuation))

        return sorted([
            item for sublist in list(
                map(
                    lambda q: indexdata[q] if q in indexdata.keys() else [],
                    search_query.split()
                    )
                )
                for item in sublist
            ], key=lambda x: x['rank'], reverse=True)

