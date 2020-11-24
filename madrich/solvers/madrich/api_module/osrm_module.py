from itertools import chain
from typing import List, Union, Tuple
from urllib.parse import quote

import numpy as np
import requests
import ujson
from polyline import encode as polyline_encode

from madrich import settings

array = np.ndarray
Point = Tuple[float, float]


def to_array(points: List[Point]) -> array:
    return np.array(points, dtype=('f8', 'f8'))


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


def get_matrix(points: Union[array, list], factor: Union[str, list], transport: str, dst=None, profile="driving"):
    """ Возвращает ассиметричные матрицы смежности
    :param points: points
    :param factor: duration; distance annotation for osrm
    :param transport: transport
    :param dst:
    :param profile: default 'driving'
    :return: one matrix in case key=str and list of matrix when key=list
    """

    host = dict(  # выбираем сервер, к которому обращаемся
        car=f'http://{settings.OSRM_CAR_HOST}:{settings.OSRM_CAR_PORT}',
        foot=f'http://{settings.OSRM_FOOT_HOST}:{settings.OSRM_FOOT_PORT}',
        bicycle=f'http://{settings.OSRM_BICYCLE_HOST}:{settings.OSRM_BICYCLE_PORT}',
    )[transport]

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
