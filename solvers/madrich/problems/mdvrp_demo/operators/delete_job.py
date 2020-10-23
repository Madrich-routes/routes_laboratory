import logging

from madrich.problems.mdvrp_demo.models import Tour, Problem, Route, Job, Track
from madrich.problems.mdvrp_demo.operators.utils import Block


def delete_job(vec : int, job : Job, track : Track, route : Route, problem : Problem) -> None:
    """
    :param vec:
    :param job: работа на удаление
    :param track: трек из которого удалять
    :param route: путь из которого взяли трек
    :param problem:
    :return:
    """
    track.storage.assigned_jobs.remove(job)
    for t in route.tracks:
        t.storage.unassigned_jobs += t.storage.assigned_jobs
        t.storage.assigned_jobs = []
    route = problem.greedy_route(vec, route.courier, {route.courier.profile : route.matrix})


