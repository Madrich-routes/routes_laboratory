#include "generate_vrp.h"


double rand_0_1()
{
	double d = rand();
	double r = d / (RAND_MAX + 1.0);
    return r;
}

array_d random_sample(int n, int k) {
    array_d ret;
    for (int i = 0; i < n; i++) {
        vec_d f;
        for (int j = 0; j < k; j++) {
            f.push_back(rand_0_1());
        }
        ret.push_back(f);
    }
    return ret;
}

array_d mult(array_d a, vec_d b, int n)
{
	array_d ret;
	for (int i = 0; i < n; i++)
	{
		vec_d f;
		f.push_back(a[i][0] * b[0]);
		f.push_back(a[i][1] * b[1]);
		ret.push_back(f);
	}
	return ret;
}

array_d add(array_d a, vec_d b, int n)
{
	array_d ret;
	for (int i = 0; i < n; i++)
	{
		vec_d f;
		f.push_back(a[i][0] + b[0]);
		f.push_back(a[i][1] + b[1]);
		ret.push_back(f);
	}
	return ret;
}

void print_array_d(array_d x)
{
	for (auto i : x)
	{
		for (auto j : i)
			std::cout << j << " ";
		std::cout << "\n";
	}
}

void print_array(array x)
{
	for (auto i : x)
	{
		for (auto j : i)
			std::cout << j << " ";
		std::cout << "\n";
	}
}

array_d generate_points(int n, double min_x, double max_x, double min_y, double max_y) {
    double diff_x = max_x - min_x;
    double diff_y = max_y - min_y;
    vec_d dff = {diff_x, diff_y};
    array_d rnd = random_sample(n, 2);
    array_d mlt = mult(rnd, dff, n);
    vec_d minn = {min_x, min_y};
    array_d ad = add(mlt, minn, n);
    return ad;
}

Storage generate_storage(int n, Point loc, int load) {
    Window w = {std::make_tuple(0, 20 * 60 * 60)};
    std::vector <std::string> skills = {"brains"};
    Storage storage = {"storage_" + std::to_string(n), load, skills, loc, w};
    return storage;
}

std::vector <Job> generate_jobs(std::vector <Point> points, std::string storage_id, int val, int delay) {
    std::vector <Job> jobs;
    int i = 0;
    for (auto point : points) {
        std::string job_id = storage_id + "_job_" + std::to_string(i);
        vec_i value = {val, val};
        std::vector <std::string> skills = {"brains"};
        Window w = {std::make_tuple((10 + i % 4) * 60 * 60, (12 + i % 5) * 60 * 60)};
        std::vector <Window> tw = {w};
        std::optional <Storage> s;
        Job j = {job_id, s, delay, value, skills, point, tw};
        jobs.push_back(j);
        i++;
    }
    return jobs;
}

std::vector<Courier> generate_couriers(int n, Point start, Point end, int val)
{
    std::vector<Courier> couriers;
    for (int i = 0; i < n; i++) {
        std::string name = "courier_" + std::to_string(i);
        Cost cost = {10., 0.5, 1.2};
        vec_i value = {val, val};
        std::vector <std::string> skills = {"brains"};
        int max_distance = 100000;
        Window w = {std::make_tuple(10 * 60 * 60, 20 * 60 * 60)};
        Courier courier = {name, "driver", cost, value, skills, max_distance, w, start, end};
        couriers.push_back(courier);
    }
    return couriers;
}

array_d adjacency_matrix(array_d points, int n) {
    // Матрица смежности 
    array_d matrix;
    for (int i = 0; i < n; i++) {
        vec_d f;
        for (int j = 0; j < n; j++) {
            f.push_back(0);
        }
        matrix.push_back(f);
    }
    for (int idx = 0; idx < n; idx++) {
        for (int idy = idx + 1; idy < n; idy++) {
            double distance = sqrt(
                    pow((points[idy][0] - points[idx][0]), 2) + pow((points[idy][1] - points[idx][1]), 2));
            matrix[idx][idy] = distance;
            matrix[idy][idx] = distance;
        }
    }
    return matrix;
}


array generate_matrix(array_d points, int n, std::string factor) {
    array_d adj = adjacency_matrix(points, n);
    array_d matrix;
    for (auto i : adj) {
        vec_d f;
        for (auto j : i) {
            f.push_back(j * 10000);
        }
        matrix.push_back(f);
    }
    array_d rnd = random_sample(n, n);
    array ret;
    for (int i = 0; i < n; i++) {
        vec_i in;
        for (int j = 0; j < n; j++) {
            double p = (rnd[i][j] * matrix[i][j] / 2 + matrix[i][j]) * coefficient[factor];
            in.push_back(p);
        }
        ret.push_back(in);
    }
    return ret;
}


std::vector <array> get_matrix(array_d points, int n, std::vector <std::string> factor) {
    /* Возвращает ассиметричные матрицы смежности
    :param factor:
    :param points: точки
    :return: матрица, одна, фиговая
    */

    std::vector <array> output;
    for (auto f : factor) {
        array g = generate_matrix(points, n, f);
        output.push_back(g);
    }
    return output;
}

void vrp::print() {
    std::cout << "-------\n";
    std::cout << "vrp:\n";
    for (auto i : jobs) {
        i.print();
    }
    std::cout << "\n";
    for (auto i : couriers) {
        i.print();
    }
    std::cout << "\n";
    matrix.print();
    storage.print();
    std::cout << "-------\n";
}

vrp generate_vrp(int points, std::string storage_name) {
    array_d pts_array = generate_points(points + 1, 55.7, 55.8, 37.6, 37.7);
    std::vector <Point> pts;
    int id = 0;
    for (auto i : pts_array) {
        std::optional<int> k = id;
        id++;
        std::optional <std::string> s;
        Point p = {k, std::make_tuple(i[0], i[1]), s};
        pts.push_back(p);
    }
    std::vector <Point> pts1 = std::vector<Point>(pts.begin() + 1, pts.end());
    Storage storage = generate_storage(0, pts[0]);
    std::vector <Job> jobs = generate_jobs(pts1, "storage_name");
    std::vector <Courier> couriers = generate_couriers(5, pts[0], pts[0]);
    std::vector <std::string> factor = {"distance", "travelTime"};
    std::vector <array> dt = get_matrix(pts_array, points + 1, factor);
    array distance = dt[0];
    array travel_time = dt[1];
    Matrix matrix = {"driver", distance, travel_time};

    vrp v = {jobs, couriers, matrix, storage};
    return v;
}






