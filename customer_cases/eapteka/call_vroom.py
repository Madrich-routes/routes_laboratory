import numpy as np
import os
import subprocess
import ujson

from models.rich_vrp.agent import Agent
from models.rich_vrp.agent_type import AgentType
from models.rich_vrp.costs import AgentCosts
from models.rich_vrp.geometry import DistanceMatrixGeometry
from models.rich_vrp.job import Job
from models.rich_vrp.problem import RichVRPProblem

'''
Функция генерации тестовой проблемы и депо
'''


def get_test_problem():
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
    res = RichVRPProblem(dist_matrix, [agent], [j1, j2, j3], [''])
    return res


'''
Преобразование RichVRPProblem в json
'''


def problem_to_json(problem, path):
    vehicles = [{'id': i,
                 'start_index': 0,  # начало маршрута примем за 0 точку в матрице
                 'end': 0,  # конец маршрута примем за 0 точку в матрице
                 'capacity': problem.agents[i].type.capacity_constraints,
                 'skills': problem.agents[i].type.skills,
                 'time_window': [int(problem.agents[i].start_time), int(problem.agents[i].end_time)]}
                for i in range(len(problem.agents))]
    jobs = [{'id': problem.jobs[i].id,
             'location': [problem.jobs[i].lon, problem.jobs[i].lat],
             'location_index': i,  # индекс на расстояние в матрице
             'service': problem.jobs[i].delay,
             'skills': problem.jobs[i].required_skills,
             'priority': problem.jobs[i].priority,
             'time_windows': problem.jobs[i].time_windows}
            for i in range(len(problem.jobs))]
    matrix = problem.matrix.d  # матрица временнОго расстояния

    data = {'vehicles': vehicles, 'jobs': jobs, 'matrix': matrix.tolist()}
    with open(path, 'w') as f:
        ujson.dump(data, f)


def main():
    vroom = "C:\\Users\\viuko\\Documents\\projects\\src\\cmake-build-debug\\vroom"  # местонахождение бинарника vroom
    input = "./tmp/vroom_input.json"  # файл ввода
    output = "./tmp/vroom_output.json"  # файл вывода
    problem = get_test_problem()  # построение тестовой проблемы
    problem_to_json(problem, input)  # конвертация нашей проблемы в .json понятный для vroom
    if subprocess.run(
            [vroom, '-i', os.path.abspath(input), '-o', os.path.abspath(output)]).returncode == 0:  # вызов vroom
        print("ok")
        return 0


if __name__ == "__main__":
    main()
