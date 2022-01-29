import numpy as np
from django.core.management.base import BaseCommand
from generic_search.searchbot.utils.pagerank import page_rank, update_ranks, generate_web_graph
np.set_printoptions(threshold=np.inf)

class Command(BaseCommand):
    help = 'Triggers the searchbot crawler to crawl this site'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'iterations',
            nargs='?',
            metavar='n',
            type=int,
            help='The number of iterations the algorithm will go through'
        )

        # Named (optional) arguments
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
            default = None,
            help='The tolerance for the algorithn. This value is used to determine if convergence has been achieved.',
        )

    def handle(self, *args, **kwargs):
       update_ranks(page_rank(
           generate_web_graph(),
           kwargs['iterations'],
           dumping_factor=kwargs['dumping_factor'],
           epsilon=kwargs['epsilon']
           )
       )