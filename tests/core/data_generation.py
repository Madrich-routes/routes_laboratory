import numpy as np

from models.rich_vrp.agent import Agent
from models.rich_vrp.agent_type import AgentType
from models.rich_vrp.costs import AgentCosts
from models.rich_vrp.geometries.geometry import DistanceMatrixGeometry
from models.rich_vrp.job import Job
from models.rich_vrp.problem import RichVRPProblem


def get_test_problem():
    """Функция генерации тестовой проблемы и депо."""
    np_dist_matrix = np.array([[0, 3, 5], [3, 0, 2], [5, 2, 0]])
    dist_matrix = DistanceMatrixGeometry(np.array([]), np_dist_matrix, 10)

    costs = {"fixed": 100, "time": 3, "distance": 5}
    value = [10000]
    start = '0'
    end = '10000'
    start_place = 0
    end_place = 0
    agent_cost = AgentCosts(5, 100, 2, 3, 5)
    agent_type = AgentType(100, 0, [50, 20], agent_cost, [2, 3])
    agent = Agent(0, costs, value, start, end, start_place, end_place, agent_type)
    j1 = Job(0, 0, 0, 0, 0, [(10, 20)], 5, np.array([10]), [2], 5)
    j2 = Job(1, 0, 3, 0, 3, [(30, 50)], 5, np.array([10]), [3], 5)
    j3 = Job(2, 0, 5, 0, 5, [(60, 80)], 5, np.array([10]), [3], 5)

    return RichVRPProblem(dist_matrix, [agent], [j1, j2, j3], [''])
