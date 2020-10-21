#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/complex.h>
#include <pybind11/stl.h>
#include "../vrp/vrp_problem.cpp"

namespace py = pybind11;

PYBIND11_MODULE(Tour, m) {

	py::class_<Window>(m, "Window")
		.def(py::init())
		.def(py::init<std::tuple<int, int>>(), pybind11::arg("w"))
		.def(py::init<const class Window&>(), pybind11::arg("w"))
		.def("print", &Window::print)
		.def("__to_sec", &Window::__to_sec)
		.def("get_seconds", &Window::get_seconds)
		.def_readwrite("window", &Window::window);
	// .def_readwrite("python_window", &Window::python_window);

	py::class_<Point>(m, "Point")
		.def(py::init())
		.def(py::init<std::optional<int>, std::tuple<float, float>, std::optional<std::string>>())
		.def(py::init<const class Point&>(), pybind11::arg("p"))
		.def("print", &Point::print)
		.def_readwrite("matrix_id", &Point::matrix_id)
		.def_readwrite("point", &Point::point)
		.def_readwrite("address", &Point::address);

	py::class_<Cost>(m, "Cost")
		.def(py::init())
		.def(py::init<float, float, float>())
		.def(py::init<const class Cost&>(), pybind11::arg("c"))
		.def("print", &Cost::print)
		.def_readwrite("start", &Cost::start)
		.def_readwrite("second", &Cost::second)
		.def_readwrite("meter", &Cost::meter);

	py::class_<Matrix>(m, "Matrix")
		.def(py::init())
		.def(py::init<std::string, array, array>())
		.def(py::init<const class Matrix&>(), pybind11::arg("m"))
		.def("print", &Matrix::print)
		.def_readwrite("profile", &Matrix::profile)
		.def_readwrite("distance", &Matrix::distance)
		.def_readwrite("travel_time", &Matrix::travel_time);

	py::class_<Storage>(m, "Storage")
		.def(py::init())
		.def(py::init<std::string, int, std::vector<std::string>, Point, Window>())
		.def(py::init<const class Storage&>(), pybind11::arg("s"))
		.def("print", &Storage::print)
		.def_readwrite("name", &Storage::name)
		.def_readwrite("load", &Storage::load)
		.def_readwrite("skills", &Storage::skills)
		.def_readwrite("location", &Storage::location)
		.def_readwrite("work_time", &Storage::work_time);

	py::class_<Job>(m, "Job")
		.def(py::init())
		.def(py::init<std::string, std::optional<Storage>, int, std::vector<int>, std::vector<std::string>, Point, std::vector<Window>>())
		.def(py::init<const class Job&>(), pybind11::arg("j"))
		.def("__eq__", &Job::operator==, py::is_operator())
		.def("print", &Job::print)
		.def_readwrite("job_id", &Job::job_id)
		.def_readwrite("storage", &Job::storage)
		.def_readwrite("delay", &Job::delay)
		.def_readwrite("value", &Job::value)
		.def_readwrite("skills", &Job::skills)
		.def_readwrite("location", &Job::location)
		.def_readwrite("time_windows", &Job::time_windows);

	py::class_<Courier>(m, "Courier")
		.def(py::init())
		.def(py::init<std::string, std::string, Cost, std::vector<int>, std::vector<std::string>, int, Window, Point, Point>())
		.def(py::init<const class Courier&>(), pybind11::arg("c"))
		.def("__eq__", &Courier::operator==, py::is_operator())
		.def("print", &Courier::print)
		.def_readwrite("name", &Courier::name)
		.def_readwrite("profile", &Courier::profile)
		.def_readwrite("cost", &Courier::cost)
		.def_readwrite("value", &Courier::value)
		.def_readwrite("skills", &Courier::skills)
		.def_readwrite("max_distance", &Courier::max_distance)
		.def_readwrite("work_time", &Courier::work_time)
		.def_readwrite("start_location", &Courier::start_location)
		.def_readwrite("end_location", &Courier::end_location);

	py::class_<State>(m, "State")
		.def(py::init())
		.def(py::init<int, int, float, std::optional<std::vector<int>>>())
		.def(py::init<const class State&>(), pybind11::arg("s"))
		.def("__add__", &State::operator+, py::is_operator())
		.def("__iadd__", &State::operator+=, py::is_operator())
		.def("__less__", &State::operator<, py::is_operator())
		.def("print", &State::print)
		// .def("deepcopy", &State::deepcopy)
		// .def("__value", &State::__value)
		.def_readwrite("travel_time", &State::travel_time)
		.def_readwrite("distance", &State::distance)
		.def_readwrite("cost", &State::cost)
		.def_readwrite("value", &State::value);

	py::class_<Route>(m, "Route")
		.def(py::init())
		.def(py::init<Storage, Courier, Matrix, int, std::vector<Job>, int, int, float>())
		.def(py::init<const class Route&>(), pybind11::arg("r"))
		.def("print", &Route::print)
		.def("save_state", &Route::save_state)
		.def("new_route", &Route::new_route)
		.def("len", &Route::len)
		.def_readwrite("storage", &Route::storage)
		.def_readwrite("courier", &Route::courier)
		.def_readwrite("matrix", &Route::matrix)
		.def_readwrite("start_time", &Route::start_time)
		.def_readwrite("jobs", &Route::jobs)
		.def_readwrite("travel_time", &Route::travel_time)
		.def_readwrite("distance", &Route::distance)
		.def_readwrite("cost", &Route::cost);

	py::class_<Tour>(m, "Tour")
		.def(py::init())
		.def(py::init<Storage, std::vector<Route>, std::vector<Job>>())
		.def(py::init<const class Tour&>(), pybind11::arg("t"))
		.def("print", &Tour::print)
		.def("get_state", &Tour::get_state)
		.def("len_jobs", &Tour::len_jobs)
		.def("len", &Tour::len)
		.def_readwrite("storage", &Tour::storage)
		.def_readwrite("routes", &Tour::routes)
		.def_readwrite("unassigned_jobs", &Tour::unassigned_jobs);
		// .def_readwrite("problem", &Tour::problem);

	py::class_<ClassicProblem>(m, "ClassicProblem")
		.def(py::init())
		// не уверен, что правильно работает (работает, но не от абстрактного класса)
		.def("__init", &ClassicProblem::init)
		.def("__get_state", &ClassicProblem::get_state)
		.def("__validate_skills", py::overload_cast<Job, Courier>(&ClassicProblem::__validate_skills))
		.def("__validate_skills", py::overload_cast<Storage, Courier>(&ClassicProblem::__validate_skills))
		.def("__cost", &ClassicProblem::__cost)
		.def("__start", &ClassicProblem::__start)
		.def("__validate_job", &ClassicProblem::__validate_job)
		.def("__go_job", &ClassicProblem::__go_job)
		.def("__validate_storage", &ClassicProblem::__validate_storage)
		.def("__go_storage", &ClassicProblem::__go_storage)
		.def("__next_job", &ClassicProblem::__next_job)
		.def("__end", &ClassicProblem::__end)
		.def("__validate_courier", &ClassicProblem::__validate_courier)
		.def("__greedy_route", &ClassicProblem::__greedy_route)
		.def("__greedy_tour", &ClassicProblem::__greedy_tour);
};
