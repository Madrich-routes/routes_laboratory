#include "vrp_improve.h"

bool unassigned_insert(Tour &tour) {
    printf("Unassigned insert started\n");
    std::vector<Job> done;
    for (auto &job : tour.storage.unassigned_jobs) {
        if (insert_best(job, tour)) {
            printf("Inserted\n");
            done.push_back(job);
        }
    }
    for (auto &job : done) {
        tour.storage.unassigned_jobs.erase(
                std::remove(tour.storage.unassigned_jobs.begin(), tour.storage.unassigned_jobs.end(), job),
                tour.storage.unassigned_jobs.end()
        );
    }
    return !done.empty();
}

bool inter_improve(Tour &tour, bool post_cross) {
    bool changed = true;
    bool result = false;
    while (changed) {
        changed = false;
        int size = tour.routes.size();
        for (int i = 0; i < size; ++i) {
            for (int j = i + 1; j < size; ++j) {
                Route route1 = tour.routes[i];
                Route route2 = tour.routes[j];
                if (inter_swap(route1, route2)) {
                    changed = result = true;
                }
                if (inter_replace(route1, route2)) {
                    changed = result = true;
                }
                if (post_cross && !changed && inter_cross(route1, route2)) {
                    changed = result = true;
                }
            }
        }
    }
    return result;
}

bool intra_improve(Tour &tour, bool post_three_opt) {
    bool changed = false;
    for (auto &route : tour.routes) {
        bool status = two_opt(route);
        if (!status && post_three_opt) {
            status = three_opt(route);
        }
        if (status) {
            changed = true;
        }
    }
    return changed;
}

Tour improve_tour(Tour &tour, bool post_cross, bool post_three_opt) {
    printf("Improve started\n");
    bool changed = true;
    std::vector<int> stat;

    while (changed) {
        changed = false;
        if (inter_improve(tour, post_cross)) {
            changed = true;
        }
        if (intra_improve(tour, post_three_opt)) {
            changed = true;
        }
        if (unassigned_insert(tour)) {
            changed = true;
        }

    }
    printf("Done\n");
    State state = tour.get_state();
    printf("travel time: %d, cost: %f, distance: %d\n", state.travel_time, state.cost, state.distance);
    return tour;
}
