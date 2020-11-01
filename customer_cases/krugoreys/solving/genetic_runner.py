import os
import uuid
from typing import List, Tuple

import ujson as json
from autologging import logged, traced
from solving.models import DistanceMatrix, Solution, Task, Tour, Vehicle


@traced
def run_genetic_solver(
        tasks: List[Task], vehicles: List[Tuple[int, Vehicle]], matrix: DistanceMatrix
):
    proc_id = uuid.uuid4()
    file = f"{proc_id}"
    generate_json(file, tasks, vehicles, matrix)
    os.system(
        f"vrp-cli solve pragmatic {file}.json -m {file}_routing_matrix.json -o {file}_solution.json"
        f"--log --max-time=600"
    )
    solution = convert_json(f"{file}_solution")

    # os.remove(f'{file}.json')
    # os.remove(f'{file}_routing_matrix.json')
    # os.remove(f'{file}_solution.json')

    return solution


@traced
def convert_json(file_name: str):
    with open(f"{file_name}.json", "r") as f:
        solution = json.load(f)
    _statistics = solution["statistic"]
    _tours = []
    for tour in solution["tours"]:
        _tour = Tour(
            tour["vehicleId"], tour["typeId"], tour["stops"], tour["statistic"]
        )
        _tours.append(_tour)
    _unassigned = None if "unassigned" not in solution else solution["unassigned"]
    return Solution(_statistics, _tours, _unassigned)


@traced
def generate_json(
        file: str,
        tasks: List[Task],
        vehicles: List[Tuple[int, Vehicle]],
        matrix: DistanceMatrix,
):
    jobs = []
    for i, task in enumerate(tasks):
        job = {
            "id": f"job{i}",
            "deliveries": [
                {
                    "places": [
                        {
                            "location": {"index": task.id},
                            "duration": task.delay,
                            # "times": [[task.tw_start, task.tw_end]],
                        }
                    ],
                    "demand": [10],
                }
            ],
        }
        jobs.append(job)
    cars = []
    for i, (num, vehicle) in enumerate(vehicles):
        car = {
            "typeId": f"car_{i}",
            "vehicleIds": [f"car_{i}_{j}" for j in range(num)],
            "profile": "normal_car",
            "costs": vehicle.costs,
            "shifts": [
                {
                    "start": {
                        "earliest": vehicle.start_time,
                        "location": {"index": vehicle.start_place},
                    }
                }
            ],
            "capacity": [vehicle.value],
        }
        cars.append(car)

    profiles = [{"name": "normal_car", "type": "car"}]
    problem = {
        "plan": {"jobs": jobs},
        "fleet": {"vehicles": cars, "profiles": profiles},
    }

    with open(f"{file}.json", "w") as f:
        json.dump(problem, f)

    size = len(matrix.dist_matrix)
    travel_times, time_m = [], matrix.time_matrix
    for i in range(size):
        for j in range(size):
            travel_times.append(int(time_m[i][j]))
    distances, distance_m = [], matrix.dist_matrix
    for i in range(size):
        for j in range(size):
            distances.append(int(distance_m[i][j]))
    routing = {
        "profile": "normal_car",
        "travelTimes": travel_times,
        "distances": distances,
    }

    with open(f"{file}_routing_matrix.json", "w") as f:
        json.dump(routing, f)
