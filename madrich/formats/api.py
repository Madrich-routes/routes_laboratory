from datetime import datetime
from typing import Dict

from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.solution import MDVRPSolution

import pandas as pd


def export_to_exel(data: dict, path: str):
    status = {
        "Статус": [data["status"]],
        "Статус прогресса": [data["progress_status"]],
    }
    status_df = pd.DataFrame(status)

    solved = data["solved"]

    couriers = [solved[i] for i in solved.keys()]
    couriers_df = pd.DataFrame(couriers)[["type", "courier_id", "statistic"]]
    couriers_df[["cost", "distance", "duration"]] = pd.DataFrame(couriers_df["statistic"].to_list())
    del couriers_df["statistic"]
    couriers_df.columns = [
        "Тип",
        "Курьер",
        "Цена",
        "Дистанция",
        "Время",
    ]

    couriers_activity = [solved[i]["stops"] for i in solved.keys()]
    activity = []
    for cur_list in range(len(couriers_activity)):
        for act in couriers_activity[cur_list]:
            act["courier_id"] = couriers[cur_list]["courier_id"]
        activity += couriers_activity[cur_list]
    activity_df = pd.DataFrame(activity)
    activity_df[["lat", "lon"]] = pd.DataFrame(activity_df["location"].to_list())
    activity_df[["arrival", "departure"]] = pd.DataFrame(activity_df["time"].to_list())
    del activity_df["location"]
    del activity_df["time"]

    activity_df = activity_df[
        ["courier_id", "activity", "distance", "load", "job_id", "lat", "lon", "arrival", "departure"]
    ]
    activity_df.columns = [
        "Курьер",
        "Действие",
        "Дистанция",
        "Загрузка",
        "Заказ",
        "Широта",
        "Долгота",
        "Время отправки",
        "Время прибытия",
    ]

    unassigned_df = pd.DataFrame(data["unassigned"])
    unassigned_df.columns = [
        "Заказ",
        "Причина",
    ]
    info = {
        "Стратегия": [data["info"]["strategy_used"]],
        "Время получения": [data["info"]["time_received"]],
        "Время вычислений": [data["info"]["time_computed"]],
    }
    info_df = pd.DataFrame(info)

    statistics = data["statistics"]
    statistics["driving"] = data["statistics"]["times"]["driving"]
    statistics["serving"] = data["statistics"]["times"]["serving"]
    statistics["waiting"] = data["statistics"]["times"]["waiting"]
    statistics["break"] = data["statistics"]["times"]["break"]
    statistics = {
        "Стоимость": [data["statistics"]["cost"]],
        "Дистанция": [data["statistics"]["distance"]],
        "Время": [data["statistics"]["duration"]],
        "Время в пути": [data["statistics"]["driving"]],
        "Время упаковки": [data["statistics"]["serving"]],
        "Время ожидания": [data["statistics"]["waiting"]],
        "Время бездействия": [data["statistics"]["break"]],
    }
    statistics_df = pd.DataFrame(statistics)

    with pd.ExcelWriter(path, datetime_format="DD.MM.YYYY HH:MM:SS") as writer:
        status_df.to_excel(writer, sheet_name="Статус")
        couriers_df.to_excel(writer, sheet_name="Курьеры")
        activity_df.to_excel(writer, sheet_name="Решения")
        unassigned_df.to_excel(writer, sheet_name="Не использованные")
        info_df.to_excel(writer, sheet_name="Информация")
        statistics_df.to_excel(writer, sheet_name="Статистика")


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
    tours = []
    # собираем стоимость выхода всех курьеров
    fixed_costs = 0
    for agent_id, plans in solution.routes.items():
        sum_dist = 0
        sum_time = 0
        for j, plan in enumerate(plans):
            if len(plan.waypoints) > 2:
                if plan == plans[0]:
                    fixed_costs += plan.agent.costs["fixed"]
                else:
                    sum_dist += solution.problem.depots_mapping.dist(
                        plans[j - 1].waypoints[0], plans[j - 1].waypoints[0], plan.agent.profile
                    )
                    sum_time += solution.problem.depots_mapping.time(
                        plans[j - 1].waypoints[0], plans[j - 1].waypoints[0], plan.agent.profile
                    )
                # собираем все посещенные депо данным курьером
                stops = []
                # проходим по каждой доставке
                for i, visit in enumerate(plan.waypoints):
                    # собираем посещения
                    if i == 0:
                        activity = "departure"
                    elif i == (len(plan.waypoints) - 1):
                        activity = "arrival"
                    else:
                        activity = "delivery"
                    stop = {
                        "activity": activity,
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
                        "distance": plan.info["distance"],
                        "duration": plan.info["duration"],
                    },
                    "stops": stops,
                }
                global_stat = update_statistic(global_stat, plan.info)
                dep_name = plan.waypoints[0].place.name
                tours.append((dep_name, tour))
        global_stat["distance"] += sum_dist
        global_stat["duration"] += sum_time
        global_stat["times"]["driving"] += sum_time
        global_stat["cost"] += sum_dist * plan.agent.costs["distance"] + sum_time * plan.agent.costs["time"]

    # добавляем посчитанные стоимости выходов всех курьеров
    global_stat["cost"] += fixed_costs
    res = {
        "status": "solved",
        "progress_status": "solved",
        "solved": {dep_name: tour for dep_name, tour in tours},
        "unassigned": [],
        "info": {},
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
