#include "vrp_intra_operators.h"


bool three_opt(VrpRoute &route) {
    State tmp_state = route.state;
    std::vector<Job> tmp_jobs = route.jobs;
    int size = route.jobs.size();
    bool changed = true;
    printf("\nThree opt started, tt: %d, cost: %f\n", tmp_state.travel_time, tmp_state.cost);

    while (changed) {
        changed = false;
        State best_state = tmp_state;
        std::vector best_jobs = tmp_jobs;

        for (std::size_t it1 = 0; it1 < size; ++it1) {
            for (std::size_t it3 = it1 + 1; it3 < size; ++it3) {
                for (std::size_t it5 = it3 + 1; it5 < size; ++it5) {
                    for (std::size_t i = 0; i < 4; ++i) {
                        std::vector<Job> new_jobs = three_opt_exchange(tmp_jobs, i, it1, it3, it5);
                        route.jobs = new_jobs;
                        std::optional<State> new_state = VrpProblem::get_state(route);
                        if (!new_state) {
                            continue;
                        }
                        if (new_state.value() < best_state) {
                            changed = true;
                            best_state = new_state.value();
                            best_jobs = new_jobs;
                        }
                        route.jobs = tmp_jobs;
                    }
                }
            }
        }
        if (changed) {
            tmp_state = best_state;
            tmp_jobs = best_jobs;
            printf("Updated, tt: %d, cost: %f\n", best_state.travel_time, best_state.cost);
        }
    }
    printf("Ended, tt: %d, cost %f\n", tmp_state.travel_time, tmp_state.cost);
    route.jobs = tmp_jobs;
    if (tmp_state < route.state) {
        route.state = tmp_state;
        return true;
    }
    return false;
}


bool two_opt(VrpRoute &route) {
    State tmp_state = route.state;
    std::vector<Job> tmp_jobs = route.jobs;
    int size = route.jobs.size();
    bool changed = true;
    printf("\nTwo opt started, tt: %d, cost: %f\n", tmp_state.travel_time, tmp_state.cost);

    while (changed) {
        changed = false;
        State best_state = tmp_state;
        std::vector best_jobs = tmp_jobs;

        for (std::size_t it1 = 0; it1 < size; ++it1) {
            for (std::size_t it3 = it1 + 1; it3 < size; ++it3) {
                std::vector<Job> new_jobs = swap(tmp_jobs, it1, it3);
                route.jobs = new_jobs;
                std::optional<State> new_state = VrpProblem::get_state(route);
                if (!new_state) {
                    continue;
                }
                if (new_state.value() < best_state) {
                    changed = true;
                    best_state = new_state.value();
                    best_jobs = new_jobs;
                }
                route.jobs = tmp_jobs;
            }
        }
        if (changed) {
            tmp_state = best_state;
            tmp_jobs = best_jobs;
            printf("Updated, tt: %d, cost: %f\n", best_state.travel_time, best_state.cost);
        }
    }
    printf("Ended, tt: %d, cost %f\n", tmp_state.travel_time, tmp_state.cost);
    route.jobs = tmp_jobs;
    if (tmp_state < route.state) {
        route.state = tmp_state;
        return true;
    }
    return false;
}
