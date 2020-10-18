from models.rich_vrp.job import Place


class Depot(Place):
    def __init__(
            self,
            lat: float,
            lon: float,
            id: int,
            address: str = ''
    ):
        super().__init__(id=id, lat=lat, lon=lon, address=address)

    def __hash__(self):
        return hash(self.id)
