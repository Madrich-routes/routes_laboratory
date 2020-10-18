from itertools import chain
from typing import List, Union, Tuple
from urllib.parse import quote

import numpy as np
import requests
import ujson
from polyline import encode as polyline_encode

from madrich.utils import to_array

array = np.ndarray
Point = Tuple[float, float]

osrm_host = 'http://osrm-car.dimitrius.keenetic.link'

coefficient = {'speed_car': 7.5, 'speed_pedestrian': 1, 'distance_car': 1.06, 'distance_pedestrian': 0.8}


def _encode_src_dst(src, dst):
    coords = tuple((c[1], c[0]) for c in chain(src, dst))
    polyline = polyline_encode(coords)
    ls, ld = map(len, (src, dst))
    params = dict(
        sources=";".join(map(str, range(ls))),
        dests=";".join(map(str, range(ls, ls + ld))),
        annotations=True, )
    return quote(polyline), params


def _encode_src(src):
    coords = tuple((c[1], c[0]) for c in src)
    polyline = polyline_encode(coords)
    params = dict(annotations="duration")
    return quote(polyline), params


def _turn_over(points):
    pts = points.copy()
    for i in range(len(pts)):
        pts[i][0], pts[i][1] = points[i][1], points[i][0]
    return pts


def get_matrix(points: Union[array, List[Point]], factor: Union[str, List[str]], host=osrm_host, dst=None,
               profile="driving") -> Union[array, List[array]]:
    """ Возвращает ассиметричные матрицы смежности
    :param points: points
    :param factor: duration; distance annotation for osrm
    :param host: osrm host
    :param dst:
    :param profile: default 'driving'
    :return: one matrix in case key=str and list of matrix when key=list
    """
    points = points if type(points) == array else to_array(points)
    points = _turn_over(points)
    if dst is not None:
        polyline, _ = _encode_src_dst(points, dst)
    else:
        polyline, _ = _encode_src(points)

    annotation = ','.join(factor) if type(factor) is list else factor
    r = requests.get(f"{host}/table/v1/{profile}/polyline({polyline})?annotations={annotation}")
    assert r.status_code == 200, f'osrm bad request: {r.reason}'
    parsed_json = ujson.loads(r.content)

    if type(factor) is str:
        output = np.array(parsed_json[f'{factor}s'])
        assert output.sum() != 0, 'координаты переверни, да?'
        return output
    else:
        output = [np.array(parsed_json[f'{fact}s']) for fact in factor]
        assert any([m.sum() == 0 for m in output]), 'координаты переверни, да?'
        return output


def get_matrices(points: Union[array, List[Point]], factor: Union[str, List[str]], max_cost: int, split=15,
                 host=osrm_host, dst=None, profile="driving") -> Union[array, List[array]]:
    """ Возвращает нужное кол-во матриц смежностей
    :param points: points
    :param factor: duration, distance
    :param max_cost: сколько времени со старта пройдет
    :param split: минуты
    :param host: osrm host
    :param dst:
    :param profile: default 'driving'
    :return: one matrix of matrix in case key=str and list when key=list
    """
    split *= 60
    size = len(points)
    length = int(np.ceil(max_cost / split))

    result = get_matrix(points, factor, host, dst, profile)
    if type(result) is list:
        output = []
        for res in result:
            matrices = np.zeros(shape=(length, size, size), dtype=np.int64)
            for i in range(length):
                matrices[i] = res.copy()
            output.append(matrices)
    else:
        output = np.zeros(shape=(length, size, size), dtype=np.int64)
        for i in range(length):
            output[i] = result

    return output
