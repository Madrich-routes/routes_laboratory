import ujson

from models.problems.base import BaseRoutingProblem
from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.solution import VRPSolution
from solvers.base import BaseSolver


class VroomSolver(BaseSolver):
    """
    Солвер, который использует vroom
    """

    def __init__(self):
        ...

    def solve(self, problem: BaseRoutingProblem) -> VRPSolution:
        pass


def problem_to_json(problem: RichVRPProblem):
    """
    RichVRPProblem -> vroom json
    """
    vehicles = [
        {
            'id': i,
            "description": str(problem.agents[i]),
            "profile": "car",  # TODO: !
            'start_index': 0,
            'end': 0,
            'capacity': problem.agents[i].type.capacity_constraints,
            'skills': problem.agents[i].type.skills,
            'time_window': [int(problem.agents[i].start_time), int(problem.agents[i].end_time)]
        }
        for i in range(len(problem.agents))
    ]

    jobs = [
        {
            'id': problem.jobs[i].id,
            'description': str(problem.jobs[i].id),
            'location': [problem.jobs[i].lon, problem.jobs[i].lat],
            'location_index': i,  # индекс на расстояние в матрице
            'service': problem.jobs[i].delay,
            'skills': problem.jobs[i].required_skills,
            'priority': problem.jobs[i].priority,
            'time_windows': problem.jobs[i].time_windows,
            'delivery': [],  # TODO: p&d
            'pickup': [],
        }
        for i in range(len(problem.jobs))
    ]

    matrix = problem.matrix.time_matrix()  # матрица временнОго расстояния
    data = {
        'vehicles': vehicles,
        'jobs': jobs,
        'matrix': matrix.tolist()
    }

    return ujson.dumps(data)


def parse_solution():
    """
    Разбираем решение, полученное VRP_CLI
    """
