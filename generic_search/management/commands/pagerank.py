import os, json, logging
import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Triggers the pagerank algorithm and associates the calculated ranks with their respective discovered pages'

    def clean_links(self):
        data = []
        with open(os.path.join(settings.BASE_DIR, 'crawled_pages/discovered_pages.json'), 'r', encoding="utf8") as f:
            try:
                data = json.loads(f.read())
            except json.JSONDecodeError:
                data = json.loads('[]')
            except Exception as e:
                logger.error(e)
                raise
            #only include outgoing links that have a matching node and that do not link back
            #to the current page i.e remove broken links and links to self.
            for index in range(len(data)):
                data[index]['links'] = list(set([
                    x
                    for node in data
                    for x in data[index]['links']
                    if x == node['url'] and x != data[index]['url']
                    ])
                )
        return data

    def generate_web_graph(self, data):
        """
        Generates a directed column-stochastic graph M, where where M_i,j
        represents the link from node 'j' to node 'i'.
        """

        num_pages = len(data)

        M = np.zeros((num_pages, num_pages))

        # Build adjacency matrix where M_i,j represents the link from 'j' to 'i', such that for all 'j'
        # sum(i, M_i,j) = 1

        for j in range(num_pages):
            links = data[j]['links']
            if len(links) > 0:
                for link in links:
                    found, i = next(((True, i) for i, node in enumerate(data) if link == node['url'] and link != data[j]['url']), (False, None))
                    if found:
                        M[i, j] = 1/len(links)
            else:
                for i in range(num_pages):
                    M[i, j] = 1/num_pages
        return M

    def page_rank(self, M, dumping_factor: float = 0.85, epsilon: float = 0.0001, iterations: int = 100,):
        """
        Calculates the pagerank of the given graph representing the web

        """
        num_nodes = M.shape[1]

        # Assume an initial probabiliy of 1/n where n = total number of nodes
        ranks = np.ones((num_nodes, 1)) / num_nodes

        # Build the state transition probability matrix using the PageRank formula
        M_hat = ((1 - dumping_factor) / num_nodes) + (M * dumping_factor)

        #Run iterations to continuously update the ranks untill converges or end of interations specified
        if iterations:
            for i in range(iterations):
                ranks = M_hat @ ranks
        else:
            last_ranks = ranks
            ranks = M_hat @ ranks
            i=0
            while np.linalg.norm(last_ranks - ranks) > epsilon :
                last_ranks = ranks
                ranks = M_hat @ ranks
                i+=1
            self.stdout.write(f"{i} iterations to convergence.")
        self.stdout.write(f"Sum of ranks: {ranks.sum(axis=0)}")
        return ranks

    def update_ranks(self, ranks):
        data = []
        with open(os.path.join(settings.BASE_DIR, 'crawled_pages/discovered_pages.json'), 'r+', encoding="utf8") as f:
            try:
                data = json.loads(f.read())
            except json.JSONDecodeError:
                data = json.loads('[]')
            except Exception as e:
                logger.error(e)
                raise

            for index in range(len(data)):
                data[index]['rank'] = ranks[index, 0]

            data = sorted(data, key=lambda d: d['rank'], reverse=True)

            f.seek(0)  # rewind
            json.dump(data, f, indent=4)
            f.truncate()
            self.stdout.write("Completed ranking pages")

    def add_arguments(self, parser):
        parser.add_argument(
            '-i',
            '--iterations',
            nargs='?',
            type=int,
            help='The number of iterations the algorithm will go through. If not provided, the algorithm will stop upon convergence.'
        )

        parser.add_argument(
            '-d',
            '--dumping_factor',
            type = float,
            default = 0.85,
            help='The dumping factor to use in the pagerank algorithm',
        )

        parser.add_argument(
            '-e',
            '--epsilon',
            type = float,
            default = 0.0001,
            help='The tolerance for the algorithn. This value is used to determine if convergence has been achieved.',
        )

    def handle(self, *args, **kwargs):
        self.update_ranks(
            self.page_rank(
                self.generate_web_graph(
                    self.clean_links()
                ),
                iterations = kwargs['iterations'],
                dumping_factor=kwargs['dumping_factor'],
                epsilon=kwargs['epsilon']
            )
        )