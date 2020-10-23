#include <generators.h>
#include <vrp_problem.h>
#include <vrp/vrp_improve.h>


int main() {
    printf("Generating...\n");
    auto[vec, couriers, storage, matrix] = generate_vrp(400, 5);
    printf("Building...\n");
    auto tour = VrpProblem::init_tour(vec, storage, couriers, matrix);

//    for (auto& route : tour.routes) {
//        VrpProblem::get_state(route);
//    }
    improve_tour(tour);
}