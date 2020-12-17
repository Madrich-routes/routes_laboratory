import numpy as np
import ujson

from madrich.models.problems import BaseRoutingProblem
from madrich.models.rich_vrp import Job, RichVRPProblem, Visit, VRPSolution


def dumps_problem(
    problem: RichVRPProblem,
) -> str:
    """Преобразование RichVRPProblem в json."""
    vehicles = [
        {
            'id': i,
            # "description": str(problem.agents[i]),
            # "profile": "car",  # TODO: !
            'start_index': 0,  # начало маршрута примем за 0 точку в матрице
            'end': 0,

            'capacity': problem.agents[i].amounts,
            #  'skills': problem.agents[i].type.skills,
            'time_window': [problem.agents[i].time_windows[0][0], problem.agents[i].time_windows[0][1]],
        }
        for i in range(len(problem.agents))
    ]

    jobs = [
        {
            'id': problem.jobs[i].id,
            'description': str(problem.jobs[i].id),
            'location': [problem.jobs[i].lon, problem.jobs[i].lat],
            'location_index': i + 1,  # индекс на расстояние в матрице
            'service': problem.jobs[i].delay,
            #  'skills': problem.jobs[i].required_skills,
            'priority': problem.jobs[i].priority,
            'delivery': problem.jobs[i].amounts.tolist(),
            # 'pickup': [],   # TODO: p&d
            'time_windows': problem.jobs[i].time_windows,
        }
        for i in range(len(problem.jobs))
    ]

    matrix = problem.matrix.dist_matrix()  # матрица временного расстояния
    data = {'vehicles': vehicles, 'jobs': jobs, 'matrix': matrix.tolist()}
    return ujson.dumps(data)


def loads_result(solution_str: str) -> VRPSolution:
    """Загружаем решение из результата vroom.

    Parameters
    ----------
    solution_str : Решение vroom в виде строки

    Returns
    -------
    Объект VRPSolution
    """
    data = ujson.loads(solution_str)

    tours_list = []
    for route in data['routes']:
        tour = []
        for i in range(len(route['steps'])):
            if route['steps'][i]['type'] == 'job':
                job = Job(
                    id=route['steps'][i]['id'],
                    lon=route['steps'][i]['location'][0],
                    lat=route['steps'][i]['location'][1],
                    delay=route['steps'][i]['service'],
                    amounts=np.array(route['steps'][i - 1]['load']) - np.array(route['steps'][i]['load']),
                )
                job.amounts = job.amounts.astype(float)
                job.amounts[0] /= 1000
                job.amounts[1] /= 1000000
                visit = Visit(job, route['steps'][i]['arrival'])
                tour.append(visit)
        tours_list.append(tour)

    return VRPSolution(BaseRoutingProblem(np.empty((1, 1))), tours_list)
