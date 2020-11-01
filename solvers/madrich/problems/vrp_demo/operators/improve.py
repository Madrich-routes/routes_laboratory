import logging
from copy import deepcopy
from typing import Tuple

from solvers.madrich.problems.vrp_demo.models import Problem, Tour
from solvers.madrich.problems.vrp_demo.operators.insert_job import insert_best
from solvers.madrich.problems.vrp_demo.operators.inter_operators import inter_cross, inter_replace, inter_swap
from solvers.madrich.problems.vrp_demo.operators.intra_operators import three_opt, two_opt


def improve_tour(tour: Tour, problem: Problem, cross=False, three=False) -> Tuple[bool, Tour]:
    def statistic(val: list):
        return f'{val}, sum: {sum(val)}'

    logging.info('Improving...')

    logging.info('\nImprove started')
    changed, result = True, False
    while changed:
        changed = False
        logging.info(f'Routes: {statistic([len(route) for route in tour.routes])}')
        logging.info(f'Travel time: {statistic([route.travel_time for route in tour.routes])}')

        if __inter_improve(tour, problem, cross):
            changed = result = True
        if __intra_improve(tour, problem, three):
            changed = result = True
        if __unassigned_insert(tour, problem):
            changed = result = True
        if __route_decrease(tour, problem):
            changed = result = True

    logging.info(f'\nDone\nRoutes: {statistic([len(route) for route in tour.routes])}')
    logging.info(f'Travel time: {statistic([route.travel_time for route in tour.routes])}')
    return result, tour


def __inter_improve(tour: Tour, problem: Problem, cross=True) -> bool:
    changed, result = True, False

    while changed:
        changed = False
        size = len(tour)
        for i in range(size):
            for j in range(i + 1, size):
                if inter_swap(tour.routes[i], tour.routes[j], problem):
                    changed = result = True
                if inter_replace(tour.routes[i], tour.routes[j], problem):
                    changed = result = True
                if cross and inter_cross(tour.routes[i], tour.routes[j], problem):
                    changed = result = True

    return result


def __intra_improve(tour: Tour, problem: Problem, three=True) -> bool:
    state = tour.get_state()

    for route in tour.routes:
        two_opt(route, problem)
        if three:
            three_opt(route, problem)

    return tour.get_state() < state


def __unassigned_insert(tour: Tour, problem: Problem) -> bool:
    logging.info(f'\nUnassigned insert started, routes:{len(tour)}')

    done = []
    for job in tour.unassigned_jobs:
        if insert_best(job, tour.routes, problem):
            logging.info('Inserted')
            done.append(job)

    for job in done:
        tour.unassigned_jobs.remove(job)
    return len(done) > 0


def __route_decrease(tour: Tour, problem: Problem) -> bool:
    logging.info(f'\nRoute decrease started, routes:{len(tour)}')
    idx, size = -1, -1

    for i, route in enumerate(tour.routes):
        if size == -1 or size > route.travel_time:
            idx, size = i, route.travel_time

    if idx == -1:
        return False
    route = tour.routes.pop(idx)
    removal_jobs = deepcopy(route.jobs)
    in_routes = deepcopy(tour.routes)

    for job in removal_jobs:
        if not insert_best(job, in_routes, problem):
            break
    else:
        tour.routes = in_routes
        logging.info(f'Decrease positive, routes:{len(tour)}')
        return True

    tour.routes.append(route)
    logging.info(f'Decrease negative, routes: {len(tour)}')
    return False
