"""Тут находятся разные генераторы гео-данных."""
import random
from functools import partial
from typing import Tuple, Callable

import chaospy
import numpy as np
from pyDOE import lhs
from scipy.optimize._shgo_lib.sobol_seq import Sobol

from geo.operations.filtering import square_bounds, check_circle, named_points, radial_bounds
from utils.types import Array


def transform_to_bounds(
    points: Array,
    bounds: Tuple[Tuple[float, float], Tuple[float, float]],
):
    """Растягиваем точки докуда нужно """
    points[:, 0] -= points[:, 0].min()
    points[:, 0] /= points[:, 0].max()
    points[:, 1] -= points[:, 1].min()
    points[:, 1] /= points[:, 1].max()

    points[:, 0] = points[:, 0] * (bounds[0][1] - bounds[0][0]) + bounds[0][0]
    points[:, 1] = points[:, 1] * (bounds[1][1] - bounds[1][0]) + bounds[1][0]
    return points


def random_points(
    num: int = 100,
    random_state: int = 42,
):
    """Случайные равномерные точки в квадрате. """
    np.random.seed(random_state)
    return np.random.rand(num, 2)


def sobol_points(
    num: int = 100,
):
    """Последовательность Cоболя.

    >>> generate_points(  # сгенерируем точки соболя
    ... generator=sobol_points,
    ... bounds=square_bounds['область'],
    ... checker=partial(check_circle, center=named_points['moscow_center'], radius=radial_bounds['бетонка']),
    ... num=4)
    array([[55.74651   , 37.60516   ],
           [55.86271133, 37.434872  ],
           [55.63030867, 37.775448  ],
           [55.68840933, 37.520016  ]])
    """
    return Sobol().i4_sobol_generate(2, num)


def latin_hypercube(
    num: int = 100,
    seed: int = 42,
):
    """Латинский гиперкуб.

    >>> generate_points(  # сгенерируем точки из гиперкуба
    ... generator=latin_hypercube,
    ... bounds=square_bounds['область'],
    ... checker=partial(check_circle, center=named_points['moscow_center'], radius=radial_bounds['бетонка']),
    ... num=4)
    array([[55.920812  , 37.67939721],
           [55.67315745, 37.65807234],
           [55.61657627, 37.75133012],
           [55.84848512, 37.860592  ]])
    """
    np.random.seed(seed)
    return lhs(2, num, criterion='maximin')


def halton(
    num: int = 100,
):
    """Последовательность Хальтона.

    >>> generate_points(  # сгенерируем точки хальтона
    ... generator=halton,
    ... bounds=square_bounds['область'],
    ... checker=partial(check_circle, center=named_points['moscow_center'], radius=radial_bounds['бетонка']),
    ... num=4)
    array([[55.59857301, 37.70817954],
           [55.70403304, 37.860592  ],
           [55.572208  , 37.67007642],
           [55.67766803, 37.82248888]])

    """
    distribution = chaospy.J(chaospy.Uniform(), chaospy.Uniform())
    return distribution.sample(num, rule="halton").reshape(num, 2)


def grid(
    num: int = 100,
):
    """Точки на сетке."""
    raise NotImplementedError()
    # distribution = chaospy.J(chaospy.Uniform(), chaospy.Uniform())
    # return distribution.sample(num, rule="grid")


def generate_points(
    generator: Callable[[int], Array],
    bounds: Tuple[Tuple[float, float], Tuple[float, float]],
    checker: Callable[[float, float], bool],
    num: int = 100,
) -> np.ndarray:
    """Получаем множество точек.

    >>> generate_points(  # сгенерируем рандомные точки
    ... generator=random_points,
    ... bounds=square_bounds['область'],
    ... checker=partial(check_circle, center=named_points['moscow_center'], radius=radial_bounds['бетонка']),
    ... num=4)
    array([[55.72419311, 37.84854368],
           [55.8776803 , 37.6275715 ],
           [55.63036211, 37.349728  ],
           [55.58830976, 37.79548226]])

    Parameters
    ----------
    generator : Функция, которая генерирует точки с равномерным распределением в [0, 1]^2
    bounds : Границы квадрата, на кторые точки масштабируются
    checker : Функция для проверки, что точки принадлежать требуемой области
    num : Требуемое количество точек

    Returns
    -------
    Массим сгенерированных точек
    """
    points = generator(num * 2)  # генерируем
    points = transform_to_bounds(points, bounds)  # трансформим
    return np.array([p for p in points if checker(p[0], p[1])])[:num]  # фильтруем
