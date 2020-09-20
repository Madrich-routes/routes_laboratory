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

        # всякие дополниельные множества
        mod.transitions = Set(within=mod.trips * mod.trips)
        mod.car_transition_hour = Set(within=mod.cars * mod.transitions * mod.hours)

        # Параметры модели
        mod.trip_historic_start = Param(mod.trips, within=NonNegativeReals, mutable=True)
        mod.trip_duration = Param(mod.trips, within=NonNegativeReals, mutable=True)
        mod.transition_duration = Param(mod.transitions, within=NonNegativeReals, mutable=True)

        # Переменные
        mod.car_transition_hour_var = Var(mod.car_transition_hour, within=Boolean)

        # -------------------------------- Ограничения ------------------------------------

        # TODO: учитывается ли, что выезжает та же машина, что въезжает?
        # TODO: а что делать с первыми, из которых только выезжает?
        # TODO: учесть trip duration?

        mod.trip_one_car = Constraint(
            mod.trips,
            rule=lambda m, t2: sum(
                m.car_transition_hour_var[c, t1, t2, h]
                for c in m.cars
                for t1 in m.trips
                for h in m.hours
            ) == 1,
            doc="В каждый трип входит ровно 1 transition",
        )

        mod.trip_one_car = Constraint(
            mod.trips,
            rule=lambda m, t1: sum(
                m.car_transition_hour_var[c, t1, t2, h]
                for c in m.cars
                for t2 in m.trips
                for h in m.hours
            ) == 1,
            doc="Из каждого трипа выходит ровно 1 transition",
        )

        mod.trip_start_3_days_later = Constraint(
            mod.trips,
            rule=lambda m, t: self.trip_time(m, t) - mod.trip_historic_start[t] <= 3 * 24,
            doc="Трип начинается не позже чем через 3 дня от реального",
        )

        mod.trip_start_3_days_earlier = Constraint(
            mod.trips,
            rule=lambda m, t: mod.trip_historic_start[t] - self.trip_time(m, t) >= 3 * 24,
            doc="Трип начинается не раньше чем через 3 дня от реального",
        )

        mod.transition_24 = Constraint(
            mod.transitions,
            rule=lambda m, t1, t2: self.transition_time(m, t1, t2) <= 24,
            doc="Пауза не больше 24 часов",
        )

        mod.transition_12 = Constraint(
            mod.transitions,
            rule=lambda m, t1, t2: self.transition_time(m, t1, t2) >= 12,
            doc="Пауза не меньше 12 часов",
        )

        mod.transition_time_ok = Constraint(
            mod.transitions,
            rule=lambda m, t1, t2: self.transition_time(m, t1, t2) <= m.transition_duration[t1, t2],
            doc="Успеем доехать transition",
        )

        # Пустой objective
        mod.total = Objective(expr=1)

        self.mod = mod

    def transition_start_time(self, m, t1):
        """
        Время, когда из t1 уехали
        """
        return sum(
            m.car_transition_hour_var[c, t1, t2, h] * h
            for h in m.hours
            for t2 in m.trips
            for c in m.cars
        )

    def transition_end_time(self, m, t2):
        """
        Время, когда в t2 приехали
        """
        return sum(
            m.car_transition_hour_var[c, t1, t2, h] * h
            for h in m.hours
            for t1 in m.trips
            for c in m.cars
        )

    def trip_time(self, m, t):
        """
        Время, которое занимает trip
        """
        return self.transition_end_time(m, t) - self.transition_start_time(m, t)

    def transition_time(self, m, t1, t2):
        """
        Время, которое занимает transition
        """
        return self.transition_end_time(m, t2) - self.transition_start_time(m, t1)

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
