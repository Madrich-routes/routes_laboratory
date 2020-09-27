"""
В этом модуле откидываются лишние ребра-кандидаты, а также им назначаются новые приоритеты с учетом ограничений.
"""
from typing import List, Set

from algorithms.candidate_edges.models import CandidateEdge
from utils.iteration import sets_intersection
from utils.types import Array


# TODO: Делать pruning до начала расчета кандидатов. И заменять в матрице на большие значения.
# TODO: Продумать оценку исходя из всех посчитанных характеристик.


def prune_time_windows(
        matrix: Array,
        candidates: List[CandidateEdge],
        tws: Array,
        max_wait: int = 0,
):
    """
    Убираем те ребра, которые точно не подходят по временным окнам
    candidates — Изначальное множество кандидатов для каждой точки матрицы
    tws - Массив временных окон List[(start, end)] для каждой точки матрицы
    """
    pruned_candidates = []

    for e in candidates:
        src_start = tws[e.src][0]
        dst_start = tws[e.dst][0] - matrix[e.src, e.dst]
        src_end = tws[e.src][1]
        dst_end = tws[e.dst][1] - matrix[e.src, e.dst]

        wait_time = src_end - dst_start  # время ожидания
        w1 = max_wait - wait_time
        w2 = dst_end - src_start
        w = min(w1, w2)

        # Не успеем или приезжаем раньше
        if w > 0:
            e.tw = w
            pruned_candidates += [e]

    return pruned_candidates


def prune_skills(
        candidates: List[CandidateEdge],  # набор ребер-кандидатов
        agents: List[Set[int]],  # набор исполнителей для каждого скила
        required_skills: List[Set[int]],  # скилы, которые требуются каждой джобе
):
    """
    Выкидываем ребра-кандидаты, которые не подходят друг-другу по скилам.
    Тем, которые подходят выставляем приоритеты.
    """
    pruned_candidates = []

    for e in candidates:
        start_agents = sets_intersection(agents[skill] for skill in required_skills[e.src])
        end_agents = sets_intersection(agents[skill] for skill in required_skills[e.dst])
        allowed = start_agents & end_agents

        if len(allowed) == 0:
            continue
        else:
            e.agents = agents
            pruned_candidates += [e]

    return pruned_candidates
