#ifndef MADRICH_INTER_OPERATORS_H
#define MADRICH_INTER_OPERATORS_H

#include "problem.h"
#include "utils.h"

bool __inter_opt(std::tuple<bool, State, Route, Route> (*func)(State best_state,
                                                               Route &route1, Route &route2, Problem *problem),
                 Route &route1, Route &route2, Problem *problem);

std::tuple<bool, State, Route, Route> __inter_cross(State best_state, Route &route1, Route &route2, Problem *problem);

std::tuple<bool, State, Route, Route> __inter_replace(State best_state,
                                                      Route &route1, Route &route2, Problem *problem);

bool __symmetric_function(std::tuple<bool, State, Route, Route> (*func)(State best_state,
                                                                        Route &route1, Route &route2, Problem *problem),
                          Route &route1, Route &route2, Problem *problem);

std::tuple<bool, State, Route, Route> __inter_swap(State best_state, Route &route1, Route &route2, Problem *problem);

bool inter_swap(Route &route1, Route &route2, Problem *problem);

bool inter_replace(Route &route1, Route &route2, Problem *problem);

bool inter_cross(Route &route1, Route &route2, Problem *problem);

#endif //MADRICH_INTER_OPERATORS_H
