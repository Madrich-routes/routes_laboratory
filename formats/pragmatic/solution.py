from datetime import datetime
from typing import Dict, List, Optional

import ujson

from models.rich_vrp import VRPSolution, Agent, Visit, Depot, Job
from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem


def search_depot(
    location: Dict[str, float], problem: RichVRPProblem
) -> Optional[Depot]:
    """Ищем склад в списках складов в заданной проблеме"""
    ret_point: Optional[Depot] = None
    lat = location['lat']
    lon = location['lon']

    for depot in problem.depots:
        if depot.lat == lat and depot.lon == lon:
            ret_point = depot
            break

    return ret_point


def search_job(job_id: int, problem: RichVRPProblem) -> Optional[Job]:
    """Ищем заказ в списках заказов в заданной проблеме"""
    ret_point: Optional[Job] = None

    for job in problem.jobs:
        if job.id == job_id:
            ret_point = job
            break

    return ret_point


def search_agent(agent_name: str, problem: RichVRPProblem) -> Optional[Agent]:
    """Ищем агента по его имени (vehicle_id) в заданной проблеме"""
    ret_agent: Optional[Agent] = None

    for agent in problem.agents:
        if agent.name == agent_name or str(agent.id) == agent_name:
            ret_agent = agent
            break

    return ret_agent


def load_solution(problem: RichVRPProblem, pragmatic_solution: str) -> VRPSolution:
    """Загружаем решение проблемы.

    Parameters
    ----------
    problem : класс проблемы со всеми агентами и задачами
    pragmatic_solution : строка с решением

    Returns
    -------
    VRPSolution instance
    """
    routes: List[Plan] = []
    data = ujson.loads(pragmatic_solution)

    for tour in data['tours']:
        agent: Optional[Agent] = search_agent(tour['vehicleId'], problem)
        if agent is None:
            raise Exception("Не найден агент для rust vrp solution")

        waypoints: List[Visit] = []
        for point in tour['stops']:
            job_type: str = point['activities'][0]['type']

            if job_type == 'departure':  # точка выезда курьера
                waypoint = agent.start_place
            elif job_type == 'delivery':  # точка доставка заказа
                waypoint = search_job(int(point['activities'][0]['jobId']), problem)
            elif job_type == 'arrival':  # точка окончания пути курьера
                waypoint = agent.end_place
            elif job_type == 'break':  # TODO: break points
                raise Exception('Break: не поддерживается в данной версии')
            elif job_type == 'reload':  # точка перезагрузки курьера
                waypoint = search_depot(point['location'], problem)
            elif job_type == 'pickup':  # точка забирания заказа курьером
                waypoint = search_job(point['activities']['jobId'], problem)
            else:
                raise Exception("Неподдерживаемый тип задач")

            if waypoint is None:
                raise Exception("Не найдена точка для rust vrp solution")

            t = int(
                datetime.strptime(
                    point['time']['arrival'], '%Y-%m-%dT%H:%M:%SZ'
                ).timestamp()
            )
            waypoints.append(Visit(place=waypoint, time=t))

        routes.append(Plan(agent=agent, waypoints=waypoints))

    return VRPSolution(problem=problem, routes=routes, info=data['statistic'])
