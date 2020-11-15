import numpy as np

from geo.transport.calc_distance import combined_matrix, transport_travel_time
from utils.types import Array


def get_example1_data():
    res = {
        "p_matrix": np.array(
            [
                [0, 20],
                [30, 0],
            ]
        ),
        "s_matrix": np.array(
            [
                [0, 8, 7],
                [6, 0, 4],
                [3, 2, 0],
            ]
        ),
        "p2s_matrix": np.array([[1, 2, 3], [4, 5, 6]]),
        "s2p_matrix": np.array([[1, 2], [3, 4], [5, 6]]),
    }

    return res


def check_transport_travel_time(
    src: int,
    dst: int,  # откуда куда
    p_matrix: Array,  # время пешком между точками
    p2s_matrix: Array,  # время пешком от точек до остановок
    s2p_matrix: Array,  # время пешком от остановок до точек
    s_matrix: Array,  # время проезда между точками
    src_closest: Array,  # индексы ближайших к старту остановок
    dst_closest: Array,  # индексы ближайших к концу остановок
):
    time, src_station, dst_station = transport_travel_time(
        src=src,
        dst=dst,
        p_matrix=p_matrix,
        p2s_matrix=p2s_matrix,
        s2p_matrix=s2p_matrix,
        s_matrix=s_matrix,
        src_closest=src_closest,
        dst_closest=dst_closest,
    )

    assert isinstance(time, int), "Время должно быть интом"
    assert time <= p_matrix[src, dst], "Пешком не хуже"

    if time == p_matrix[src, dst]:
        assert (
            src_station is None and dst_station is not None
        ), "Если пешком, то станций нет"
    else:
        assert (
            time
            == s_matrix[src_station, dst_station]
            + s2p_matrix[src, src_station]
            + p2s_matrix[dst_station, dst]
        ), "Неправильное время в пути при проезде"


def test_transport_travel_time():
    """Тестируем, что функция расчета расстояний ведет себя адекватно."""
    data = get_example1_data()

    res = transport_travel_time(
        src=0,
        dst=1,
        p_matrix=data["p_matrix"],
        p2s_matrix=data["p2s_matrix"],
        s2p_matrix=data["s2p_matrix"],
        s_matrix=data["s_matrix"],
        src_closest=np.array([0, 1, 2]),
        dst_closest=np.array([0, 1]),
    )

    assert res == (3, 0, 0)


def test_combined_matrix():
    """Тестируем матрицу с транспортом."""
    data = get_example1_data()

    res = combined_matrix(
        p_matrix=data["p_matrix"],
        p2s_matrix=data["p2s_matrix"],
        s2p_matrix=data["s2p_matrix"],
        s_matrix=data["s_matrix"],
        candidates=2,
    )

    assert np.array_equal(res, np.array([[0, 3], [5, 0]]))
