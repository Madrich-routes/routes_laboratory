#include "vrp_inter_operators.h"

bool inter_swap(Route &route1, Route &route2) {
    int size1 = route1.jobs.size();
    int size2 = route2.jobs.size();
    State state1 = route1.state;
    State state2 = route2.state;
    State state = route1.state + route2.state;
    bool changed = true;
    bool result = false;
    printf("Swap started, tt: %d, cost: %f\n", state.travel_time, state.cost);

    while (changed) {
        changed = false;
        State best_state1 = state1;
        State best_state2 = state2;
        State best_state = state;
        int a = -1;
        int b = -1;

        for (std::size_t it1 = 0; it1 < size1; ++it1) {
            for (std::size_t it2 = 0; it2 < size2; ++it2) {
                std::swap(route1.jobs[it1], route2.jobs[it2]);
                std::optional<State> new_state1 = VrpProblem::get_state(route1);
                std::optional<State> new_state2 = VrpProblem::get_state(route2);
                if ((!new_state1) || (!new_state2)) {
                    continue;
                }
                State new_state = new_state1.value() + new_state2.value();
                if (new_state < best_state) {
                    result = changed = true;
                    best_state = new_state;
                    best_state1 = new_state1.value();
                    best_state2 = new_state2.value();
                    a = it1;
                    b = it2;
                }
                std::swap(route1.jobs[it1], route2.jobs[it2]);
            }
        }
        if (changed) {
            state = best_state;
            state1 = best_state1;
            state2 = best_state2;
            std::swap(route1.jobs[a], route2.jobs[b]);
            printf("Updated, tt: %d, cost: %f\n", best_state.travel_time, best_state.cost);
        }
    }
    printf("Ended, tt: %d, cost %f\n", state.travel_time, state.cost);
    if (result) {
        route1.state = state1;
        route2.state = state2;
    }
    return result;
}

bool uns_inter_replace(Route &route1, Route &route2) {
    int size1 = route1.jobs.size();
    int size2 = route2.jobs.size();
    std::vector jobs1 = route1.jobs;
    std::vector jobs2 = route2.jobs;
    State state1 = route1.state;
    State state2 = route2.state;
    State state = route1.state + route2.state;
    bool changed = true;
    bool result = false;

    while (changed) {
        changed = false;
        State best_state1 = state1;
        State best_state2 = state2;
        State best_state = state;
        std::vector best_jobs1 = jobs1;
        std::vector best_jobs2 = jobs2;

        for (std::size_t it1 = 0; it1 < size1; ++it1) {
            for (std::size_t it2 = 0; it2 < size2; ++it2) {
                auto[new_jobs1, new_jobs2] = replace(route1.jobs, route2.jobs, it1, it2);
                route1.jobs = new_jobs1;
                route2.jobs = new_jobs2;
                std::optional<State> new_state1 = VrpProblem::get_state(route1);
                std::optional<State> new_state2 = VrpProblem::get_state(route2);
                if ((!new_state1) || (!new_state2)) {
                    continue;
                }
                State new_state = new_state1.value() + new_state2.value();
                if (new_state < best_state) {
                    result = changed = true;
                    best_state = new_state;
                    best_state1 = new_state1.value();
                    best_state2 = new_state2.value();
                    best_jobs1 = new_jobs1;
                    best_jobs2 = new_jobs2;
                }
                route1.jobs = jobs1;
                route2.jobs = jobs2;
            }
        }
        if (changed) {
            state = best_state;
            state1 = best_state1;
            state2 = best_state2;
            route1.jobs = best_jobs1;
            route2.jobs = best_jobs2;
            printf("Updated, tt: %d, cost: %f\n", best_state.travel_time, best_state.cost);
        }
    }
    if (result) {
        route1.state = state1;
        route2.state = state2;
    }
    return result;
}

bool inter_replace(Route &route1, Route &route2) {
    bool result = false;
    bool changed = true;
    State state = route1.state + route2.state;
    printf("Replace started, tt: %d, cost: %f\n", state.travel_time, state.cost);

    while (changed) {
        bool changed1 = uns_inter_replace(route1, route2);
        bool changed2 = uns_inter_replace(route2, route1);
        changed = changed1 | changed2;
        if (changed) {
            result = changed;
        }
    }

    state = route1.state + route2.state;
    printf("Ended, tt: %d, cost %f\n", state.travel_time, state.cost);
    return result;
}

bool inter_cross(Route &route1, Route &route2) {
    int size1 = route1.jobs.size();
    int size2 = route2.jobs.size();
    std::vector jobs1 = route1.jobs;
    std::vector jobs2 = route2.jobs;
    State state = route1.state + route2.state;
    for (std::size_t it1 = 0; it1 < size1; ++it1) {
        for (std::size_t it2 = it1; it2 < size1; ++it2) {
            for (std::size_t it3 = 0; it3 < size2; ++it3) {
                for (std::size_t it4 = it3; it4 < size2; ++it4) {
                    auto[new_jobs1, new_jobs2] = cross(route1.jobs, route2.jobs, it1, it2, it3, it4);
                    route1.jobs = new_jobs1;
                    route2.jobs = new_jobs2;
                    std::optional<State> new_state1 = VrpProblem::get_state(route1);
                    std::optional<State> new_state2 = VrpProblem::get_state(route2);
                    if ((!new_state1) || (!new_state2)) {
                        continue;
                    }
                    State new_state = new_state1.value() + new_state2.value();
                    if (new_state < state) {
                        route1.state = new_state1.value();
                        route2.state = new_state2.value();
                        return true;
                    }
                    route1.jobs = jobs1;
                    route2.jobs = jobs2;
                }
            }
        }
    }
    return false;
}
