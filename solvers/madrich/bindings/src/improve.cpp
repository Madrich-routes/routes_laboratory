#include "improve.h"

bool __route_decrease(Tour tour, Problem *problem) {
    std::cout << "Route decrease started, routes:" << tour.len() << "\n";
    int idx = -1;
    int size = -1;
    int i = 0;
    for (auto route : tour.routes) {
        if ((size == -1) || (size > route.travel_time)) {
            idx = i;
            size = route.travel_time;
        }
        i++;
    }
    if (idx == -1) {
        return false;
    }
    Route route = tour.routes[idx];
    tour.routes.erase(tour.routes.begin() + idx);
    std::vector <Job> removal_jobs = route.jobs;
    std::vector <Route> in_routes;
    for (auto i : tour.routes) {
        in_routes.push_back(Route(i));
    }
    bool els = true;
    for (auto job : removal_jobs) {
        if (!insert_best(job, in_routes, problem)) {
            els = false;
            break;
        }
    }
    if (els) {
        tour.routes = in_routes;
        std::cout << "Decrease positive, routes:" << tour.len() << "\n";
        return true;
    }
    tour.routes.push_back(route);
    std::cout << "Decrease negative, routes: " << tour.len() << "\n";
    return false;
}

bool __unassigned_insert(Tour tour, Problem *problem) {
    std::cout << "Unassigned insert started, routes:" << tour.len() << "\n";
    std::vector <Job> done;
    for (auto job : tour.unassigned_jobs) {
        if (insert_best(job, tour.routes, problem)) {
            std::cout << "Inserted\n";
            done.push_back(job);
        }
    }
    for (auto job : done) {
        tour.unassigned_jobs.erase(std::remove(tour.unassigned_jobs.begin(), tour.unassigned_jobs.end(), job),
                                   tour.unassigned_jobs.end());
    }
    return done.size() > 0;
}

bool __intra_improve_t(Tour tour, Problem* problem, bool three)
{
    State state = tour.get_state();
    for (auto route : tour.routes) {
        two_opt(route, problem);
        if (three) {
            three_opt(route, problem);
        }
    }
    return tour.get_state() < state;
}

bool __inter_improve_c(Tour tour, Problem* problem, bool cross)
{
    bool changed = true; 
    bool result = false;
    while (changed) {
        changed = false;
        int size = tour.len();
        for (int i = 0; i < size; i++) {
            for (int j = i + 1; j < size; j++) {
                if (inter_swap(tour.routes[i], tour.routes[j], problem)) {
                    changed = true;
                    result = true;
                }
                if (inter_replace(tour.routes[i], tour.routes[j], problem)) {
                    changed = true;
                    result = true;
                }
                if (cross) {
                    if (inter_cross(tour.routes[i], tour.routes[j], problem)) {
                        changed = true;
                        result = true;
                    }
                }
            }
        }
	}
    return result;
}


void statistic(std::vector<int> val)
{
	int sum = 0;
	for (auto i : val)
	{
		sum += i;
		std::cout << i << " ";
	}
	std::cout << ", sum=" << sum << "\n";
}

std::tuple<bool, Tour> improve_tour(Tour tour, Problem* problem, bool cross, bool three)
{
	std::cout << "Improving...\n";
    std::cout << "Improve started\n";
    bool changed = true;
    bool result = true;
    std::vector<int> stat;
    while (changed) {
        changed = false;
        std::cout << "Routes: ";
        stat.clear();
        for (auto i : tour.routes) {
            stat.push_back(i.len());
        }
        statistic(stat);
        std::cout << "Travel time: ";
        stat.clear();
        for (auto i : tour.routes) {
            stat.push_back(i.travel_time);
        }
        statistic(stat);
        std::cout << "Start improve cross\n";
        if (__inter_improve_c(tour, problem, cross)) {
            std::cout << "End success!\n";
            changed = true;
            result = true;
        }
        std::cout << "Start improve three\n";
        if (__intra_improve_t(tour, problem, three)) {
            std::cout << "End success!\n";
            changed = true;
            result = true;
        }
        std::cout << "Start improve insert\n";
        if (__unassigned_insert(tour, problem)) {
            std::cout << "End success!\n";
            changed = true;
            result = true;
        }
        std::cout << "Start improve decrease\n";
        if (__route_decrease(tour, problem)) {
            std::cout << "End success!\n";
            changed = true;
            result = true;
        }
    }
    std::cout << "Done\n";
    std::cout << "Routes: ";
    stat.clear();
    for (auto i : tour.routes) {
        stat.push_back(i.len());
    }
    statistic(stat);
    std::cout << "Travel time: ";
    stat.clear();
    for (auto i : tour.routes) {
        stat.push_back(i.travel_time);
    }
    statistic(stat);
    return std::make_tuple(result, tour);
}















