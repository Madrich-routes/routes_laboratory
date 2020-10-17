from models.rich_vrp.agent import Agent
from models.rich_vrp.geometry import BaseGeometry


def export_coords(lat: float, lon: float):
    return [lon, lat]



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
