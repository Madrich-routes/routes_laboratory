import logging
from sys import maxsize
from typing import List

from madrich.problems.mdvrp_demo.models import Problem, Route, Job, Tour
from madrich.problems.mdvrp_demo.operators.utils import Block

"""
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
"""

def insert_best(block : Block, job: Job, routes: List[Route], problem: Problem) -> bool:
    logging.info('Insert started')
    best_insert = (-1, -1, -1)
    best_time = maxsize

    for i, route in enumerate(routes):

        if not block.check_route(route):
            logging.info('\nBLOCKED: insert_job')
            block.mark_route(route, False)
            continue
        status = False
        old_tt = route.state.travel_time
        for k, track in enumerate(route.tracks):
            # проверяем на перевес
            state_track = problem.get_state_track(track, route)
            size_v = len(state_track.value)
            for t in range(size_v):
                if state_track.value[t] + job.value[t] > route.courier.value[t]:
                    logging.info('\n track cant insert this job')
                    continue

            for j in range(len(track) + 1):
                old_jobs = track.jobs
                new_jobs = track.jobs[:j] + [job] + track.jobs[j:]
                track.jobs = new_jobs

                state = problem.get_state(route)
                if state is None:
                    track.jobs = old_jobs
                    continue
                new_time = state.travel_time - old_tt
                if new_time < best_time:
                    best_time = new_time
                    best_insert = (i, j, k)
                    status = True
                track.jobs = old_jobs
        block.mark_route(route, status)

    if best_insert[0] == -1:
        logging.info('Insert negative')
        return False

    i, j, k = best_insert
    route = routes[i]
    route.tracks[k].jobs = route.tracks[k].jobs[:j] + [job] + route.tracks[k].jobs[j:]
    logging.info('Insert positive')
    return True

def insert(tour: Tour, problem: Problem) -> bool:
    logging.info(f'\nUnassigned insert started, routes:{len(tour)}')
    block = Block(tour)

    result = False
    for storage in tour.storages:
        done = []
        unassigned_jobs = storage.unassigned_jobs
        for job in unassigned_jobs:
            if insert_best(block, job, tour.routes, problem):
                logging.info('Inserted')
                done.append(job)
                result = True

        for job in done:
            storage.unassigned_jobs.remove(job)
    return result