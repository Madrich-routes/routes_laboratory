from datetime import datetime
from typing import Dict

import ujson

from madrich.models.rich_vrp.job import Job
from madrich.models.rich_vrp.solution import MDVRPSolution


def export(solution: MDVRPSolution) -> str:
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

    return ujson.dumps(res)


def update_statistic(global_stat: Dict[str, float], local_stat: Dict[str, float]) -> Dict[str, float]:
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
