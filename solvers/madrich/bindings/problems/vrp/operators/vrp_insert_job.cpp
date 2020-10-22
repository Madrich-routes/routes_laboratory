#include "vrp_insert_job.h"


std::vector<Job> insert(int place, const Job &job, const std::vector<Job> &jobs) {
    std::vector new_route = std::vector<Job>(jobs.size() + 1);
    for (std::size_t i = 0; i < jobs.size(); ++i) {
        if (i < place) {
            new_route[i] = jobs[i];
        } else if (i == place) {
            new_route[i] = job;
        } else {
            new_route[i + 1] = jobs[i];
        }
    }
    return new_route;
}

bool insert_best(const Job &job, VrpTour &tour) {
    int a = -1;
    int b = -1;
    int best_time = -1;

    for (std::size_t i = 0; i < tour.routes.size(); ++i) {
        VrpRoute& route = tour.routes[i];
        std::vector tmp = route.jobs;
        int old_tt = route.state.travel_time;
        for (std::size_t j = 0; j < route.jobs.size() + 1; ++j) {
            std::vector new_jobs = insert(j, job, route.jobs);
            route.jobs = new_jobs;
            std::optional<State> state = VrpProblem::get_state(route);
            if (!state) {
                route.jobs = tmp;
                continue;
            }
            int new_time = state.value().travel_time - old_tt;
            if ((best_time == -1) || (new_time < best_time)) {
                best_time = new_time;
                a = i;
                b = j;
            }
            route.jobs = tmp;
        }
    }

    if (best_time == -1) {
        printf("Insert negative\n");
        return false;
    }

    VrpRoute& route = tour.routes[a];
    route.jobs = insert(b, job, route.jobs);
    printf("Insert positive\n");
    return true;
}    
