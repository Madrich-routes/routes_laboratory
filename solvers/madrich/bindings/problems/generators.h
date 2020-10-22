#ifndef MADRICH_SOLVER_GENERATORS_H
#define MADRICH_SOLVER_GENERATORS_H

#include <vector>
#include <random>
#include <map>
#include <cmath>
#include <vrp/vrp_model.h>


float generate_value();

std::tuple<float, float> generate_tuple();

std::vector<std::tuple<float, float>>
generate_points(int n, float min_x = 55.65, float max_x = 55.82, float min_y = 37.45, float max_y = 37.75);

std::vector<std::vector<int>>
generate_matrix(const std::vector<std::tuple<float, float>> &points, const std::string &type);

std::vector<Job>
generate_jobs(const std::vector<Point>& points, int start, int end, const std::string& storage_id);

std::tuple<int, std::vector<Courier>, Storage, std::map<std::string, Matrix>>
generate_vrp(int jobs, int couriers);

#endif //MADRICH_SOLVER_GENERATORS_H
