import logging
from copy import deepcopy

from solvers.madrich.problems.utils import three_opt_exchange, swap
from solvers.madrich.problems.vrp_demo.models import Route, Problem


def three_opt(route: Route, problem: Problem) -> bool:
    tmp_route = route.new_route(deepcopy(route.jobs))
    state = tmp_state = problem.get_state(tmp_route)
    size = len(tmp_route.jobs)
    changed = True

    logging.info(f'\nThree opt started, tt:{state.travel_time}, cost:{state.cost}')

    while changed:
        changed = False
        best_state, best_route = tmp_state, tmp_route

        for it1 in range(size):
            for it3 in range(it1 + 1, size):
                for it5 in range(it3 + 1, size):
                    for i in range(7):
                        path = three_opt_exchange(tmp_route.jobs, i, (it1, it3, it5))
                        new_route = tmp_route.new_route(path)
                        new_state = problem.get_state(new_route)
                        if new_state is None:
                            continue

                        if new_state < best_state:
                            changed = True
                            best_state, best_route = new_state, new_route

        if changed:
            tmp_state, tmp_route = best_state, best_route
            logging.info(f'Updated, tt:{best_state.travel_time}, cost:{best_state.cost}')

    logging.info(f'Ended, tt:{tmp_state.travel_time}, cost:{tmp_state.cost}')
    if tmp_state < state:
        route.jobs = tmp_route.jobs
        return True
    return False


def two_opt(route: Route, problem: Problem) -> bool:
    tmp_route = route.new_route(deepcopy(route.jobs))
    state = tmp_state = problem.get_state(tmp_route)
    size = len(tmp_route.jobs)
    changed = True

    logging.info(f'\nTwo opt started, tt:{state.travel_time}, cost:{state.cost}')

    while changed:
        changed = False
        best_state, best_route = tmp_state, tmp_route

        for it1 in range(size):
            for it3 in range(it1 + 1, size):
                path = swap(tmp_route.jobs, it1, it3)
                new_route = tmp_route.new_route(path)
                new_state = problem.get_state(new_route)
                if new_state is None:
                    continue

                if new_state < best_state:
                    changed = True
                    best_state, best_route = new_state, new_route

        if changed:
            tmp_state, tmp_route = best_state, best_route
            logging.info(f'Updated, tt:{best_state.travel_time}, cost:{best_state.cost}')

    logging.info(f'Ended, tt:{tmp_state.travel_time}, cost:{tmp_state.cost}')
    if tmp_state < state:
        route.jobs = tmp_route.jobs
        return True
    return False
