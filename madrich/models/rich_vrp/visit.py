from dataclasses import dataclass

from madrich.models.rich_vrp.place import Place
from madrich.solvers.vrp_cli.converters import ts_to_rfc


@dataclass
class Visit:
    place: Place
    activity: str
    arrival: int  # секунды с начала мира, когда приехал на точку
    departure: int  # секунды с начала мира, когда уехал на точку

    def __repr__(self):
        return f'{ts_to_rfc(self.arrival)} {ts_to_rfc(self.departure)}'
