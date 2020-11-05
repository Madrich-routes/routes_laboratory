import random
from collections import Callable

from algorithms.metaheuristics.genetic.models import BaseIndividual
from temp.tsp import List
from utils.types import Array

import numpy as np


def select_lexicase(
    population: List[BaseIndividual],
    k: int,
    n_objectives: int,
    epsilon: float = None,
):
    """
    Выбираем лучших по каждой метрике.
    Вообще-то, похоже, что это было придумано для разных измерений величины. (хз)

    http://faculty.hampshire.edu/lspector/pubs/lexicase-IEEE-TEC.pdf
    https://push-language.hampshire.edu/uploads/default/original/1X/35c30e47ef6323a0a949402914453f277fb1b5b0.pdf
    """

    def estimate_epsilon(metrics: Array):
        """
        Автоматически оцениваем epsilon
        """
        median_val = np.median(metrics)
        return np.median(np.abs(metrics - median_val))

    def update_candidates(candidates, m):
        """
        Оставляем только хороших кандидатов
        """
        metrics = np.array([x.metrics[m] for x in candidates])
        max_val = metrics.max()
        eps = (
            estimate_epsilon(metrics) if epsilon is not None else None
        )  # Назвать пременную epsilon не выйдет

        return candidates[max_val - metrics <= eps]

    chosen = []
    for _ in range(k):
        metrics_idx = np.random.permutation(n_objectives)  # случайная перестановка
        candidates = np.array(population)

        for m in metrics_idx:
            candidates = update_candidates(candidates, m)
            if len(candidates) == 1:
                break

        chosen += [random.choice(candidates)]


def select_double_tournament(
    population: List[BaseIndividual],
    k: int,
    first_size: int,
    choose_first: Callable[[List[BaseIndividual]], List[BaseIndividual]],
    choose_second: Callable[[List[BaseIndividual]], List[BaseIndividual]],
):
    """
    Отбираем в 2 этапа, можно по разным метрикам. Можно обобщить на разные метрики.
    В оригинале, первая — select_probability_tournament по длине вектора, потом select_tournament по fitness.
    select_probability_tournament используется, чтобы уменьшить давление отбора.

    Для лучших результатов предлагается ограничить глубину (wat?).
    Говорят, что не важно что делать первым, что вторым.

    .. [Luke2002fighting] Luke and Panait, 2002, Fighting bloat with
    nonparametric parsimony pressure
    """
    chosen = choose_first(population, k=first_size)
    return choose_second(chosen, k=k)
