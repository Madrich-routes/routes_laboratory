from collections import defaultdict
from typing import List, Dict

import pandas as pd

from madrich.models.rich_vrp.plan import Plan
from madrich.models.rich_vrp.solution import MDVRPSolution
from madrich.solvers.vrp_cli.converters import ts_to_rfc


def export_to_excel(data: dict, path: str):
    with pd.ExcelWriter(path) as writer:
        st = data['statistics']
        tm = st['times']
        dataframe = {'A': ['cost', 'distance', 'duration', 'driving', 'serving', 'waiting'],
                     'B': [st['cost'], st['distance'], st['duration'], tm['driving'], tm['serving'], tm['waiting']]}
        df = pd.DataFrame(dataframe)
        df.to_excel(writer, sheet_name=f'info', index=False, header=False)

        for courier in data['solved']:
            dataframe = defaultdict(list)

            for stop in courier['stops']:
                dataframe['name'].append(stop['name'])
                dataframe['activity'].append(stop['activity'])
                dataframe['point_id'].append(stop['job_id'])
                location = stop['location']
                dataframe['location'].append(f'{location["lat"]}, {location["lon"]}')
                dataframe['arrival'].append(stop['time']['arrival'])
                dataframe['departure'].append(stop['time']['departure'])

            df = pd.DataFrame(dataframe)
            df.to_excel(writer, sheet_name=f'courier_id {courier["id"]}', index=False, startcol=3)
            dataframe = {'A': ['id', 'profile', 'name'], 'B': [courier['id'], courier['profile'], courier['name']]}
            df = pd.DataFrame(dataframe)
            df.to_excel(writer, sheet_name=f'courier_id {courier["id"]}', index=False, header=False, startrow=1)


def export(solution: MDVRPSolution) -> dict:
    """
     Конвертируем MDVRPSolution для нашего API.

    Parameters
    ----------
    solution: MDVRPSolution,

    Returns
    -------
    """
    global_stat = {
        "cost": 0,
        "distance": 0,
        "duration": 0,
        "times": {
            "driving": 0,
            "serving": 0,
            "waiting": 0,
            "break": 0,
        },
    }

    tours: List[Dict[str, dict]] = []
    # собираем стоимость выхода всех курьеров
    fixed_costs = 0
    for _, routes in solution.routes.items():
        fixed_costs += export_routes(tours, global_stat, routes, solution)

    # добавляем посчитанные стоимости выходов всех курьеров
    global_stat["cost"] += fixed_costs
    res = {
        "solved": tours,
        "statistics": global_stat,
    }

    return res


def collect_stops(plan: Plan) -> list:
    stops = []
    for i, visit in enumerate(plan.waypoints):  # проходим по каждой доставке
        # собираем посещения
        if i == 0:
            activity = "departure"  # выехал со склада
        elif i == (len(plan.waypoints) - 1):
            activity = "arrival"  # точка или склад
        else:
            activity = "delivery"  # приехал на склад
        stop = {
            "name": visit.place.name,
            "activity": activity,
            "point_id": visit.place.id,
            "location": {"lat": visit.place.lat, "lon": visit.place.lon},
            "time": {"arrival": ts_to_rfc(visit.arrival), "departure": ts_to_rfc(visit.departure)},
        }
        stops.append(stop)
    return stops


def export_routes(tours: List[dict], global_stat: dict, routes: List[Plan], solution: MDVRPSolution) -> float:
    sum_dist = 0  # собираем неучтенку за переезды между складами
    sum_time = 0  # тоже неучтенка, но время

    if not routes:
        return 0
    agent = routes[0].agent

    tour = {
        'id': agent.id,
        'profile': agent.profile,
        'name': agent.name,
        'stops': []
    }

    for j, plan in enumerate(routes):  # каждый route относится к конкретному агенту
        if j != 0:
            prev_depot = routes[j].waypoints[0].place  # неучтеночка
            curr_depot = routes[j - 1].waypoints[0].place
            sum_dist += solution.problem.depots_mapping.dist(prev_depot, curr_depot, agent.profile)
            sum_time += solution.problem.depots_mapping.time(prev_depot, curr_depot, agent.profile)

        tour['stops'] += collect_stops(plan)
        global_stat = update_statistic(global_stat, plan.info)

    tours.append(tour)

    global_stat["distance"] += sum_dist
    global_stat["duration"] += sum_time
    global_stat["times"]["driving"] += sum_time
    global_stat["cost"] += sum_dist * agent.costs["distance"] + sum_time * agent.costs["time"]
    return agent.costs['fixed'] * (len(routes) - 1)


def update_statistic(global_stat: dict, local_stat: dict) -> dict:
    """
    Функция пересчера общей статистики после прохода очередного route.
    """
    global_stat["cost"] += local_stat["cost"]
    global_stat["distance"] += local_stat["distance"]
    global_stat["duration"] += local_stat["duration"]
    global_stat["times"]["driving"] += local_stat["times"]["driving"]
    global_stat["times"]["serving"] += local_stat["times"]["serving"]
    global_stat["times"]["waiting"] += local_stat["times"]["waiting"]
    global_stat["times"]["break"] += local_stat["times"]["break"]
    return global_stat
