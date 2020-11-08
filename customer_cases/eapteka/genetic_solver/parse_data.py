import logging
import math
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import ujson
from transliterate import translit

from customer_cases.eapteka.genetic_solver.models import Courier, Depot, Task
from customer_cases.eapteka.genetic_solver.utils import check_point, make_windows, make_windows_orders
from geo.providers import osrm_module

Point = Tuple[float, float]


def reindexing(depot: Depot, depot_id: str, global_revers: dict, tasks: Dict[str, List[Task]],
               address_mapping: Dict[Point, Tuple[str, str, str]]) -> Dict[Point, int]:
    """Reindexing for tasks location."""

    internal_mapping, index = {}, 0
    if len(tasks[depot_id]) > 10:
        tmp_loc = depot_loc = global_revers[depot.location]
        depot_loc, index = __add_point(internal_mapping, index, depot_loc[0], depot_loc[1])
        depot.location = depot_loc

        min_priority = min(task.priority for task in tasks[depot_id])
        for task in tasks[depot_id]:
            task_loc = global_revers[task.location]
            task_loc, index = __add_point(internal_mapping, index, task_loc[0], task_loc[1])
            task.location = task_loc
            task.priority = task.priority if min_priority == 1 else 1

        courier_loc = (round(tmp_loc[0] + 5e-4, 6), round(tmp_loc[1], 6))
        address_mapping[courier_loc] = ('depot', 'depot', 'depot')
        __add_point(internal_mapping, index, courier_loc[0], courier_loc[1])

    return internal_mapping


def download_transport_simple(file, points: list):
    def return_checked(t, d: int):
        if t != 0 and 5 < d / t < 13:
            if t > 2 * 60 * 60:
                return d / 12, d
            elif d > 100 * 1000:
                return t, t * 12
            else:
                return d / 12, d
        return t, d

    p_dist, p_time = osrm_module.get_osrm_matrix(points, transport='foot')
    c_dist, c_time = osrm_module.get_osrm_matrix(points, transport='car')

    res_time = np.zeros(p_dist.shape)
    res_dist = np.zeros(p_dist.shape)

    res_time[p_time <= 15 * 60] = p_time[p_time <= res_time['time']]
    res_time[15 * 60 < p_time < 45 * 60] = p_time[15 * 60 < p_time < 45 * 60]

    travel_times, distances = [], []
    for i in range(len(points)):
        for j in range(len(points)):
            pt = p_dist[i][j]
            dtt, dd = return_checked(p_time[i][j], p_time[i][j])

            if pt <= 15 * 60:
                travel_times.append(int(pt))
                distances.append(int(pt))
            elif 15 * 60 < pt < 45 * 60:
                tt = int(min(dtt * 1.5, pt))
                travel_times.append(tt)
                distances.append(int(dd))
            else:
                tt = int(min(dtt * 2, pt))
                travel_times.append(tt)
                distances.append(int(dd))

    routing = {'profile': 'transport_simple', 'travelTimes': travel_times, 'distances': distances}

    with open(file, 'w') as f:
        ujson.dump(routing, f)
