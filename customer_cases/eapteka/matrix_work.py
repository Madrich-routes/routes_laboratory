import pickle
from copy import deepcopy
from datetime import datetime
from itertools import product
from typing import List, Tuple

import numpy as np
import ujson
from herepy import RouteMode
from madrich.api_module import here_module
from madrich.utils import to_array

Point = Tuple[float, float]
HERE_KEY = ''


def assemble_matrix(subs: List[List[np.array]], small_size: int, full_size: int):
    """
    Собираем большую матрицу из набора маленьких
    """
    res = np.zeros((full_size, full_size), dtype=np.int32)

    for i, j in product(range(len(subs)), repeat=2):
        i_from = i * small_size
        i_to = min((i + 1) * small_size, full_size)
        j_from = j * small_size
        j_to = min((j + 1) * small_size, full_size)
        res[i_from:i_to, j_from:j_to] = subs[i][j]

    return res


def save_chunk(x, y, obj):
    with open(f'./tmp/chunk_{x}_{y}.pkl', 'wb') as f:
        pickle.dump(obj, f)


def load_matrix(small_size):
    super_cell = [[None] * small_size for _ in range(small_size)]
    p_dist, p_time = deepcopy(super_cell), deepcopy(super_cell)
    d_dist, d_time = deepcopy(super_cell), deepcopy(super_cell)

    for x in range(small_size):
        for y in range(small_size):
            with open(f'./tmp/chunk_{x}_{y}.pkl', 'rb') as f:
                p_distance, p_travel_time, d_distance, d_travel_time = pickle.load(f)
                p_dist[x][y] = p_distance
                p_time[x][y] = p_travel_time
                d_dist[x][y] = d_distance
                d_time[x][y] = d_travel_time

    return p_dist, p_time, d_dist, d_time


def convert_pedestrian_to_transport(depot_id, pts, driver_matrix, pedestrian_matrix):
    size = len(pts)
    driver_distance, driver_time = driver_matrix
    pedestrian_distance, pedestrian_time = pedestrian_matrix
    transport_distance = []
    transport_time = []

    for i in range(size):
        for j in range(size):
            pt = pedestrian_time[i][j]
            if pt <= 15 * 60:
                transport_time.append(int(pt))
                transport_distance.append(int(pedestrian_distance[i][j]))
            elif 15 * 60 < pt < 45 * 60:
                transport_time.append(int(min(driver_time[i][j] * 1.5, pt)))
                transport_distance.append(int(min(driver_distance[i][j], pedestrian_distance[i][j])))
            else:
                transport_time.append(int(driver_time[i][j] * 2))
                transport_distance.append(int(driver_distance[i][j]))

    routing = {'profile': 'transport_simple_2',
               'travelTimes': transport_time,
               'distances': transport_distance}

    file = f'./tmp/{depot_id}.transport_simple_2.routing_matrix.json'
    with open(file, 'w') as f:
        ujson.dump(routing, f)


def download_matrix(points: List[Point], time_window):
    p = [RouteMode.fastest, RouteMode.publicTransport, RouteMode.traffic_default]

    t = datetime.strptime(time_window, '%Y-%m-%dT%H:%M:%SZ').timestamp()
    pts = to_array(points)  # numpy <pair>

    cell_size = 300
    size = len(pts)
    small_size = int(np.ceil(size / cell_size))

    super_cell = [[None] * small_size for _ in range(small_size)]
    p_dist, p_time = deepcopy(super_cell), deepcopy(super_cell)

    for x in range(small_size):
        for y in range(small_size):
            print(x, y)
            x_from = x * cell_size
            x_to = min((x_from + cell_size), size)

            y_from = y * cell_size
            y_to = min((y_from + cell_size), size)

            src = pts[x_from: x_to]
            dst = pts[y_from: y_to]

            p_distance, p_travel_time = here_module.get_matrix_sd(src=src, dst=dst, modes=p,
                                                                  start_t=t, key=HERE_KEY,
                                                                  factor=['distance', 'travelTime'])

            save_chunk(x, y, (p_distance, p_travel_time))

            p_dist[x][y] = p_distance
            p_time[x][y] = p_travel_time

    p_distance = assemble_matrix(p_dist, cell_size, size)
    p_travel_time = assemble_matrix(p_time, cell_size, size)
    return p_distance, p_travel_time
