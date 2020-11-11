import pandas as pd

import settings
from models.rich_vrp.geometries.transport import TransportMatrixGeometry
from geo.providers import osrm_module


def test_matrix():
    data = pd.read_excel(settings.DATA_DIR / "eapteka/data/update_3.xlsx")
    data = data.head(100)
    points = [(float(row.lat), float(row.lng)) for row in data.itertuples()]
    _, walk_matrix = osrm_module.get_osrm_matrix(
        src=points, transport="foot", return_distances=False
    )

    tmg = TransportMatrixGeometry(points, walk_matrix)
    t = tmg.time(10, 20)
    print(t)


if __name__ == "__main__":
    test_matrix()