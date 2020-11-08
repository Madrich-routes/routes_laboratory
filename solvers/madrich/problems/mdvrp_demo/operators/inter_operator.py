import logging
from typing import Callable, List, Tuple

from solvers.madrich.problems.mdvrp_demo.models import Job, Problem, Route
from solvers.madrich.problems.mdvrp_demo.operators.utils import check_values
from solvers.madrich.problems.models import State
from solvers.madrich.problems.utils import cross, replace

OptFunc = Callable[[State, int, int, Route, Route, Problem], Tuple[bool, State, List[Job], List[Job]]]


def inter_replace(track_id1: int, track_id2: int, route1: Route, route2: Route, problem: Problem) -> bool:
    """Перемещает точку из одного тура в другой.

    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур, состояние, новый список, новый список
    """
    logging.info(f'\nReplace started, {route1.get_state() + route2.get_state()}')
    result = __symmetric_call(__inter_replace, track_id1, track_id2, route1, route2, problem)
    logging.info(f'Ended, {route1.get_state() + route2.get_state()}')
    return result


def inter_cross(track_id1: int, track_id2: int, route1: Route, route2: Route, problem: Problem) -> bool:
    """ Cross оператор - подходит для постоптимизации
    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур, состояние, новый список, новый список
    """
    logging.info(f'\nCross started, {route1.get_state() + route2.get_state()}')
    result = __inter_opt(__inter_cross, track_id1, track_id2, route1, route2, problem)
    logging.info(f'Ended, {route1.get_state() + route2.get_state()}')
    return result


def inter_swap(track_id1: int, track_id2: int, route1: Route, route2: Route, problem: Problem) -> bool:
    """Меняет две точки местами.

    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур
    """
    logging.info(f'\nSwap started, {route1.get_state() + route2.get_state()}')
    track1, track2 = route1.tracks[track_id1], route2.tracks[track_id2]
    assert track1.storage.name == track2.storage.name, 'different storage for tracks'
    jobs1, jobs2 = track1.jobs, track2.jobs
    size1, size2 = len(jobs1), len(jobs2)
    state = route1.get_state() + route2.get_state()
    result, changed = False, True

    while changed:
        changed = False
        best_state, best_swap = state, (-1, -1)

        for it1 in range(size1):
            for it2 in range(size2):
                jobs1[it1], jobs2[it2] = jobs2[it2], jobs1[it1]
                new_state1, new_state2 = problem.get_state(route1), problem.get_state(route2)
                if new_state1 is None or new_state2 is None:
                    jobs1[it1], jobs2[it2] = jobs2[it2], jobs1[it1]
                    continue
                new_state = new_state1 + new_state2
                if new_state < best_state:
                    result = changed = True
                    best_state, best_swap = new_state, (it1, it2)
                jobs1[it1], jobs2[it2] = jobs2[it2], jobs1[it1]

        if changed:
            state = best_state
            it1, it2 = best_swap
            jobs1[it1], jobs2[it2] = jobs2[it2], jobs1[it1]
            logging.info(f'Updated, {best_state}')

    if result:
        route1.state = problem.get_state(route1)
        route2.state = problem.get_state(route2)
    logging.info(f'Ended, {route1.get_state() + route2.get_state()}')
    return result


def __symmetric_call(func: OptFunc, track_id1: int, track_id2: int, route1: Route, route2: Route, problem: Problem):
    """Применяет оптимизацию к обоим подмаршрутам.

    :param func: функция, которая ищет улучшение не туре
    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур
    """
    result, changed = False, True

    while changed:
        changed1 = __inter_opt(func, track_id1, track_id2, route1, route2, problem)
        changed2 = __inter_opt(func, track_id1, track_id2, route1, route2, problem)
        changed = changed1 or changed2
        if changed:
            result = changed

    return result


