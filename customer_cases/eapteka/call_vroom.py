import ujson, sys, subprocess, os, re, pickle
import numpy as np
import pandas as pd
from datetime import datetime, time

from geo.providers import osrm
from models.rich_vrp.problem import RichVRPProblem
from models.rich_vrp.geometry import DistanceMatrixGeometry
from models.rich_vrp.agent import Agent
from models.rich_vrp.agent_type import AgentType
from models.rich_vrp.costs import AgentCosts
from models.rich_vrp.visit import Visit
from models.rich_vrp.solution import VRPSolution
from models.rich_vrp.job import Job
from models.problems.base import BaseRoutingProblem
from geo.transforms import line_distance_matrix
'''
Функция генерации тестовой проблемы и депо
'''


def get_test_problem():
    np_dist_matrix = np.array([[0, 3, 5, 8], [3, 0, 2, 5], [5, 2, 0, 3], [8, 5, 3, 0]])
    dist_matrix = DistanceMatrixGeometry(np.array([]), np_dist_matrix, 10)

    costs = {"fixed": 100, "time": 3, "distance": 5}
    value = [10000]
    start = int(datetime(2020, 10, 16, 8, 00).timestamp())
    end = int(datetime(2020, 10, 16, 20, 00).timestamp())
    start_place = 0
    end_place = 0
    agent_cost = AgentCosts(5, 100, 2, 3, 5)
    agent_type = AgentType(100, 0, [50], agent_cost, [2, 3])
    agent = Agent(0, costs, value, start,end, start_place, end_place, agent_type)
    j1 = Job(0, 0, 0, 0, 0, [(int(datetime(2020, 10, 16, 10, 00).timestamp()), int(datetime(2020, 10, 16, 11, 00).timestamp()))], 5, np.array([10]), [2], 5)
    j2 = Job(1, 0, 3, 0, 3, [(int(datetime(2020, 10, 16, 11, 00).timestamp()), int(datetime(2020, 10, 16, 12, 00).timestamp()))], 5, np.array([10]), [3], 5)
    j3 = Job(2, 0, 5, 0, 5, [(int(datetime(2020, 10, 16, 12, 00).timestamp()), int(datetime(2020, 10, 16, 13, 00).timestamp()))], 5, np.array([10]), [3], 5)
    j4 = Job(3, 0, 8, 0, 8, [(int(datetime(2020, 10, 16, 21, 00).timestamp()), int(datetime(2020, 10, 16, 22, 00).timestamp()))], 5, np.array([10]), [3], 5)
    res = RichVRPProblem(dist_matrix, [agent], [j1, j2, j3, j4], [''])
    return res


'''
Преобразование RichVRPProblem в json
'''


def problem_to_json(problem, path):
    vehicles = [{'id': i,
                 'start_index': 0,                                  # начало маршрута примем за 0 точку в матрице
                 'capacity': problem.agents[i].value,
                 #  'skills': problem.agents[i].type.skills,
                 'time_window': [problem.agents[i].start_time, problem.agents[i].end_time]}
                for i in range(len(problem.agents))]
    jobs = [{'id': problem.jobs[i].id,
             'location': [problem.jobs[i].lon, problem.jobs[i].lat],
             'location_index': i+1,                                    # индекс на расстояние в матрице
             'service': problem.jobs[i].delay,
            #  'skills': problem.jobs[i].required_skills,
             'priority': problem.jobs[i].priority,
             'delivery': problem.jobs[i].amounts.tolist(),
             'time_windows': problem.jobs[i].time_windows}
            for i in range(len(problem.jobs))]
    matrix = problem.matrix.d  # матрица временнОго расстояния

    data = {'vehicles': vehicles, 'jobs': jobs, 'matrix': matrix.tolist()}
    with open(path, 'w') as f:
        ujson.dump(data, f)

'''
Конвертация решения от vroom в Excel
'''
def read_out_json(path, excel_path):
    with open(path) as data_file:    
        data = ujson.load(data_file)
        toursList = []
        for route in data['routes']:
            tour = []
            for i in range(len(route['steps'])):
                if(route['steps'][i]['type'] == 'job'):
                    job = Job(id = route['steps'][i]['id'],
                                lon = route['steps'][i]['location'][0],
                                lat = route['steps'][i]['location'][1],
                                delay = route['steps'][i]['service'],
                                amounts= np.array(route['steps'][i-1]['load']) - np.array(route['steps'][i]['load']))
                    job.amounts = job.amounts.astype(float)
                    job.amounts[0] /= 1000
                    job.amounts[1] /= 1000000
                    visit = Visit(job, route['steps'][i]['arrival'])
                    tour.append(visit)
            toursList.append(tour)
        
        solution = VRPSolution(BaseRoutingProblem(np.empty((1,1))), toursList)
        solution.to_excel(excel_path)

