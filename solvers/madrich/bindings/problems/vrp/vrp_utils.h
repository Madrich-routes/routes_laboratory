#ifndef MADRICH_SOLVER_VRP_UTILS_H
#define MADRICH_SOLVER_VRP_UTILS_H

#include <stdexcept>

#include "vrp_model.h"


std::vector<Job>
swap(const std::vector<Job> &rt, int x, int y);

std::vector<Job>
three_opt_exchange(const std::vector<Job> &rt, int best_exchange, int x, int y, int z);

std::tuple<std::vector<Job>, std::vector<Job>>
cross(const std::vector<Job> &route1, const std::vector<Job> &route2, int it1, int it2, int it3, int it4);

std::tuple<std::vector<Job>, std::vector<Job>>
replace(const std::vector<Job> &route1, const std::vector<Job> &route2, int it1, int it2);

#endif //MADRICH_SOLVER_VRP_UTILS_H
