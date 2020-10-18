import faulthandler
import logging

from madrich.problems.vrp_demo.generators import generate_vrp
from madrich.problems.vrp_demo.vrp_problem import ProblemVrp
from madrich.problems.vrp_demo.search import SearchEngine

faulthandler.enable()
logging.basicConfig(format='%(message)s', level=logging.INFO)

jobs, couriers, _, storage = generate_vrp(40)
engine = SearchEngine(jobs, couriers, storage, ProblemVrp(), False)
engine.improve()

jobs, _, _, _ = generate_vrp(40, 'storage_2')
engine.insert_jobs(jobs)
engine.improve()
