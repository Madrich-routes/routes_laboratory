#include "insert_job.h"

bool insert_greedy(Job job, std::vector <Route> routes, Problem *problem) {
    std::cout << "Greedy insert started\n";
    for (auto route :routes) {
        for (int i = 0; i < route.len() + 1; i++) {
            std::vector <Job> jobs;
            for (int j = 0; j < i; j++) {
                jobs.push_back(route.jobs[j]);
            }
            jobs.push_back(job);
            for (int j = i; j < route.jobs.size(); j++) {
                jobs.push_back(route.jobs[j]);
            }
            Route nr = route.new_route(jobs);
            std::optional <State> state = problem->get_state(&nr);
            if (!state) {
                continue;
            }
            route.jobs = jobs;
            std::cout << "Greedy insert positive";
            return true;
        }
    }
    std::cout << "Greedy insert negative\n";
    return false;
}

bool insert_best(Job job, std::vector<Route> routes, Problem* problem)
{
    std::cout << "Insert started\n";
    std::tuple<int, int> best_insert = {-1, -1};
    int best_time = -1;
	int i = 0;
    for (auto route : routes) {
        int old_tt = route.travel_time;
        for (int j = 0; j < route.len() + 1; j++) {
            std::vector <Job> jobs;
            for (int k = 0; k < j; k++) {
                jobs.push_back(route.jobs[k]);
            }
            jobs.push_back(job);
            for (int k = j; k < route.jobs.size(); k++) {
                jobs.push_back(route.jobs[k]);
            }
            Route nr = route.new_route(jobs);
            std::optional <State> state = problem->get_state(&nr);
            if (!state) {
                continue;
            }
            int new_time = state.value().travel_time - old_tt;
            if ((best_time == -1) || (new_time < best_time)) {
                best_time = new_time;
                best_insert = std::make_tuple(i, j);
            }
        }
        i++;
    }
    if (std::get<0>(best_insert) == -1) {
        std::cout << "Insert negative\n";
        return false;
    }
    i = std::get<0>(best_insert);
    int j = std::get<1>(best_insert);
    Route route = routes[i];
    int sz = route.jobs.size();
    route.jobs.clear();
    for (int k = 0; k < j; k++) {
        route.jobs.push_back(route.jobs[k]);
    }
    route.jobs.push_back(job);
    for (int k = j; k < sz; k++) {
        route.jobs.push_back(route.jobs[k]);
    }
    std::cout << "Insert positive\n";
    return true;
}    
    
    
    
    
