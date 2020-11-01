import os
from typing import Dict, List, Tuple

import numpy as np
import ujson

from customer_cases.eapteka.genetic_solver.models import Courier, Depot, Task
from utils.types import Array

Point = Tuple[float, float]
array = np.ndarray


def convert_json(file: str) -> dict:
    """
    Просто парсим и возвращаем результат солвера
    """
    with open(file, "r") as f:
        return ujson.load(f)


def generate_matrix(
        name: str,
        profiles: List[str],
        distance_matrix: Dict[str, Array],
        time_matrix: Dict[str, Array],
):
    """

    :param name: Описание матрицы расстояния
    :param profiles:
    :param distance_matrix:
    :param time_matrix:
    :return:
    :rtype:
    """
    files: List[Tuple[str, str]] = []
    size = len(distance_matrix[profiles[0]])

    if not os.path.exists("./tmp"):
        os.mkdir("./tmp")

    for profile in profiles:

        travel_times, distances = [], []
        for i in range(size):
            for j in range(size):
                travel_times.append(int(time_matrix[profile][i][j]))
                distances.append(int(distance_matrix[profile][i][j]))

        routing = {
            "profile": profile,
            "travelTimes": travel_times,
            "distances": distances,
        }

        file = f"./tmp/{name}.{profile}.routing_matrix.json"

        with open(file, "w") as f:
            ujson.dump(routing, f)

        files.append((profile, file))

    return files


def generate_problem(
        name: str,
        profiles: List[str],
        tasks: List[Task],
        depot: Depot,
        couriers: List[Courier],
) -> str:
    """
    Generate json problem file for solver
    """
    jobs = []
    for i, task in enumerate(tasks):
        job = {
            "id": f"job_{i}",
            "deliveries": [
                {
                    "places": [
                        {
                            "location": {"index": task.location},
                            "duration": task.delay,
                            "times": task.time_windows,
                        }
                    ],
                    "demand": task.value,
                }
            ],
            "priority": task.priority,
        }
        jobs.append(job)

    executors = []
    for i, courier in enumerate(couriers):
        executor = {
            "typeId": courier.type_id,
            "vehicleIds": [courier.name],
            "profile": courier.profile,
            "costs": courier.costs,
            "shifts": [
                {
                    "start": {
                        "earliest": time_window[0],
                        "location": {"index": courier.start},
                    },
                    "end": {
                        "latest": time_window[1],
                        "location": {"index": courier.end},
                    },
                    "reloads": [
                        {
                            "location": {"index": depot.location},
                            "duration": depot.reload,
                        }
                    ],
                    "depots": [
                        {"location": {"index": depot.location}, "duration": depot.load}
                    ],
                }
                for time_window in courier.time_windows
            ],
            "capacity": courier.value,
        }
        executors.append(executor)

    profiles = [{"name": profile, "type": f"{profile}_profile"} for profile in profiles]
    problem = {
        "plan": {"jobs": jobs},
        "fleet": {"vehicles": executors, "profiles": profiles},
    }

    if not os.path.exists("./tmp"):
        os.mkdir("tmp")

    file = f"./tmp/{name}.json"
    with open(file, "w") as f:
        ujson.dump(problem, f)

    return file
