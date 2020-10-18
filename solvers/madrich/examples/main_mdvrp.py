import faulthandler
import logging
from time import time

from madrich.problems.mdvrp_demo.generators import generate_mdvrp
from madrich.problems.mdvrp_demo.mdvrp_problem import ProblemMdvrp
# from madrich.problems.mdvrp_demo.utils import draw_mdvrp
from madrich.problems.mdvrp_demo.operators.improve import improve_tour

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

storages, couriers, matrix = generate_mdvrp(50, 4, 10)
problem = ProblemMdvrp()
tour = problem.init(2, storages, couriers, matrix)

# draw_mdvrp(storages, tour)

t = time()
improve_tour(tour, problem, False, False)
logging.info(f'\nTIME: {time() - t:0.1f} sec')

# draw_mdvrp(storages, tour)
