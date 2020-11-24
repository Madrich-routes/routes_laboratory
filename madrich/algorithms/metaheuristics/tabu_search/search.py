"""Основной алгоримт табу-поиска. """
from fastcore.foundation import L, attrgetter


def tabu_search(
    s0,
    max_iterations: int = 100,
    max_tabu_size: int = 200,
):
    current_best = s0
    best_candidate = s0
    tabu_list = []

    for _ in range(max_iterations):
        neighbourhood = L(best_candidate.neighbours()).filter(lambda n: n in tabu_list)
        best_candidate = max(neighbourhood, key=attrgetter('fitness'))

        if best_candidate.fitness > current_best.fitness:
            current_best = best_candidate

        tabu_list += [best_candidate]

        if len(tabu_list) > max_tabu_size:
            tabu_list = tabu_list[:10]

    return current_best
