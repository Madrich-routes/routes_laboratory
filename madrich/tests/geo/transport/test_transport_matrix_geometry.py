import pandas as pd

from madrich import settings
from madrich.geo.providers import osrm_module
from madrich.models.rich_vrp.geometries.transport import TransportMatrixGeometry


def test_matrix():
    data = pd.read_excel(settings.DATA_DIR / "eapteka/data/update_3.xlsx")
    data = data.head(100)
    points = [(float(row.lat), float(row.lng)) for row in data.itertuples()]
    _, walk_matrix = osrm_module.get_osrm_matrix(
        src=points, transport="foot", return_distances=False
    )

    tmg = TransportMatrixGeometry(points, walk_matrix)
    for i in range(11, 15):
        t = tmg.time(10, i)
        print(points[10], points[i])
        print(t)
    k = 0


if __name__ == "__main__":
    test_matrix()
