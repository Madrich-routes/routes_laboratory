from datetime import datetime

import ujson

from madrich.models.rich_vrp import VRPSolution
from madrich.models.rich_vrp import PlanReport


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
        if len(plan.waypoints) > 2:
            visits = []
            sum_dist = 0
            # проходим по каждой доставке
            geometry = plan.agent.type.name
            for i, visit in enumerate(plan.waypoints):
                distance = (
                    0
                    if i == 0
                    else solution.problem.matrix.geometries[geometry].dist_matrix[
                        plan.waypoints[i - 1].place.id, visit.place.id
                    ]
                )  # !!!не уверен что так, но других вариантов не вижу
                distance = 0 if distance is None else distance
                sum_dist += distance
                # собираем посещения
                stop = {
                    "activity": "departure",
                    "distance": distance,
                    "load": visit.place.amounts
                    if type(visit.place) == "Job"
                    else [0, 0],
                    "job_id": visit.place.id,
                    "location": {"lat": visit.place.lat, "lan": visit.place.lon},
                    "time": {
                        "arrival": datetime.fromtimestamp(visit.time).strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        ),
                        "departure": datetime.fromtimestamp(
                            visit.time + visit.place.delay
                        ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                }
                visits.append(stop)
            report = PlanReport(plan, solution.problem)
            tour = {
                "type": plan.agent.type,
                "courier_id": plan.agent.id,
                "statistic": {
                    "cost": 0,
                    "distance": sum_dist,
                    "duration": report.duration,
                },
                "stops": visits,
            }
            tours.append(tour)

    # собираем результат
    res = {
        "status": "solved",
        "progress_status": "solved",
        "solved": {"depot_name": tours},
        "unassigned": [{"job_id": "job_0", "reason": "because"}],  # !!! откуда брать?
        "info": {
            "strategy_used": "genetic",
            "time_received": "2020-10-01T10:00:00Z",
            "time_computed": "2020-10-01T10:05:00Z",
        },
        "statistics": solution.info,
    }

    return ujson.dumps(res)
