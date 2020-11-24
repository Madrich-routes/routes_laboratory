import os
from typing import Dict, List, Tuple

from pyomo.core import AbstractModel, Boolean, Constraint, NonNegativeReals, Objective, Param, Set, Var
from pyomo.opt import SolverFactory


def get_cbc():
    opt = SolverFactory("cbc")
    opt.options["threads"] = os.cpu_count()
    # opt.options['absmipgap'] = 1
    # mb ratioGap = 1%
    # seconds = 1000 sec?

    return opt


class SimpleFlowModel:
    def __init__(self):
        mod = AbstractModel()

        mod.trips = Set()
        mod.cars = Set()
        mod.hours = Set()

        # mod.h12_forward_start = Set(within=mod.hours)
        mod.hours = Set(within=mod.hours)
        mod.hours = Set(within=mod.hours)

        # всякие дополниельные множества
        mod.transitions = Set(within=mod.trips * mod.trips)
        mod.car_trips = Set(within=mod.cars * mod.trips)
        mod.car_transition_hour = Set(within=mod.cars * mod.transitions * mod.hours)

        # Параметры модели
        mod.trip_historic_start = Param(mod.trips, within=NonNegativeReals, mutable=True)
        mod.trip_duration = Param(mod.trips, within=NonNegativeReals, mutable=True)
        mod.transition_duration = Param(mod.transitions, within=NonNegativeReals, mutable=True)

        # Переменные
        mod.car_transition_hour_var = Var(mod.car_transition_hour, within=Boolean)

        # -------------------------------- Ограничения ------------------------------------

        mod.trip_one_car = Constraint(
            mod.trips,
            rule=lambda m, t: sum(
                mod.car_transition_hour_var[c, t, h]
                for c in mod.cars
                for h in mod.hours
            ) == 1,
            doc="Каждый трип берет ровно одна машина",
        )

        mod.trip_start_3_days_later = Constraint(
            mod.trips,
            rule=lambda m, t: self.trip_start_time(m, t) - mod.trip_historic_start[t] <= 3 * 24,
            doc="Трип начинается не позже чем через 3 дня от реального",
        )

        mod.trip_start_3_days_earlier = Constraint(
            mod.trips,
            rule=lambda m, t: mod.trip_historic_start[t] - self.trip_start_time(m, t) >= 3 * 24,
            doc="Трип начинается не раньше чем через 3 дня от реального",
        )

        mod.transition_24 = Constraint(
            mod.car_transition_pairs,
            rule=lambda m, c, t1, t2: ...,
            doc="Пауза не больше 24 часов",
        )

        mod.transition_12 = Constraint(
            mod.car_transition_pairs,
            rule=lambda m, c, t1, t2: ...,
            doc="Пауза не меньше 12 часов",
        )

        # Пустой objective
        mod.total = Objective(expr=1)

        self.mod = mod

    def trip_start_time(self, m, t):
        """Время начала."""
        return sum(
            m.car_transition_hour_var[c, t, h] * h
            for h in m.hours
            for c in m.cars
        )

    def trip_car(self, m, t):
        """Машина, которая взяла trip."""
        return sum(
            m.car_transition_hour_var[c, t, h] * c
            for h in m.hours
            for c in m.cars
        )

    def trips_next_12_hours(self, m, c, h):
        """В ближайшие 12 часов."""
        return sum(
            m.car_transition_hour_var[c, t, h] + m.car_transition_hour_var[c, t, h] * c
            for t in m.trips
        )

    def instantiate(  # noqa
        self,
        sources: List[int],  # id вершин
        middles: List[int],  # id середин
        destinations: List[int],  # список id стоков

        edges: List[Tuple[int, int]],  # допустимые ребра
        capacities: Dict[int, float],  # словарь вершина -> пропускная способность
        prices: Dict[Tuple, float],  # (v1, v2) -> цена на единицук потока
        source_vol: Dict[int, float],  # индекс источника -> генерируемый поток
    ):
        # sources_set, middles_set, dest_set = map(set, [sources, middles, destinations])
        # non_source_set = middles_set | dest_set

        data = {None: {
            # Множества
            'sources': {None: sources},
            'middles': {None: middles},
            'destinations': {None: destinations},
            'all_edges': {None: edges},

            # Параметры
            'capacities': capacities,
            'prices': prices,
            'source_vol': source_vol,
        }}

        return self.mod.create_instance(data)
