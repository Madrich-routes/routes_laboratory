#include "inter_operators.h"

bool __inter_opt(std::tuple<bool, State, Route, Route> (*func)(State best_state,
                                                               Route &route1, Route &route2, Problem *problem),
                 Route &route1, Route &route2, Problem *problem) {
    Route tmp_route1 = route1.new_route(route1.jobs);
    Route tmp_route2 = route2.new_route(route2.jobs);
    std::optional <State> st1 = problem->get_state(&tmp_route1);
    std::optional <State> st2 = problem->get_state(&tmp_route2);
    State state;
    if (st1 && st2) {
        state = st1.value() + st2.value();
    }
    State tmp_state = state;
    bool changed = true;
    while (changed) {
        std::tuple<bool, State, Route, Route> f = func(tmp_state, tmp_route1, tmp_route2, problem);
        changed = std::get<0>(f);
        State best_state = std::get<1>(f);
        Route best_route1 = std::get<2>(f);
        Route best_route2 = std::get<3>(f);
        if (changed) {
            tmp_state = best_state;
            tmp_route1 = best_route1;
            tmp_route2 = best_route2;
            std::cout << "Updated, tt:" << best_state.travel_time << ", cost:" << best_state.cost << "\n";
        }
    }

    if (tmp_state < state) {
        route1.jobs = tmp_route1.jobs;
        route2.jobs = tmp_route2.jobs;
        problem->get_state(&route1);
        problem->get_state(&route2);
        return true;
    }
    return false;
}

std::tuple<bool, State, Route, Route> __inter_cross(State best_state, Route &route1, Route &route2, Problem *problem) {
    int size1 = route1.jobs.size();
    int size2 = route2.jobs.size();
    Route best_route1 = route1;
    Route best_route2 = route2;
    for (int it1 = 0; it1 < size1; it1++) {
        for (int it2 = it1; it2 < size1; it2++) {
            for (int it3 = 0; it3 < size2; it3++) {
                for (int it4 = it3; it4 < size2; it4++) {
                    std::tuple <std::vector<Job>, std::vector<Job>> js12 = cross(route1.jobs, route2.jobs, it1, it2,
                                                                                 it3, it4);
                    std::vector <Job> jobs1 = std::get<0>(js12);
                    std::vector <Job> jobs2 = std::get<1>(js12);
                    Route new_route1 = route1.new_route(jobs1);
                    Route new_route2 = route2.new_route(jobs2);
                    std::optional <State> ns1 = problem->get_state(&new_route1);
                    std::optional <State> ns2 = problem->get_state(&new_route2);
                    State new_state;
                    if ((!ns1) || (!ns2)) {
                        continue;
                    } else {
                        new_state = ns1.value() + ns2.value();
                    }
                    if (new_state < best_state) {
                        std::cout << "ggg\n";
                        best_state = new_state;
                        best_route1 = new_route1;
                        best_route2 = new_route2;
                        return std::make_tuple(true, best_state, best_route1, best_route2);
                    }
                }
    		}
    	}
    }
    return std::make_tuple(false, best_state, best_route1, best_route2);
}

std::tuple<bool, State, Route, Route> __inter_replace(State best_state, Route& route1, Route& route2, Problem* problem)
{
    int size1 = route1.jobs.size(); 
    int size2 = route2.jobs.size();
    Route best_route1 = route1; 
    Route best_route2 = route2;
    bool changed = false;
    for (int it1 = 0; it1 < size1; it1++)
        for (int it2 = 0; it2 < size2; it2++) {
            std::tuple <std::vector<Job>, std::vector<Job>> js12 = replace(route1.jobs, route2.jobs, it1, it2);
            std::vector <Job> jobs1 = std::get<0>(js12);
            std::vector <Job> jobs2 = std::get<1>(js12);
            Route new_route1 = route1.new_route(jobs1);
            Route new_route2 = route2.new_route(jobs2);
            std::optional <State> ns1 = problem->get_state(&new_route1);
            std::optional <State> ns2 = problem->get_state(&new_route2);
            State new_state;
            if ((!ns1) || (!ns2)) {
                continue;
            } else {
                new_state = ns1.value() + ns2.value();
            }

            if (new_state < best_state) {
                changed = true;
                best_state = new_state;
                best_route1 = new_route1;
                best_route2 = new_route2;
                return std::make_tuple(true, best_state, best_route1, best_route2);
            }
        }
    return std::make_tuple(changed, best_state, best_route1, best_route2);
}

