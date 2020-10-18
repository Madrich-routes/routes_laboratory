#ifndef MADRICH_UTILS_H
#define MADRICH_UTILS_H

#include "problem.h"


std::vector <Job> swap(std::vector <Job> rt, int x, int y);

std::vector <Job> three_opt_exchange(std::vector <Job> rt, int best_exchange, std::tuple<int, int, int> nodes);

std::tuple <std::vector<Job>, std::vector<Job>> cross(std::vector <Job> route1, std::vector <Job> route2,
                                                      int it1, int it2, int it3, int it4);

std::tuple <std::vector<Job>, std::vector<Job>> replace(std::vector <Job> route1, std::vector <Job> route2,
                                                        int it1, int it2);

#endif //MADRICH_UTILS_H
