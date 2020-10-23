import logging
from typing import Callable

from solvers.madrich.problems.mdvrp_demo.models import Route, Problem
from solvers.madrich.problems.utils import three_opt_exchange, swap

OptFunc = Callable[[int, Route, Problem], bool]


def three_opt(route: Route, problem: Problem) -> bool:
    """ Выполняем 3-opt по маршруту
    :param route: маршрут
    :param problem: проблема
    :return: улучился или нет
    """
    logging.info(f'\nThree opt started, {route.state}')
    result = __opt(__three_opt, route, problem)
    logging.info(f'Ended, {route.state}')
    return result


def two_opt(route: Route, problem: Problem) -> bool:
    """ Выполняем 2-opt по маршруту
    :param route: маршрут
    :param problem: проблема
    :return: улучился или нет
    """
    logging.info(f'\nTwo opt started, {route.state}')
    result = __opt(__two_opt, route, problem)
    logging.info(f'Ended, {route.state}')
    return result


def __opt(func: OptFunc, route: Route, problem: Problem) -> bool:
    changed, result = True, False
    size = len(route.tracks)

    while changed:
        changed = False
        for i in range(size):
            status = func(i, route, problem)
            if status:
                changed = result = status

    return result


def __three_opt(track_id: int, route: Route, problem: Problem) -> bool:
    """ На основе текущего подмаршрута пытается сделать 3-opt и создать новый
    :param track_id: подмаршрут
    :param route: маршрут
    :param problem: проблема
    :return: улучшился или нет
    """
    track = route.tracks[track_id]
    tmp_jobs = track.jobs
    tmp_state = route.state
    size = len(track.jobs)
    changed = True

    while changed:
        changed = False
        best_state, best_jobs = tmp_state, tmp_jobs

        for it1 in range(size):
            for it3 in range(it1 + 1, size):
                for it5 in range(it3 + 1, size):
                    for i in range(4):
                        # 1. Пробуем поменять, без 2-opt вариантов
                        new_jobs = three_opt_exchange(tmp_jobs, i, (it1, it3, it5))
                        track.jobs = new_jobs
                        # 2. Тогда оценим весь тур
                        new_state = problem.get_state(route)
                        if new_state is None:
                            continue
                        if new_state < best_state:
                            changed = True
                            best_state, best_jobs = new_state, new_jobs

        if changed:
            tmp_state, tmp_jobs = best_state, best_jobs
            logging.info(f'Updated, {best_state}')

    route.tracks[track_id].jobs = tmp_jobs
    if tmp_state < route.state:
        route.state = tmp_state
        return True
    return False


def __two_opt(track_id: int, route: Route, problem: Problem) -> bool:
    """ На основе текущего подмаршрута пытается сделать 2-opt и создать новый
    :param track_id: подмаршрут
    :param route: маршрут
    :param problem: проблема
    :return: улучшился или нет
    """
    track = route.tracks[track_id]
    tmp_jobs = track.jobs
    tmp_state = route.state
    size = len(track.jobs)
    changed = True

    while changed:
        changed = False
        best_state, best_jobs = tmp_state, tmp_jobs

        for it1 in range(size):
            for it3 in range(it1 + 1, size):
                # 1. Пробуем поменять
                new_jobs = swap(tmp_jobs, it1, it3)
                track.jobs = new_jobs
                # 2. Тогда оценим весь тур
                new_state = problem.get_state(route)
                if new_state is None:
                    continue
                if new_state < best_state:
                    changed = True
                    best_state, best_jobs = new_state, new_jobs

        if changed:
            tmp_state, tmp_jobs = best_state, best_jobs
            logging.info(f'Updated, {best_state}')

    route.tracks[track_id].jobs = tmp_jobs
    if tmp_state < route.state:
        route.state = tmp_state
        return True
    return False
