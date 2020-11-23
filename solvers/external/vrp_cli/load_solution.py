from datetime import datetime
from typing import List, Optional, Dict

from models.rich_vrp import VRPSolution, Agent, Job, Visit
from models.rich_vrp.plan import Plan
from models.rich_vrp.problem import RichVRPProblem


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


def generate_waypoints(agent: Agent, tour: Dict, problem: RichVRPProblem) -> List[Visit]:
    waypoints: List[Visit] = []

    for point in tour['stops']:
        job_type: str = point['activities'][0]['type']

        if job_type == 'departure':  # точка выезда курьера
            waypoint, activity = agent.start_place, 'departure'
        elif job_type == 'delivery':  # точка доставка заказа
            waypoint, activity = search_job(int(point['activities'][0]['jobId']), problem), 'delivery'
        elif job_type == 'arrival':  # точка окончания пути курьера
            waypoint, activity = agent.end_place, 'arrival'
        elif job_type == 'reload':  # точка перезагрузки курьера
            waypoint, activity = problem.depot, 'reload'
        else:
            raise Exception("Неподдерживаемый тип задач")

        if waypoint is None:
            raise Exception("Не найдена точка для rust vrp solution")

        arrival = int(datetime.strptime(point['time']['arrival'], '%Y-%m-%dT%H:%M:%SZ').timestamp())
        departure = int(datetime.strptime(point['time']['departure'], '%Y-%m-%dT%H:%M:%SZ').timestamp())
        waypoints.append(Visit(place=waypoint, arrival=arrival, departure=departure, activity=activity))

    return waypoints


def load_solution(problem: RichVRPProblem, solution: dict) -> VRPSolution:
    """Загружаем решение проблемы.

    Parameters
    ----------
    problem : класс проблемы со всеми агентами и задачами
    solution : строка с решением

    Returns
    -------
    VRPSolution instance
    """
    routes: List[Plan] = []

    for tour in solution['tours']:
        agent: Optional[Agent] = search_agent(tour['vehicleId'], problem)
        if agent is None:
            raise Exception("Не найден агент для rust vrp solution")

        waypoints = generate_waypoints(agent, tour, problem)
        routes.append(Plan(agent=agent, waypoints=waypoints, info=tour['statistic']))

    return VRPSolution(problem=problem, routes=routes, info=solution['statistic'])