import os
from typing import List, Tuple

import numpy as np

from benchmark import Benchmark
from formats.tsplib import split_into_tours
from models.rich_vrp.agent import Agent
from models.rich_vrp.depot import Depot
from models.rich_vrp.geometries.geometry import DistanceMatrixGeometry
from models.rich_vrp.job import Job
from models.rich_vrp.problem import RichVRPProblem
from utils.types import Array


def get_distance_matrix(nodes: List[Tuple[int, int]]) -> Array:
    count = len(nodes)
    distance_matrix = np.zeros((count, count))
    for i in range(count):
        for j in range(i, count):
            delX = nodes[i][0] - nodes[j][0]
            delY = nodes[i][1] - nodes[j][1]
            distance = (delX * delX + delY * delY) ** (1 / 2)
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance
    return distance_matrix


def parse(file: str) -> Benchmark:
    # Открываем файл проблемы
    with open(file) as f:
        text = f.readlines()
    coords_start = 9 if file.startswith('sources/Solomon') else 8
    # Получаем необходимые данные
    count = int(text[2].split(":")[1])
    vehicle = int(text[3].split(":")[1])
    capacity = int(text[4].split(":")[1])
    service_time = int(text[5].split(":")[1])
    coords = text[coords_start: coords_start + count]
    demands = text[coords_start + count + 1: coords_start + 2 * count + 1]
    time_windows = text[coords_start + 2 * count + 2: coords_start + 3 * count + 2]
    # Приводим к необходимому формату
    nodes = [(int(coords[i].split()[1]), int(coords[i].split()[2])) for i in range(len(coords))]
    matrix = get_distance_matrix(nodes)

    agents_list = []
    for i in range(vehicle):
        agent = Agent(
            id=i,
            value=[capacity],
            time_windows=[(int(time_windows[0].split()[1]), int(time_windows[0].split()[2]))],
            costs=None,
            start_place=0,
            end_place=0,
            type=None,
        )
        agents_list.append(agent)
    jobs_list = []
    for i in range(1, count):
        time_window = [(int(time_windows[i].split()[1]), int(time_windows[i].split()[2]))]
        job = Job(
            id=i,
            x=nodes[i][0],
            y=nodes[i][1],
            time_windows=time_window,
            delay=service_time,
            amounts=np.array(demands[i]),
        )
        jobs_list.append(job)

    depot = Depot(
        0,
        (int(time_windows[0].split()[1]), int(time_windows[0].split()[2])),
        float(nodes[0][0]),
        float(nodes[0][1]),
        0,
        '',
    )
    problem = RichVRPProblem(
        DistanceMatrixGeometry(np.array([]), matrix, 1), agents_list, jobs_list, [depot], []
    )

    # Достаем правильное решение
    path_parts = file.split('/')
    solution_dir = '/'.join(path_parts[0: len(path_parts) - 1])
    filename_start = '.'.join(path_parts[-1].split('.')[:-1])
    solution_file = [
        f
        for f in os.listdir(solution_dir)
        if os.path.isfile(os.path.join(solution_dir, f)) and f.startswith(filename_start)
    ][0]
    # Длинна лучешго маршрута
    best_known_lenght = int(solution_file.split('.')[-2])
    with open(solution_dir + '/' + solution_file) as f:
        text = f.readlines()
    # Получаем необходимые данные о решении
    tour_len = int(text[4].split(":")[1])
    tour_start = 6
    node_indexes = text[tour_start: tour_start + tour_len]
    raw_tour = [int(node_indexes[i]) for i in range(len(node_indexes))]
    tours = split_into_tours(raw_tour, count)
    return Benchmark(problem, best_known_lenght, tours)


def get_benchmarks(nodes_count: int = None, benchmarks_count: int = None) -> List[Benchmark]:
    directories = [
        'sources/Solomon_25',
        'sources/Solomon_50',
        'sources/Solomon_100',
        'sources/Homberger_200',
        'sources/Homberger_400',
        'sources/Homberger_600',
        'sources/Homberger_800',
        'sources/Homberger_1000',
    ]
    if nodes_count == 25:
        files = [
            directories[0] + '/' + f
            for f in os.listdir(directories[0])
            if os.path.isfile(os.path.join(directories[0], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 50:
        files = [
            directories[1] + '/' + f
            for f in os.listdir(directories[1])
            if os.path.isfile(os.path.join(directories[1], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 100:
        files = [
            directories[2] + '/' + f
            for f in os.listdir(directories[2])
            if os.path.isfile(os.path.join(directories[2], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 200:
        files = [
            directories[3] + '/' + f
            for f in os.listdir(directories[3])
            if os.path.isfile(os.path.join(directories[3], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 400:
        files = [
            directories[4] + '/' + f
            for f in os.listdir(directories[4])
            if os.path.isfile(os.path.join(directories[4], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 600:
        files = [
            directories[5] + '/' + f
            for f in os.listdir(directories[5])
            if os.path.isfile(os.path.join(directories[5], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 800:
        files = [
            directories[6] + '/' + f
            for f in os.listdir(directories[6])
            if os.path.isfile(os.path.join(directories[6], f)) and f.endswith('.vrptw')
        ]
    elif nodes_count == 1000:
        files = [
            directories[7] + '/' + f
            for f in os.listdir(directories[7])
            if os.path.isfile(os.path.join(directories[7], f)) and f.endswith('.vrptw')
        ]
    else:
        files = []
        for directory in directories:
            files += [
                directory + '/' + f
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and f.endswith('.vrptw')
            ]

    if nodes_count is not None and benchmarks_count < len(files):
        files = files[:benchmarks_count]
    res = [parse(file) for file in files]
    return res


if __name__ == "__main__":
    get_benchmarks(600, 10)
    k = 0
    # parse('sources/Solomon_25/C101.25.3.vrptw')
