import json
from dataclasses import dataclass
from typing import Tuple, List, Dict, Optional

Point = Tuple[float, float]


@dataclass
class Task:
    location: Point  # lat lot
    times: List[Tuple[str, str]]  # временные окна
    delay: float  # время обслуживания на точке
    value: List[int]  # объем груза


@dataclass
class Depot:
    location: Point  # lat lot
    load: float  # время загрузки
    reload: float  # время перезагрузки


@dataclass
class Vehicle:
    car_type: str  # что это такое
    type_id: str  # индетификатор транспортного средства (название какое-нибудь)
    profile: str  # имя профиля маршрутизации
    costs: Dict[str, float]  # на сколько дорого обходится использования средства (fixed, time, distance)
    value: List[int]  # вместимость
    max_time: float  # максимальное время работы
    max_distance: float  # максимальная дальность
    start_time: str  # время начала работы
    end_time: str  # время конца работы
    start_place: Point  # стартовая точка
    end_place: Point  # конечная точка прибытия


@dataclass
class Tour:
    vehicle_id: str
    type_id: str
    statistic: dict
    stops: List[dict]


@dataclass
class Solution:
    statistic: dict
    tours: List[Tour]
    unassigned: Optional[dict]


def convert_json(file_name: str):
    with open(f'{file_name}.json', 'r') as f:
        solution = json.load(f)
    _statistics = solution['statistic']
    _tours = []
    for tour in solution['tours']:
        _tour = Tour(tour['vehicleId'], tour['typeId'], tour['stops'], tour['statistic'])
        _tours.append(_tour)
    _unassigned = None if 'unassigned' not in solution else solution['unassigned']
    return Solution(_statistics, _tours, _unassigned)


def generate_json(file_name: str, tasks: List[Task], depot: Depot, vehicles: List[Tuple[int, Vehicle]]):
    _jobs = []
    for i, task in enumerate(tasks):
        _job = {
            'id': f'job{i}',
            'deliveries': [{
                'places': [{
                    'location': {'lat': task.location[0], 'lng': task.location[1]},
                    'duration': task.delay,
                    'times': task.times
                }],
                'demand': task.value
            }]
        }
        _jobs.append(_job)

    _vehicles = []
    for i, (num, vehicle) in enumerate(vehicles):
        _vehicle = {
            'typeId': vehicle.type_id,
            'vehicleIds': [f'{vehicle.type_id}_{j}' for j in range(num)],
            'profile': vehicle.profile,
            'costs': vehicle.costs,
            'shifts': [{
                'start': {
                    'earliest': vehicle.start_time,
                    'location': {'lat': vehicle.start_place[0], 'lng': vehicle.start_place[1]}
                },
                'end': {
                    'latest': vehicle.end_time,
                    'location': {'lat': vehicle.end_place[0], 'lng': vehicle.end_place[1]}
                },
                'reloads': [{
                    'location': {'lat': depot.location[0], 'lng': depot.location[1]},
                    'duration': depot.reload
                }],
                'depots': [{
                    'location': {'lat': depot.location[0], 'lng': depot.location[1]},
                    'duration': depot.load
                }]
            }],
            'capacity': vehicle.value
        }
        _vehicles.append(_vehicle)

    _profiles = []
    for _, vehicle in vehicles:
        _profiles.append({'name': vehicle.profile, 'type': vehicle.car_type})

    _problem = {'plan': {'jobs': _jobs}, 'fleet': {'vehicles': _vehicles, 'profiles': _profiles}}

    with open(f'{file_name}.json', 'w') as f:
        json.dump(_problem, f)
