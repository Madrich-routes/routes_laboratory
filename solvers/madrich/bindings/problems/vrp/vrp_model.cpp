#include "vrp/vrp_model.h"

#include <vrp/operators/vrp_insert_job.h>
#include <vrp/operators/vrp_inter_operators.h>
#include <vrp/operators/vrp_intra_operators.h>


/// VrpRoute


VrpRoute::VrpRoute(int vec,
                   int start_time,
                   const Storage &storage,
                   const Courier &courier,
                   const Matrix &matrix,
                   std::vector<Job> jobs,
                   const State &state)
        : vec(vec), storage(storage), courier(courier), matrix(matrix),
          start_time(start_time), jobs(std::move(jobs)), state(state) {}

[[maybe_unused]] void VrpRoute::print() const {
    printf("VrpRoute; courier: %s, jobs: %llu\n", courier.name.c_str(), jobs.size());
}


//// VrpTour


VrpTour::VrpTour(const Storage &storage)
        : storage(storage), routes(std::vector<VrpRoute>()) {}

[[maybe_unused]] void VrpTour::print() const {
    printf("VrpTour; storage: %s\n", storage.name.c_str());
}

bool VrpTour::unassigned_insert() {
    printf("\nUnassigned insert started\n");
    std::vector<int> done;
    auto size = storage.unassigned_jobs.size();
    for (std::size_t i = 0; i < size; ++i) {
        Job &job = storage.unassigned_jobs[i];
        int index = insert_best(job, *this);
        if (index != -1) {
            VrpRoute& route = routes[index];
            mark_route(true, route);
            printf("Inserted\n");
            done.push_back(i);
        }
    }
    for (auto &job_index : done) {
        storage.unassigned_jobs.erase(storage.unassigned_jobs.begin() + job_index);
    }
    return !done.empty();
}

bool VrpTour::inter_improve(bool post_cross) {
    bool result = false;
    int size = routes.size();
    for (int i = 0; i < size; ++i) {
        for (int j = i + 1; j < size; ++j) {
            VrpRoute &route1 = routes[i];
            VrpRoute &route2 = routes[j];
            if (!check_route(route1) and !check_route(route2)) {
                mark_route(false, route1, route2);
                printf("BLOCKED\n");
                continue;
            }

            bool changed = false;
            if (inter_swap(route1, route2)) {
                changed = result = true;
            }
            if (inter_replace(route1, route2)) {
                changed = result = true;
            }
            if (post_cross && !changed && inter_cross(route1, route2)) {
                changed = result = true;
            }
            mark_route(changed, route1, route2);
        }
    }
    return result;
}

bool VrpTour::intra_improve(bool post_three_opt) {
    bool result = false;
    for (auto &route : routes) {
        if (!check_route(route)) {
            mark_route(false, route);
            printf("BLOCKED\n");
            continue;
        }

        bool changed = false;
        bool status = two_opt(route);
        if (!status && post_three_opt) {
            status = three_opt(route);
        }
        if (status) {
            result = changed = true;
        }
        mark_route(changed, route);
    }
    return result;
}

void VrpTour::improve_tour(bool post_cross, bool post_three_opt) {
    printf("Improve started\n");
    bool changed = true;
    check_block();

    while (changed) {
        changed = false;
        if (inter_improve(post_cross)) {
            changed = true;
        }
        if (intra_improve(post_three_opt)) {
            changed = true;
        }
        if (unassigned_insert()) {
            changed = true;
        }
        update_phase();
    }

    printf("Done\n");
    State state = get_state();
    printf("travel time: %d, cost: %f, distance: %d\n", state.travel_time, state.cost, state.distance);
}

State VrpTour::get_state() {
    State state = State();
    for (const auto &route : routes) {
        state += route.state;
    }
    return state;
}

void VrpTour::update_phase() {
    phase += 1;
    previous_phase = current_phase;
    for (const auto &route : current_phase) {
        current_phase[route.first] = false;
    }
}

bool VrpTour::check_route(const VrpRoute &route) {
    return previous_phase[route.courier.name] || current_phase[route.courier.name];
}

void VrpTour::mark_route(bool value, const VrpRoute &route) {
    bool current_state = current_phase[route.courier.name];
    if (!current_state) {
        current_phase[route.courier.name] = value;
    }
}

void VrpTour::mark_route(bool value, const VrpRoute &route1, const VrpRoute &route2) {
    mark_route(value, route1);
    mark_route(value, route2);
}

void VrpTour::check_block() {
    for (const auto& route : routes) {
        if (!current_phase.contains(route.courier.name)) {
            current_phase[route.courier.name] = false;
        }
        if (!previous_phase.contains(route.courier.name)) {
            previous_phase[route.courier.name] = true;
        }
    }
}
