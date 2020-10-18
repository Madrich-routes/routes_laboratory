#ifndef MADRICH_INSERT_JOB_H
#define MADRICH_INSERT_JOB_H

#include "problem.h"


bool insert_greedy(Job job, std::vector <Route> routes, Problem *problem);

bool insert_best(Job job, std::vector <Route> routes, Problem *problem);

#endif //MADRICH_INSERT_JOB_H
