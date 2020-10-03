from models.rich_vrp.base import GeoPoint


class Depot(GeoPoint):
    def __init__(
            self,
            lat: float,
            lon: float,
            id_: int,
            address: str = ''
    ):
        super().__init__(id_=id_, lat=lat, lon=lon, address=address)

    def __hash__(self):
        return hash(self.id_)