def __inter_opt(func: OptFunc, track_id1: int, track_id2: int, route1: Route, route2: Route, problem: Problem) -> bool:
    """Общий интерфейс к функции, которая внутри себя вызывает некоторую оптимизацию.

    :param func: функция, которая ищет улучшение не туре
    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур
    """
    track1, track2 = route1.tracks[track_id1], route2.tracks[track_id2]
    assert track1.storage.name == track2.storage.name, 'different storage for tracks'
    state = route1.get_state() + route2.get_state()
    result, changed = False, True

    while changed:
        changed, best_state, best_jobs1, best_jobs2 = func(state, track_id1, track_id2, route1, route2, problem)
        if changed:
            state, result = best_state, True
            track1.jobs, track2.jobs = best_jobs1, best_jobs2
            logging.info(f'Updated, {best_state}')

    if result:
        route1.state = problem.get_state(route1)
        route2.state = problem.get_state(route2)
    return result


def __inter_replace(best_state: State, track_id1: int, track_id2: int, route1: Route, route2: Route,
                    problem: Problem) -> Tuple[bool, State, List[Job], List[Job]]:
    """Перемещает точку из одного тура в другой.

    :param best_state: лучший на данный момент
    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур, состояние, новый список, новый список
    """
    track1, track2 = route1.tracks[track_id1], route2.tracks[track_id2]
    jobs1, jobs2 = track1.jobs, track2.jobs
    size1, size2 = len(jobs1), len(jobs2)
    best_jobs1, best_jobs2 = track1.jobs, track2.jobs
    track_value = problem.get_state_track(track1, route1).value
    courier_value = route1.courier.value
    changed = False

    for it1 in range(size1):
        for it2 in range(size2):
            if not check_values(courier_value, track_value + jobs2[it2].value):
                continue
            new_jobs1, new_jobs2 = replace(jobs1, jobs2, it1, it2)
            track1.jobs, track2.jobs = new_jobs1, new_jobs2
            new_state1, new_state2 = problem.get_state(route1), problem.get_state(route2)
            if new_state1 is None or new_state2 is None:
                track1.jobs, track2.jobs = jobs1, jobs2
                continue
            new_state = new_state1 + new_state2
            if new_state < best_state:
                changed = True
                best_state = new_state
                best_jobs1, best_jobs2 = new_jobs1, new_jobs2
            track1.jobs, track2.jobs = jobs1, jobs2

    return changed, best_state, best_jobs1, best_jobs2


def __inter_cross(best_state: State, track_id1: int, track_id2: int, route1: Route, route2: Route,
                  problem: Problem) -> Tuple[bool, State, List[Job], List[Job]]:
    """ Cross оператор - подходит для постоптимизации
    :param best_state: лучший на данный момент
    :param track_id1: номер первого подмаршрута
    :param track_id2: номер второго подмаршрута
    :param route1: маршрут
    :param route2: маршрут
    :param problem:
    :return: изменился ли тур, состояние, новый список, новый список
    """
    track1, track2 = route1.tracks[track_id1], route2.tracks[track_id2]
    jobs1, jobs2 = track1.jobs, track2.jobs
    size1, size2 = len(jobs1), len(jobs2)

    for it1 in range(size1):
        for it2 in range(it1, size1):
            for it3 in range(size2):
                for it4 in range(it3, size2):
                    new_jobs1, new_jobs2 = cross(jobs1, jobs2, it1, it2, it3, it4)
                    track1.jobs, track2.jobs = new_jobs1, new_jobs2
                    new_state1, new_state2 = problem.get_state(route1), problem.get_state(route2)
                    if new_state1 is None or new_state2 is None:
                        track1.jobs, track2.jobs = jobs1, jobs2
                        continue
                    new_state = new_state1 + new_state2
                    if new_state < best_state:
                        return True, new_state, new_jobs1, new_jobs2
                    track1.jobs, track2.jobs = jobs1, jobs2

    return False, best_state, jobs1, jobs2
