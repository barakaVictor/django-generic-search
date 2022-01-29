import os, json, logging
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)
np.set_printoptions(threshold=np.inf)

def generate_web_graph():
    """
    Generates a directed column-stochastic graph where the columns indicate the
    probability of leaving the current node to another node based on the outgoing
    links from the current node. The rows show the probability of landing on the current
    node from other nodes.
    """
    data = []
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/clean_data.json'), 'r', encoding="utf8") as f:
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            data = json.loads('[]')
        except Exception as e:
            logger.error(e)
            raise

        num_pages = len(data)
        # Generate directed graph representing page relationships
        G = np.zeros((num_pages, num_pages))

        #G[i, j] = 1/ denotes that page i has a link pointing to page j
        for index, doc in enumerate(data):
            for link in doc['links']:
                found, i = next(((True, i) for i, item in enumerate(data) if item['url'] == link), (False, None))
                if found:
                    G[i, index] = 1/len(doc['links'])
        return G

def update_ranks(ranks):
    data = []
    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/clean_data.json'), 'r', encoding="utf8") as f:
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            data = json.loads('[]')
        except Exception as e:
            logger.error(e)
            raise

        for index in range(len(data)):
            data[index]['rank'] = ranks[index]

    with open(os.path.join(settings.BASE_DIR, 'crawled_pages/ranking_results.json'), 'w', encoding="utf8") as f:
        json.dump(data, f, indent=4)
        logger.debug("Completed ranking pages")

def page_rank(G, iterations: int = 100, dumping_factor: float = 0.85, epsilon: float = None):
    """
    Calculates the pagerank of the given graph representing the web

    """
    num_pages = G.shape[1]
    # Assume an initial probabiliy of 1/n where n = total number of pages
    ranks = np.ones(num_pages) / num_pages
    #M_hat = (dumping_factor * G + (1 - dumping_factor) / num_pages)
    M_hat = dumping_factor * G + (1-dumping_factor)/num_pages * np.ones([num_pages, num_pages])

    if epsilon:
        last_ranks = ranks
        ranks = M_hat @ ranks
        i=0
        while np.linalg.norm(last_ranks - ranks) > epsilon :
            last_ranks = ranks
            ranks = M_hat @ ranks
            i+=1
        logger.debug(f"{i} iterations to convergence.")
    else:
        for i in range(iterations):
            ranks = M_hat @ ranks
    return ranks


