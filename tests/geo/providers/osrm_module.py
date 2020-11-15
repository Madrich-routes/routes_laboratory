"""Тесты для OSRM. """
from functools import partial

from geo.data_generation.points import random_points, generate_points
from geo.operations.filtering import square_bounds, check_circle, named_points, radial_bounds
from geo.providers.osrm_module import get_osrm_matrix


def test_osrm_square_matrix():
    """Проверяем, что OSRM не падает с ошибками. """
    points = generate_points(
        generator=random_points,
        bounds=square_bounds['область'],
        checker=partial(check_circle, center=named_points['moscow_center'], radius=radial_bounds['бетонка']),
        num=4,
    )

    # get_osrm_matrix(points)
    get_osrm_matrix(src=points, dst=points)
