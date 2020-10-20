import logging
from sys import maxsize
from typing import List

from madrich.problems.vrp_demo.models import Problem, Route, Job


def insert_greedy(job: Job, routes: List[Route], problem: Problem) -> bool:
    logging.info('Greedy insert started')
    for route in routes:
        for i in range(len(route) + 1):
            jobs = route.jobs[:i] + [job] + route.jobs[i:]
            state = problem.get_state(route.new_route(jobs))
            if state is None:
                continue

            route.jobs = jobs
            logging.info('Greedy insert positive')
            return True
    logging.info('Greedy insert negative')
    return False


def insert_best(job: Job, routes: List[Route], problem: Problem) -> bool:
    logging.info('Insert started')
    best_insert = (-1, -1)
    best_time = maxsize

    for i, route in enumerate(routes):
        old_tt = route.transport_travel_time
        for j in range(len(route) + 1):
            jobs = route.jobs[:j] + [job] + route.jobs[j:]
            state = problem.get_state(route.new_route(jobs))
            if state is None:
                continue
            new_time = state.transport_travel_time - old_tt
            if new_time < best_time:
                best_time = new_time
                best_insert = (i, j)

    if best_insert[0] == -1:
        logging.info('Insert negative')
        return False

    i, j = best_insert
    route = routes[i]
    route.jobs = route.jobs[:j] + [job] + route.jobs[j:]
    logging.info('Insert positive')
    return True
