import pandas as pd

from models.rich_vrp.geometries.transport import TransportMatrixGeometry
from geo.providers import osrm_module


def main():
    data = pd.read_excel("../../../data/eapteka/data/update_3.xlsx")
    data = data.head(100)
    points = [(row.lat, row.lng) for row in data.itertuples()]
    _, walk_matrix = osrm_module.get_osrm_matrix(
        src=points, dst=[], transport="foot", return_distances=False
    )

    tmg = TransportMatrixGeometry(points, walk_matrix)
    t = tmg.time(10, 20)
    print(t)


if __name__ == "__main__":
    main()
