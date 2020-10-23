#include <generators.h>
#include <vrp_problem.h>


int main() {
    printf("Generating...\n");
    auto[vec, couriers, storage, matrix] = generate_vrp(100, 10);
    printf("Building...\n");
    VrpTour tour = VrpProblem::init_tour(vec, storage, couriers, matrix);
    tour.improve_tour();
}
