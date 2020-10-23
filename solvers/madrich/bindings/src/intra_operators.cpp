#include "intra_operators.h"

bool three_opt(Route &route, Problem *problem) {
    Route tmp_route = route.new_route(route.jobs);
    std::optional <State> st = problem->get_state(&tmp_route);
    State state;
    if (st) {
        state = st.value();
    }
    State tmp_state = state;
    int size = tmp_route.jobs.size();
    bool changed = true;

    std::cout << "Three opt started, tt:" << state.travel_time << ", cost:" << state.cost << "\n";
    while (changed) {
        changed = false;
        State best_state = tmp_state;
        Route best_route = tmp_route;

        for (int it1 = 0; it1 < size; it1++) {
            for (int it3 = it1 + 1; it3 < size; it3++) {
                for (int it5 = it3 + 1; it5 < size; it5++) {
                    for (int i = 0; i < 7; i++) {
                        std::vector <Job> path = three_opt_exchange(tmp_route.jobs, i, std::make_tuple(it1, it3, it5));
                        Route new_route = tmp_route.new_route(path);
                        std::optional <State> ns = problem->get_state(&new_route);
                        State new_state;
                        if (!ns) {
                            continue;
                        } else {
                            new_state = ns.value();
                        }

                        if (new_state < best_state) {
                            changed = true;
                            best_state = new_state;
                            best_route = new_route;
                        }
                    }
                }
            }
        }
        if (changed) {
            tmp_state = best_state;
            tmp_route = best_route;
            std::cout << "Updated, tt:" << best_state.travel_time << ", cost:" << best_state.cost << "\n";
        }
    }
    std::cout << "Ended, tt:" << tmp_state.travel_time << ", cost:" << tmp_state.cost << "\n";
    if (tmp_state < state) {
        route.jobs = tmp_route.jobs;
        return true;
    }
    return false;
}

bool two_opt(Route &route, Problem *problem) {
    Route tmp_route = route.new_route(route.jobs);
    std::optional <State> st = problem->get_state(&tmp_route);
    State state;
    if (st) {
        state = st.value();
    }
    State tmp_state = state;
    int size = tmp_route.jobs.size();
    bool changed = true;

    std::cout << "Two opt started, tt:" << state.travel_time << ", cost:" << state.cost << "\n";
    while (changed) {
        changed = false;
        State best_state = tmp_state;
        Route best_route = tmp_route;

        for (int it1 = 0; it1 < size; it1++) {
            for (int it3 = it1 + 1; it3 < size; it3++) {
                std::vector <Job> path = swap(tmp_route.jobs, it1, it3);
                Route new_route = tmp_route.new_route(path);
                std::optional <State> ns = problem->get_state(&new_route);
                State new_state;
                if (!ns) {
                    continue;
                } else {
                    new_state = ns.value();
                }

                if (new_state < best_state) {
                    changed = true;
                    best_state = new_state;
                    best_route = new_route;
                }
            }
        }

        if (changed) {
            tmp_state = best_state;
            tmp_route = best_route;
            std::cout << "Updated, tt:" << best_state.travel_time << ", cost:" << best_state.cost << "\n";
        }
    }
    std::cout << "Ended, tt:" << tmp_state.travel_time << ", cost:" << tmp_state.cost << "\n";
    if (tmp_state < state) {
        route.jobs = tmp_route.jobs;
        problem->get_state(&route);
        return true;
    }
    return false;
}