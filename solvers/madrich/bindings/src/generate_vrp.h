#ifndef MADRICH_GENERATE_VRP_H
#define MADRICH_GENERATE_VRP_H

#include "problem.h"

#include <stdlib.h>
#include <cmath>


double rand_0_1();

array_d random_sample(int n, int k);

array_d mult(array_d a, vec_d b, int n);

array_d add(array_d a, vec_d b, int n);

void print_array_d(array_d x);

void print_array(array x);

array_d generate_points(int n, double min_x = 55.65, double max_x = 55.82, double min_y = 37.45, double max_y = 37.75);

Storage generate_storage(int n, Point loc, int load = 300);

std::vector <Job> generate_jobs(std::vector <Point> points, std::string storage_id = "", int val = 2, int delay = 300);

std::vector <Courier> generate_couriers(int n, Point start, Point end, int val = 20);

array_d adjacency_matrix(array_d points, int n);

array generate_matrix(array_d points, int n, std::string factor = "travelTime");

std::vector <array> get_matrix(array_d points, int n, std::vector <std::string> factor = {"travelTime"});

class vrp {
public:
    std::vector <Job> jobs;
    std::vector <Courier> couriers;
    Matrix matrix;
    Storage storage;

    void print();
};

vrp generate_vrp(int points, std::string storage_name = "");

#endif //MADRICH_GENERATE_VRP_H
