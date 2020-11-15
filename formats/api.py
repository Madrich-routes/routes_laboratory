from datetime import datetime

import ujson

from models.rich_vrp import VRPSolution


def export(solution: VRPSolution) -> str:
    """
     Конвертируем VRPSolution для нашего API.

    Parameters
    ----------
    solution: VRPSolution,

    Returns
    -------
    """
    sum_statistic = {"cost": 0, "distance": 0, "duration": 0}
    tours = []
    # проходим по каждому туру
    for plan in solution.routes:
        if len(plan.waypoints > 2):
            statistic = {"cost": 0, "distance": 0, "duration": 0}
            visits = []

            # проходим по каждой доставке
            for i, visit in enumerate(plan.waypoints):
                distance = 0 if i == 0 else solution.problem.matrix[
                    plan.waypoints[i - 1].place.id, visit.place.id]  # !!!не уверен что так, но других вариантов не вижу
                # собираем посещения
                stop = {
                    "activity": "departure",  # !!!Как определить?
                    "distance": distance,
                    "load": [0, 0],  # !!!Брать неоткуда
                    "job_id": visit.place.id,
                    "location": {"lat": visit.place.lat, "lan": visit.place.lon},
                    "time": {
                        "arrival": datetime.fromtimestamp(visit.time).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "departure": datetime.fromtimestamp(visit.time + visit.place.delay).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")
                    }
                }
                visits.append(stop)
            # определяем общую длительность маршрута
            first_point = plan.waypoints[0]
            last_point = plan.waypoints[-1]
            last_duration = last_point.delay if hasattr(last_point, 'delay') else 0
            statistic["duration"] = last_point.time - first_point.time + last_duration

            # !!!Не уверен что так, но другого решения не вижу
            statistic["cost"] = plan.agent.costs.departure + plan.agent.costs.time * statistic[
                "duration"] + plan.agent.costs.dist * statistic["distance"]
            tour = {
                "type": plan.agent.type,
                "courier_id": plan.agent.id,
                "statistic": statistic,
                "stops": visits
            }
            tours.append(tour)
            sum_statistic["cost"] += statistic["cost"]
            sum_statistic["duration"] += statistic["duration"]
            sum_statistic["distance"] += statistic["distance"]

    # собираем результат
    res = {
        "status": "solved",
        "progress_status": "solved",
        "solved": {
            "depot_name": tours
        },
        "unassigned": [{
            "job_id": "job_0",  # !!! откуда брать?
            "reason": "because"
        }],
        "info": {
            "strategy_used": "genetic",
            "time_received": "2020-10-01T10:00:00Z",
            "time_computed": "2020-10-01T10:05:00Z"
        },
        "statistics": {
            "cost": sum_statistic["cost"],
            "distance": sum_statistic["distance"],
            "duration": sum_statistic["duration"],
            "full_tours": len(tours),
            "times": {  # !!! в текущей конфигурации входных данных не вижу возможности посчитать
                "driving": 22558,
                "serving": 5400,
                "waiting": 9036,
                "break": 0
            }
        }
    }

    return ujson.dumps(res)
