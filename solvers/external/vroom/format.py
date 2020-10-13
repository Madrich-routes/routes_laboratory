from models.rich_vrp.agent import Agent
from models.rich_vrp.geometry import BaseGeometry
from models.rich_vrp.job import Job


def export_coords(lat: float, lon: float):
    return [lon, lat]


def export_job(job: Job):
    """

    """
    return {
        'id': job.id,
        'description': str(job),
        'location_index': ...,  # TODO:
        'delivery': [],
        'pickup': [],
        'skills': job.required_skills,
        'priority': job.priority,
        'time_windows': job.time_windows
    }


# def export_break(job: Job):

def export_vehicle(agent: Agent):
    return {
        "id": agent.id,
        "profile": "car",
        "description": str(agent),
        "start_index": str()
    }


def export_matrix(gm: BaseGeometry):
    """
    Дампаем матрицу времени
    """
    return gm.time_matrix()
