from datetime import datetime
from typing import Dict

from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.solution import MDVRPSolution

import pandas as pd


def export_to_exel(data: dict, path: str):
    status = {
        'Статус': [data['status']],
        'Статус прогресса': [data['progress_status']],
    }
    status_df = pd.DataFrame(status)

    solved = data['solved']

    couriers = [solved[i] for i in solved.keys()]
    couriers_df = pd.DataFrame(couriers)[['type', 'courier_id', 'statistic']]
    couriers_df[['cost', 'distance', 'duration']] = pd.DataFrame(couriers_df['statistic'].to_list())
    del couriers_df['statistic']
    couriers_df.columns = [
        'Тип',
        'Курьер',
        'Цена',
        'Дистанция',
        'Время',
    ]

    couriers_activity = [solved[i]['stops'] for i in solved.keys()]
    activity = []
    for cur_list in range(len(couriers_activity)):
        for act in couriers_activity[cur_list]:
            act['courier_id'] = couriers[cur_list]['courier_id']
        activity += couriers_activity[cur_list]
    activity_df = pd.DataFrame(activity)
    activity_df[['lat', 'lon']] = pd.DataFrame(activity_df['location'].to_list())
    activity_df[['arrival', 'departure']] = pd.DataFrame(activity_df['time'].to_list())
    del activity_df['location']
    del activity_df['time']

    activity_df = activity_df[[
        'courier_id',
        'activity',
        'distance',
        'load',
        'job_id',
        'lat',
        'lon',
        'arrival',
        'departure'
    ]]
    activity_df.columns = [
        'Курьер',
        'Действие',
        'Дистанция',
        'Загрузка',
        'Заказ',
        'Широта',
        'Долгота',
        'Время отправки',
        'Время прибытия',
    ]

    unassigned_df = pd.DataFrame(data['unassigned'])
    unassigned_df.columns = [
        'Заказ',
        'Причина',
    ]
    info = {
        'Стратегия': [data['info']['strategy_used']],
        'Время получения': [data['info']['time_received']],
        'Время вычислений': [data['info']['time_computed']],
    }
    info_df = pd.DataFrame(info)

    statistics = data['statistics']
    statistics['driving'] = data['statistics']['times']['driving']
    statistics['serving'] = data['statistics']['times']['serving']
    statistics['waiting'] = data['statistics']['times']['waiting']
    statistics['break'] = data['statistics']['times']['break']
    statistics = {
        'Стоимость': [data['statistics']['cost']],
        'Дистанция': [data['statistics']['distance']],
        'Время': [data['statistics']['duration']],
        'Время в пути': [data['statistics']['driving']],
        'Время упаковки': [data['statistics']['serving']],
        'Время ожидания': [data['statistics']['waiting']],
        'Время бездействия': [data['statistics']['break']],
    }
    statistics_df = pd.DataFrame(statistics)

    with pd.ExcelWriter(path, datetime_format='DD.MM.YYYY HH:MM:SS') as writer:
        status_df.to_excel(writer, sheet_name='Статус')
        couriers_df.to_excel(writer, sheet_name='Курьеры')
        activity_df.to_excel(writer, sheet_name='Решения')
        unassigned_df.to_excel(writer, sheet_name='Не использованные')
        info_df.to_excel(writer, sheet_name='Информация')
        statistics_df.to_excel(writer, sheet_name='Статистика')


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
        "cost": sum([agent.costs["fixed"] for agent in solution.problem.agents]),
        "distance": 0,
        "duration": 0,
        "times": {
            "driving": 0,
            "serving": 0,
            "waiting": 0,
            "break": 0,
        },
    }
    tours = []
    for agent_id, plans in solution.routes.items():
        for plan in plans:
            if len(plan.waypoints) > 2:
                stops = []
                sum_dist = 0
                # проходим по каждой доставке
                for i, visit in enumerate(plan.waypoints):
                    distance = 0  # if i == 0 else solution.problem.sub_problems
                    sum_dist += distance
                    # собираем посещения
                    if i == 0:
                        activity = "departure"
                    elif i == (len(plan.waypoints) - 1):
                        activity = "arrival"
                    else:
                        activity = "delivery"
                    stop = {
                        "activity": activity,
                        "distance": distance,
                        "load": visit.place.capacity_constraints if isinstance(visit.place, Job) else [],
                        "job_id": visit.place.id,
                        "location": {"lat": visit.place.lat, "lan": visit.place.lon},
                        "time": {
                            "arrival": datetime.fromtimestamp(visit.arrival).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "departure": datetime.fromtimestamp(visit.departure).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        },
                    }
                    stops.append(stop)
                tour = {
                    "type": plan.agent.profile,
                    "courier_id": plan.agent.id,
                    "statistic": {
                        "cost": plan.info["cost"],
                        "distance": sum_dist,
                        "duration": plan.info["duration"],
                    },
                    "stops": stops,
                }
                global_stat = update_statistic(global_stat, plan.info)
                dep_name = plan.waypoints[0].place.name
                tours.append((dep_name, tour))
    res = {
        "status": "solved",
        "progress_status": "solved",
        "solved": {dep_name: tour for dep_name, tour in tours},
        "unassigned": [{"job_id": "job_0", "reason": "because"}],
        "info": {
            "strategy_used": "genetic",
            "time_received": "2020-10-01T10:00:00Z",
            "time_computed": "2020-10-01T10:05:00Z",
        },
        "statistics": global_stat,
    }

    return res


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
