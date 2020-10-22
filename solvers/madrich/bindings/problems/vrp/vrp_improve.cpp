#include "vrp_improve.h"


bool unassigned_insert(VrpTour &tour) {
    printf("\nUnassigned insert started\n");
    std::vector<int> done;
    auto size = tour.storage.unassigned_jobs.size();
    for (std::size_t i = 0; i < size; ++i) {
        Job& job = tour.storage.unassigned_jobs[i];
        if (insert_best(job, tour)) {
            printf("Inserted\n");
            done.push_back(i);
        }
    }
    for (auto &job_index : done) {
        tour.storage.unassigned_jobs.erase(tour.storage.unassigned_jobs.begin() + job_index);
    }
    return !done.empty();
}


bool inter_improve(VrpTour &tour, bool post_cross) {
    bool changed = true;
    bool result = false;
    while (changed) {
        changed = false;
        int size = tour.routes.size();
        for (int i = 0; i < size; ++i) {
            for (int j = i + 1; j < size; ++j) {
                VrpRoute& route1 = tour.routes[i];
                VrpRoute& route2 = tour.routes[j];
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


bool intra_improve(VrpTour &tour, bool post_three_opt) {
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


VrpTour improve_tour(VrpTour &tour, bool post_cross, bool post_three_opt) {
    printf("Improve started\n");
    bool changed = true;

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