bool __symmetric_function(std::tuple<bool, State, Route, Route> (*func)(State best_state,
                                                                        Route &route1, Route &route2, Problem *problem),
                          Route &route1, Route &route2, Problem *problem) {
    Route tmp_route1 = route1.new_route(route1.jobs);
    Route tmp_route2 = route2.new_route(route2.jobs);
    bool changed = true;
    while (changed) {
        changed = __inter_opt(func, tmp_route1, tmp_route2, problem);
        if (changed) {
            continue;
        }
        changed = __inter_opt(func, tmp_route2, tmp_route1, problem);
    }
    std::optional <State> s1 = problem->get_state(&route1);
    std::optional <State> s2 = problem->get_state(&route2);
    std::optional <State> ts1 = problem->get_state(&tmp_route1);
    std::optional <State> ts2 = problem->get_state(&tmp_route2);
    State state;
    State tmp_state;
    if (s1 && s2) {
        state = s1.value() + s2.value();
    }
    if (ts1 && ts2) {
        tmp_state = ts1.value() + ts2.value();
    }
    std::cout << "Ended, tt:" << tmp_state.travel_time << "\n";
    if (tmp_state < state) {
        std::cout << "updated\n";
        route1.jobs = tmp_route1.jobs;
        route2.jobs = tmp_route2.jobs;
        problem->get_state(&route1);
        problem->get_state(&route2);
        return true;
    }
    return false;
}

std::tuple<bool, State, Route, Route> __inter_swap(State best_state, Route& route1, Route& route2, Problem* problem)
{
    int size1 = route1.jobs.size(); 
    int size2 = route2.jobs.size();
    Route best_route1 = route1;
    Route best_route2 = route2;
    bool changed = false;
    for (int it1 = 0; it1 < size1; it1++)
        for (int it2 = 0; it2 < size2; it2++) {
            std::vector <Job> jobs1;
            std::vector <Job> jobs2;
            for (auto i : route1.jobs)
                jobs1.push_back(Job(i));
            for (auto i : route2.jobs)
                jobs2.push_back(Job(i));
            Job f = jobs1[it1];
            jobs1[it1] = jobs2[it2];
            jobs2[it2] = f;
            Route new_route1 = route1.new_route(jobs1);
            Route new_route2 = route2.new_route(jobs2);
            std::optional <State> ns1 = problem->get_state(&new_route1);
            std::optional <State> ns2 = problem->get_state(&new_route2);
            State new_state;
            if ((!ns1) || (!ns2)) {
                continue;
            } else {
                new_state = ns1.value() + ns2.value();
            }

            if (new_state < best_state) {
                changed = true;
                best_state = new_state;
                best_route1 = new_route1;
                best_route2 = new_route2;
                return std::make_tuple(true, best_state, best_route1, best_route2);
            }
        }
    return std::make_tuple(changed, best_state, best_route1, best_route2);
}

bool inter_swap(Route& route1, Route& route2, Problem* problem)
{
    std::cout << "Swap started, tt:" << route1.travel_time + route2.travel_time << "\n";
    bool ret = __inter_opt(&__inter_swap, route1, route2, problem);
    std::cout << "Ended, tt:" << route1.travel_time + route2.travel_time << "\n";
    return ret;
}

bool inter_replace(Route& route1, Route& route2, Problem* problem)
{
    std::cout << "Replace started, tt:" <<route1.travel_time + route2.travel_time << "\n";
    return __symmetric_function(&__inter_replace, route1, route2, problem);
}

bool inter_cross(Route& route1, Route& route2, Problem* problem)
{
    std::cout << "Cross started, tt:" << route1.travel_time + route2.travel_time << "\n";
    return __symmetric_function(&__inter_cross, route1, route2, problem);
}




 
