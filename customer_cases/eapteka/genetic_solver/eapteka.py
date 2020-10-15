import logging
from collections import defaultdict
from typing import Tuple, List, Dict

import pandas as pd
import ujson

from customer_cases.eapteka.genetic_solver.models import Courier, Depot, Task
from customer_cases.eapteka.genetic_solver.runner import runner
from customer_cases.eapteka.genetic_solver.utils import cut_windows, get_index, add_depot, send_courier, add_tour, \
    add_courier

Point = Tuple[float, float]


def prepare_courier(internal_mappings: dict, depot_id: str, depot: Depot, couriers: List[Courier]):
    """ Prepare courier for send them to depot
    """
    courier_loc = 0
    for point in internal_mappings[depot_id]:
        courier_loc = internal_mappings[depot_id][point]
    revers_internal_mapping = {v: k for k, v in internal_mappings[depot_id].items()}

    for courier in couriers:
        courier.start = courier_loc
        courier.end = courier_loc

    tmp_couriers = cut_windows(couriers, depot)

    return revers_internal_mapping, tmp_couriers


def prepare_statistic(depot_id: str, solution: dict, address_mapping: dict, revers_mapping: dict, tours: dict,
                      depots_output: dict, couriers_output: dict):
    """
    Save statistic from solution
    """
    statistic = solution['statistic']
    add_depot(depots_output, depot_id, statistic['distance'], statistic['duration'])
    names, st = [], 0

    for tour in solution['tours']:
        name = tour['vehicleId']
        points = len(tour['stops'])
        if points - 3 == 0:
            continue
        st += points
        start_time = tour['stops'][0]['time']['arrival']
        end_time = tour['stops'][-1]['time']['departure']
        duration = tour['statistic']['duration']
        distance = tour['statistic']['distance']
        tour_data = defaultdict(list)

        for j in range(0, points):
            point = tour['stops'][j]
            arrival = point['time']['arrival']
            departure = point['time']['departure']
            activity = point['activities'][0]['type']
            if activity != 'delivery':
                points -= 1
                st -= 1
            weight, capacity = [0, 0] if activity == 'departure' else point['load']
            loc = revers_mapping[point['location']['index']]
            address, was, corrected = address_mapping[(loc[0], loc[1])]
            add_tour(tour_data, address, was, corrected, loc, arrival, departure, activity, weight, capacity)

        add_courier(couriers_output, name, depot_id, start_time, end_time, distance, duration, points)
        tours[f'{name}{depot_id}'] = tour_data
        names.append((name, start_time, end_time))

    return st, names


def refactor_couriers(couriers: List[Courier], names: List[Tuple[str, str, str]]) -> Tuple[int, List[Courier]]:
    """ Refactor used couriers for sending them to another depots
    """
    sv, tmp_couriers = 0, []

    for name, start_time, end_time in names:
        for j, courier in enumerate(couriers):
            if courier.name == name:
                tmp = send_courier(courier, start_time, end_time)
                if tmp is not None:
                    tmp_couriers.append(tmp)
                    sv += 1
                del couriers[j]
                break

    return sv, tmp_couriers


def get_solution(depots: Dict[str, Depot], couriers: List[Courier], orders: Dict[str, List[Task]],
                 internal_mappings: dict, files: Dict[str, List[str]], profiles: List[str], address: dict,
                 couriers_path: str, depots_path: str, directory_couriers: str):
    """ Run solver and get solution
    """
    solutions, tours, all_points = {}, {}, 0
    couriers_output, depots_output = defaultdict(list), defaultdict(list)

    for i, (depot_id, depot) in enumerate(depots.items()):
        logging.info('\n')
        logging.info(f'Problem: {depot_id} id: {i}')
        logging.info(f'Couriers: {len(couriers)}')
        logging.info(f'Orders: {len(orders[depot_id]) - 2}')

        revers, tmp_couriers = prepare_courier(internal_mappings, depot_id, depot, couriers)
        solution = runner(orders[depot_id], depot_id, depot, tmp_couriers, profiles, files)
        solutions[depot_id] = {'solution': solution, 'indexes': get_index(internal_mappings[depot_id])}

        logging.info(f'Not Solved: {0 if "unassigned" not in solution else len(solution["unassigned"])}')

        st, names = prepare_statistic(depot_id, solution, address, revers, tours, depots_output, couriers_output)
        sv, tmp_couriers = refactor_couriers(couriers, names)
        couriers += tmp_couriers
        all_points += st

        logging.info(f'Solved: {st}')
        logging.info(f'Couriers: {len(names)}')
        logging.info(f'Saved: {sv}')

    logging.info(f'\nSolved points: {all_points}')
    logging.info(f'Writing...')

    pd.DataFrame.from_dict(couriers_output).to_csv(couriers_path, index=False)
    pd.DataFrame.from_dict(depots_output).to_csv(depots_path, index=False)

    for name, tour in tours.items():
        pd.DataFrame.from_dict(tour).to_csv(f"{directory_couriers}/{name}.csv", index=False)

    with open('answer.json', 'w') as f:
        ujson.dump(solutions, f)

    logging.info('\nDone')