def get_eapteka_problem():
    stock = [55.8075060, 37.6053370] #координаты склада на марьиной роще
    coords = pd.read_excel("data/update_3.xlsx")
    info = pd.read_excel("data/Заказы_13.xlsx")
    agents = pd.read_excel("data/Курьеры_13.xlsx")
    data = coords.join(info)

    #ровняем данные
    regex = r'Доставка с ([0-9]{0,2}).* по ([0-9]{0,2}).*$'
    times = data['ИнтервалДоставки']
    t_from = times.map(lambda x: re.search(regex, x).group(1))
    t_to = times.map(lambda x: re.search(regex, x).group(2))
    t_from.unique()
    t_to.unique()
    # фиксим отсутствующие
    t_to[t_to == ''] = '24'
    t_from[t_from == ''] = '00'
    # фиксим типы данных
    t_to = t_to.astype(int)
    t_from = t_from.astype(int)
    # фиксим нерабочие окна
    t_to[t_to <= t_from] = 24
    data['t_from'] = t_from
    data['t_to'] = t_to
    data['ВесЗаказа'] = data['ВесЗаказа'].fillna(0)
    data['ОбъемЗаказа'] = data['ОбъемЗаказа'].fillna(0)
    data['Приоритет'] = data['Приоритет'].fillna(0)

    #собираем агентов
    agents_list = []
    for i in range(len(agents.index)):   
        row = agents.iloc[i]
        if row['Должность'] == 'Курьер':
            value = [100*1000, 500*1000000]
        else:
            value = [10*1000, 50*1000000]
        time_interval = row['Интервал работы'].split('-')
        start = int(datetime(2020, 10, 16, int(time_interval[0]), 00).timestamp())
        if time_interval[1] == '24':
            end = int(datetime(2020, 10, 16, 23, 59).timestamp())
        else:
            end = int(datetime(2020, 10, 16, int(time_interval[1]), 00).timestamp())
        
        agent = Agent(id=i,value=value,start_time=start,end_time=end, costs=None, start_place = 0, end_place=0, type=None)
        agents_list.append(agent)
    
    #собираем заказы
    jobs_list = []
    for  i in range(len(data.index)): 
        row = data.iloc[i]
        window_to = int(datetime(2020, 10, 16, 23, 59).timestamp()) if row['t_to'] == 24 else int(datetime(2020, 10, 16, row['t_to'], 00).timestamp())
        time_windows = [(int(datetime(2020, 10, 16, row['t_from'], 00).timestamp()), window_to)]
        amounts = np.array((int(row['ВесЗаказа']*1000), int(row['ОбъемЗаказа']*1000000)))
        
        job = Job(id=i, lon=row['lng'], lat=row['lat'], time_windows=time_windows, delay=5, amounts=amounts, priority=int(row['Приоритет']))
        jobs_list.append(job)
    matrix = calculate_dist_matrix()
    problem = RichVRPProblem(DistanceMatrixGeometry(np.array([]), matrix, 200), agents_list, jobs_list, [])
    return problem

'''
Получаем матрицу, пока тупо
TODO переделать
'''
def calculate_dist_matrix(): 
    data = pd.read_excel("data/update_3.xlsx") 
    stock = [55.8075060, 37.6053370]
    points = list([row.lat, row.lng] for row in data.itertuples())
    points.insert(0, [stock[0], stock[1]]) #добавляю склад как 0 точку
    matrix = line_distance_matrix(points)
    matrix *= 1000
    np.around(matrix, 3)
    matrix = matrix.astype(int)
    return matrix

def main():
    vroom = "C:\\Users\\viuko\\Documents\\projects\\src\\cmake-build-debug\\vroom" # местонахождение бинарника vroom
    input = "tmp/eapteka_vroom_input.json" # файл ввода
    output = "tmp/eapteka_vroom_output.json"  # файл вывода
    excel_out = "data/eapteka_vroom_result.xlsx"  # файл вывода

    # problem = get_test_problem() # построение тестовой проблемы

    problem = get_eapteka_problem()
    problem_to_json(problem, input) # конвертация нашей проблемы в .json понятный для vroom
    if subprocess.run([vroom, '-i', os.path.abspath(input), '-o', os.path.abspath(output)]).returncode == 0: # вызов vroom
        print("ok")
        read_out_json(output, excel_out)
        return 0


if __name__ == "__main__":
    main()
