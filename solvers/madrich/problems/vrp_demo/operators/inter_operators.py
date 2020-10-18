import logging
from copy import deepcopy
from typing import Tuple

from madrich.problems.models import State
from madrich.problems.utils import cross, replace
from madrich.problems.vrp_demo.models import Problem, Route


def inter_swap(route1: Route, route2: Route, problem: Problem) -> bool:
    logging.info(f'\nSwap started, tt:{route1.travel_time + route2.travel_time}')
    ret = __inter_opt(__inter_swap, route1, route2, problem)
    logging.info(f'Ended, tt:{route1.travel_time + route2.travel_time}')
    return ret


def inter_replace(route1: Route, route2: Route, problem: Problem) -> bool:
    logging.info(f'\nReplace started, tt:{route1.travel_time + route2.travel_time}')
    return __symmetric_function(__inter_replace, route1, route2, problem)


def inter_cross(route1: Route, route2: Route, problem: Problem) -> bool:
    logging.info(f'\nCross started, tt:{route1.travel_time + route2.travel_time}')
    return __symmetric_function(__inter_cross, route1, route2, problem)


def __inter_swap(best_state: State, route1: Route, route2: Route, problem: Problem) -> Tuple[bool, State, Route, Route]:
    size1, size2 = len(route1.jobs), len(route2.jobs)
    best_route1, best_route2 = route1, route2
    changed = False

    for it1 in range(size1):
        for it2 in range(size2):
            jobs1, jobs2 = deepcopy(route1.jobs), deepcopy(route2.jobs)
            jobs1[it1], jobs2[it2] = jobs2[it2], jobs1[it1]
            new_route1, new_route2 = route1.new_route(jobs1), route2.new_route(jobs2)
            new_state1, new_state2 = problem.get_state(new_route1), problem.get_state(new_route2)
            if new_state1 is None or new_state2 is None:
                continue
            new_state = new_state1 + new_state2

            if new_state < best_state:
                changed = True
                best_state = new_state
                best_route1, best_route2 = new_route1, new_route2

    return changed, best_state, best_route1, best_route2


def __symmetric_function(func, route1: Route, route2: Route, problem: Problem) -> bool:
    tmp_route1 = route1.new_route(deepcopy(route1.jobs))
    tmp_route2 = route2.new_route(deepcopy(route2.jobs))
    changed = True

    while changed:
        changed = __inter_opt(func, tmp_route1, tmp_route2, problem)
        if changed:
            continue
        changed = __inter_opt(func, tmp_route2, tmp_route1, problem)

    state = problem.get_state(route1) + problem.get_state(route2)
    tmp_state = problem.get_state(tmp_route1) + problem.get_state(tmp_route2)

    logging.info(f'Ended, tt:{tmp_state.travel_time}')
    if tmp_state < state:
        route1.jobs = tmp_route1.jobs
        route2.jobs = tmp_route2.jobs
        return True
    return False


def __inter_opt(func, route1: Route, route2: Route, problem: Problem) -> bool:
    tmp_route1 = route1.new_route(deepcopy(route1.jobs))
    tmp_route2 = route2.new_route(deepcopy(route2.jobs))
    state = tmp_state = problem.get_state(tmp_route1) + problem.get_state(tmp_route2)
    changed = True

    while changed:
        changed, best_state, best_route1, best_route2 = func(tmp_state, tmp_route1, tmp_route2, problem)
        if changed:
            tmp_state = best_state
            tmp_route1, tmp_route2 = best_route1, best_route2
            logging.info(f'Updated, tt:{best_state.travel_time}, cost:{best_state.cost}')

    if tmp_state < state:
        route1.jobs = tmp_route1.jobs
        route2.jobs = tmp_route2.jobs
        problem.get_state(route1)
        problem.get_state(route2)
        return True
    return False


def __inter_cross(best_state: State, route1: Route, route2: Route,
                  problem: Problem) -> Tuple[bool, State, Route, Route]:
    size1, size2 = len(route1.jobs), len(route2.jobs)
    best_route1, best_route2 = route1, route2

    for it1 in range(size1):
        for it2 in range(it1, size1):
            for it3 in range(size2):
                for it4 in range(it3, size2):
                    jobs1, jobs2 = cross(route1.jobs, route2.jobs, it1, it2, it3, it4)
                    new_route1, new_route2 = route1.new_route(jobs1), route2.new_route(jobs2)
                    new_state1, new_state2 = problem.get_state(new_route1), problem.get_state(new_route2)
                    if new_state1 is None or new_state2 is None:
                        continue
                    new_state = new_state1 + new_state2

                    if new_state < best_state:
                        best_state = new_state
                        best_route1, best_route2 = new_route1, new_route2
                        return True, best_state, best_route1, best_route2

    return False, best_state, best_route1, best_route2


def __inter_replace(best_state: State, route1: Route, route2: Route,
                    problem: Problem) -> Tuple[bool, State, Route, Route]:
    size1, size2 = len(route1.jobs), len(route2.jobs)
    best_route1, best_route2 = route1, route2
    changed = False

    for it1 in range(size1):
        for it2 in range(size2):
            jobs1, jobs2 = replace(route1.jobs, route2.jobs, it1, it2)
            new_route1, new_route2 = route1.new_route(jobs1), route2.new_route(jobs2)
            new_state1, new_state2 = problem.get_state(new_route1), problem.get_state(new_route2)
            if new_state1 is None or new_state2 is None:
                continue
            new_state = new_state1 + new_state2

            if new_state < best_state:
                changed = True
                best_state = new_state
                best_route1, best_route2 = new_route1, new_route2

    return changed, best_state, best_route1, best_route2
