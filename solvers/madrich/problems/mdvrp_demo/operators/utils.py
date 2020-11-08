import numba as nb
import numpy as np

from solvers.madrich.problems.mdvrp_demo.models import Route, Tour


@nb.njit
def check_values(left: np.ndarray, right: np.ndarray) -> bool:
    """left <= right."""
    for i in range(len(left)):
        if not left[i] <= right[i]:
            return False
    return True


class Block:
    """Проверяем есть ли смысл пытаться что-то улучшить."""

    def __init__(self, tour: Tour):
        self.prev_phase_route = {route.courier.name: True for route in tour.routes}
        self.curr_phase_route = {route.courier.name: False for route in tour.routes}
        # self.prev_phase_track = {storage.name: True for storage in tour.storages}
        # self.curr_phase_track = {storage.name: False for storage in tour.storages}

    def update_phase(self):
        self.prev_phase_route = self.curr_phase_route
        # self.prev_phase_track = self.curr_phase_track
        self.curr_phase_route = {key: False for key in self.curr_phase_route}
        # self.curr_phase_track = {key: False for key in self.curr_phase_track}

    # def check_tracks(self, track1: Track, track2: Track) -> bool:
    #     """ Менялись или нет """
    #     state1 = self.block_track[track1.storage.name]
    #     state2 = self.block_track[track2.storage.name]
    #     return (state1 == -1 or state1 == 1) or (state2 == -1 or state2 == 1)

    def check_route(self, route: Route) -> bool:
        """Менялось или нет."""
        curr_state = self.curr_phase_route[route.courier.name]
        prev_state = self.prev_phase_route[route.courier.name]
        return curr_state or prev_state

    # def mark_track(self, track: Track, value: bool):
    #     """ Поменялся или нет """
    #     self.block_track[track.storage.name] = value

    def mark_route(self, route: Route, value: bool):
        """Поменялся или нет."""
        curr_state = self.curr_phase_route[route.courier.name]
        if not curr_state and value:
            self.curr_phase_route[route.courier.name] = value

    def mark_routes(self, route1: Route, route2: Route, value: bool):
        """Поменялся или нет."""
        self.mark_route(route1, value)
        self.mark_route(route2, value)
