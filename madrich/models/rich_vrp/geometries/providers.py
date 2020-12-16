from madrich.geo.providers.osrm_module import get_osrm_matrix
from madrich.models.rich_vrp.geometries.geometry import DistanceAndTimeMatrixGeometry
from madrich.utils.types import Array


class OSRMMatrixGeometry(DistanceAndTimeMatrixGeometry):
    """Простая геометрия, которая получает на вход одну матрицу расстояний и дефолтную скорость (которую можно
    менять)"""

    def __init__(
        self,
        points: Array,
        transport: str,
        stop_time=None,
    ) -> None:
        distances, durations = get_osrm_matrix(points, transport=transport)

        stop_time = stop_time if stop_time is not None else dict(
            car=5 * 60,
            foot=0,
            bicycle=1 * 60,
        )[transport]

        durations[durations != 0] += stop_time

        super().__init__(points, distance_matrix=distances, time_matrix=durations)

# class SimpleTransportGeometry(OSRMMatrixGeometry):
#     def __init__(
#         self,
#         points: Array,
#     ):
#         foot_dist, foot_time = osrm_module.get_osrm_matrix(points, transport='foot')
#         car_dist, car_time = osrm_module.get_osrm_matrix(points, transport='car')
#
#         res_time = np.zeros_like(foot_dist)
#         res_dist = np.zeros_like(foot_dist)
#
#         res_time[foot_time <= 15 * 60] = foot_time[foot_time <= res_time['time']]
#         res_time[15 * 60 < foot_time < 45 * 60] = foot_time[15 * 60 < foot_time < 45 * 60]
#
#         travel_times, distances = [], []
#         for i in range(len(points)):
#             for j in range(len(points)):
#                 pt = p_dist[i][j]
#                 dtt, dd = return_checked(p_time[i][j], p_time[i][j])
#
#                 if pt <= 15 * 60:
#                     travel_times.append(int(pt))
#                     distances.append(int(pt))
#                 elif 15 * 60 < pt < 45 * 60:
#                     tt = int(min(dtt * 1.5, pt))
#                     travel_times.append(tt)
#                     distances.append(int(dd))
#                 else:
#                     tt = int(min(dtt * 2, pt))
#                     travel_times.append(tt)
#                     distances.append(int(dd))
#
#     def _return_checked(
#         self,
#         time: int,
#         dist: int,
#     ):
#         if time != 0 and 5 < dist / time < 13:
#             if time > 2 * 60 * 60:
#                 return dist / 12, dist
#             elif dist > 100 * 1000:
#                 return time, time * 12
#             else:
#                 return dist / 12, dist
#
#         return time, dist
