#include <generators.h>
#include <iostream>
#include <vrp_problem.h>


int main() {
    auto[vec, couriers, storage, matrix] = generate_vrp(20, 5);
    auto tour = VrpProblem::init_tour(vec, storage, couriers, matrix);
    tour.print();
}
