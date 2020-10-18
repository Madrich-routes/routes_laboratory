import logging
from typing import Tuple

from madrich.problems.mdvrp_demo.models import Tour, Problem, Route
from madrich.problems.mdvrp_demo.operators.inter_operator import inter_swap, inter_replace, inter_cross
from madrich.problems.mdvrp_demo.operators.intra_operator import two_opt, three_opt
from madrich.problems.mdvrp_demo.operators.utils import Block


def improve_tour(tour: Tour, problem: Problem, cross=False, three=False) -> Tuple[bool, Tour]:
    logging.info('\nImprove started')
    block = Block(tour)
    changed, result = True, False

    while changed:
        changed = False
        if inter_improve(tour, problem, block, cross):
            changed = result = True
        if intra_improve(tour, problem, block, three):
            changed = result = True
        block.update_phase()

    logging.info(f'\nDone')
    return result, tour


def inter_improve(tour: Tour, problem: Problem, block: Block, cross=True) -> bool:
    changed, result = True, False

    size = len(tour.routes)
    for i in range(size):
        for j in range(i + 1, size):
            route1, route2 = tour.routes[i], tour.routes[j]

            if not (block.check_route(route1) or block.check_route(route2)):
                logging.info('\nBLOCKED: inter')
                block.mark_routes(route1, route2, False)
                continue

            answer = __inter_improve(route1, route2, problem, block, cross)
            if answer:
                result = True
            block.mark_routes(tour.routes[i], tour.routes[j], answer)

    return result


def __inter_improve(route1: Route, route2: Route, problem: Problem, block: Block, cross: bool) -> bool:
    changed, result = True, False

    while changed:
        changed = False

        for tr1, track1 in enumerate(route1.tracks):
            for tr2, track2 in enumerate(route2.tracks):
                # можно докидать ограничений для производительности метода
                if track1.storage.name != track2.storage.name:
                    continue
                if inter_swap(tr1, tr2, route1, route2, problem):
                    changed = result = True
                if inter_replace(tr1, tr2, route1, route2, problem):
                    changed = result = True
                if cross and not changed and inter_cross(tr1, tr2, route1, route2, problem):
                    changed = result = True

    return result


def intra_improve(tour: Tour, problem: Problem, block: Block, three=True) -> bool:
    state = tour.get_state()

    for route in tour.routes:

        if not block.check_route(route):
            logging.info('\nBLOCKED: intra')
            block.mark_route(route, False)
            continue

        status = two_opt(route, problem)
        if three:
            status = three_opt(route, problem)
        block.mark_route(route, status)

    return tour.get_state() < state
