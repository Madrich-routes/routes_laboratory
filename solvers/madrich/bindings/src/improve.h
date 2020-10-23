#ifndef MADRICH_IMPROVE_H
#define MADRICH_IMPROVE_H

#include "problem.h"
#include "utils.h"
#include "insert_job.h"
#include "inter_operators.h"
#include "intra_operators.h"


bool __route_decrease(Tour tour, Problem *problem);

bool __unassigned_insert(Tour tour, Problem *problem);

bool __intra_improve_t(Tour tour, Problem *problem, bool three = true);

bool __inter_improve_c(Tour tour, Problem *problem, bool cross = true);

void statistic(std::vector<int> val);

std::tuple<bool, Tour> improve_tour(Tour tour, Problem *problem, bool cross = false, bool three = false);

#endif //MADRICH_IMPROVE_H
