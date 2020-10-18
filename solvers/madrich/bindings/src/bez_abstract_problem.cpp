#pragma once

#include <vector>
#include <string>
#include <map>
#include <algorithm>

#include <iostream>

namespace py = pybind11;
typedef std::vector< std::vector<int> > array;

////////////////////////////////////////////////////////////////////////////////////////////////// optional
/*template<class T>
class optional
{
    public:
        bool is_none;
        T v;
        
        optional<T>()
        {
            is_none = true;
        }
        
        optional<T>(T vv)
        {
            is_none = false;
            v = vv;
        }
        
        T value()
        {
            return v;
        }
        
        optional<T> operator=(T& other)
        {
            v = other;
            is_none = false;
            return *this;
        }
        
        operator bool() {
            return !is_none;
        }
};*/
////////////////////////////////////////////////////////////////////////////////////////////////// window
class Window 
{
    public:
        std::tuple<int, int> window;
        //std::tuple<std::string, std::string> python_window;
        
		Window(){}
		
		Window(std::tuple<int, int> w)
		{
			window = w;
		}
		
        void print()
        {
            std::cout << "-------\n";
            std::cout << "Window:\n";
            std::cout << std::get<0>(window) << " " << std::get<1>(window) << "\n";
            std::cout << "-------\n";
        }
        
        Window(const Window& w)
        {
        	window = std::make_tuple(std::get<0>(w.window), std::get<1>(w.window));
		}
        
        /*
        static int __to_sec_python(std::string t)
        {
            return 0; //int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp());
        }
        */
        static int __to_sec(int t) // получаем изначально секунды
        {
            return t;
        }

        std::tuple<int, int> get_seconds()
        {
            return std::make_tuple(Window::__to_sec(std::get<0>(window)), Window::__to_sec(std::get<1>(window)));
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// Point
class Point
{
    public:
        std::optional<int> matrix_id; 
        std::tuple<float, float> point;
        std::optional<std::string> address;
        
        Point(){}
        
        Point(
        	std::optional<int> mi, 
        	std::tuple<float, float> p, 
        	std::optional<std::string> a)
        {
        	matrix_id = mi;
        	point = p;
        	address = a;
        }
        
        void print()
        {
            std::cout << "-------\n";
            std::cout << "Point:\n";
            if (matrix_id)
                std::cout << matrix_id.value() << "\n";
            std::cout << std::get<0>(point) << " " << std::get<1>(point) << "\n";
            if (address)
                std::cout << address.value() << "\n";
            std::cout << "-------\n";
        }
        
        Point(const Point& p)
        {
        	if (p.matrix_id)
        		matrix_id = p.matrix_id.value();
        	point = std::make_tuple(std::get<0>(p.point), std::get<1>(p.point));
        	if (p.address)
        		address = p.address.value();
		}
};
////////////////////////////////////////////////////////////////////////////////////////////////// Cost
class Cost 
{
    public:
        float start;
        float second;
        float meter;
        
        Cost(){}
        
        Cost(
        	float st,
        	float s,
        	float m)
        {
        	start = st;
        	second = s;
        	meter = m;
		}
        
        void print()
        {
            std::cout << "-------\n";
            std::cout << "Cost:\n";
            std::cout << start << "\n";
            std::cout << second << "\n";
            std::cout << meter << "\n";
            std::cout << "-------\n";
        }
        
        Cost(const Cost& c)
        {
        	start = c.start;
        	second = c.second;
        	meter = c.meter;
		}
};
////////////////////////////////////////////////////////////////////////////////////////////////// Matrix
class Matrix  
{
    public:
        std::string profile;
        array distance;
        array travel_time;
        
        Matrix(){}
        
        Matrix(
        	std::string p,
        	array d,
        	array tt)
        {
        	profile = p;
        	distance = d;
        	travel_time = tt;
		}
        
        void print()
        {
            std::cout << "-------\n";
            std::cout << "Matrix:\n";
            std::cout << profile << "\n";
            for (auto i : distance)
            {
                for (auto j : i)
                    std::cout << j << " ";
                std::cout << "\n";
            }
            std::cout << "\n";
            for (auto i : travel_time)
            {
                for (auto j : i)
                    std::cout << j << " ";
                std::cout << "\n";
            }
            std::cout << "-------\n";
        }
        
        Matrix(const Matrix& m)
        {
        	for (auto i : m.distance)
        	{
        		std::vector<int> k;
        		for (auto j : i)
        			k.push_back(j);
        		distance.push_back(k);
        	}
        	for (auto i : m.travel_time)
        	{
        		std::vector<int> k;
        		for (auto j : i)
        			k.push_back(j);
        		travel_time.push_back(k);
        	}
        	profile = m.profile;
		}
};
////////////////////////////////////////////////////////////////////////////////////////////////// Storage
class Storage  
{
    public:
        std::string name;
        int load;
        std::vector<std::string> skills;
        Point location;
        Window work_time;
        
        Storage(){}
        
        Storage(
        	std::string n,
        	int l,
        	std::vector<std::string> ss,
        	Point ln,
        	Window wt)
        {
		    name = n;
		    load = l;
		    skills = ss;
		    location = ln;
		    work_time = wt;
        }
        
        void print()
        {
            std::cout << "-------\n";
            std::cout << "Storage:\n";
            std::cout << name << "\n";
            std::cout << load << "\n";
            for (auto i : skills)
            	std::cout << i << " ";
          	std::cout << "\n";
          	location.print();
          	work_time.print();
            std::cout << "-------\n";
        } 
        
        Storage(const Storage& s)
        {
        	name = s.name;
        	load = s.load;
			for (auto i : s.skills)
				skills.push_back(i);
			location = Point(s.location);
			work_time = Window(s.work_time);
		}	
};
////////////////////////////////////////////////////////////////////////////////////////////////// Job
class Job  
{
    public:
        std::string job_id;  // unique
        std::optional<Storage> storage;
        int delay;
        std::vector<int> value;
        std::vector<std::string> skills;
        Point location;  // not unique
        std::vector<Window> time_windows;
        
        Job(){}
        
        Job(
        	std::string ji,
        	std::optional<Storage> s,
        	int d,
        	std::vector<int> v,
        	std::vector<std::string> ss,
        	Point l,
        	std::vector<Window> tw)
        {
        	job_id = ji;
        	storage = s;
        	delay = d;
        	value = v;
        	skills = ss;
        	location = l;
        	time_windows = tw;
		}
        
        void print()
        {
            std::cout << "-------\n";
        	std::cout << "Job:\n";
        	std::cout << job_id << "\n";
        	if (storage)
        		storage.value().print();
        	std::cout << delay << "\n";
        	for (auto i : value)
        		std::cout << i << " ";
        	std::cout << "\n";
        	for (auto i : skills)
        		std::cout << i << " ";
        	std::cout << "\n";
        	location.print();
        	for (auto i : time_windows)
        		i.print();
        	std::cout << "\n";
            std::cout << "-------\n";
		}
		
		Job(const Job& j)
		{
			job_id = j.job_id;
			if (j.storage)
				storage = Storage(j.storage.value());
			delay = j.delay;
			for (auto i : j.value)
				value.push_back(i);
			for (auto i : j.skills)
				skills.push_back(i);
			location = Point(j.location);
			for (auto i : j.time_windows)
				time_windows.push_back(Window(i));
		}
		
        bool operator==(const Job& other)
        {
            return other.job_id == job_id;
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// Courier
class Courier  
{
    public:
        std::string name;
        std::string profile;
        Cost cost;
        std::vector<int> value;
        std::vector<std::string> skills;
        int max_distance;
        Window work_time;
        Point start_location;
        Point end_location;
        
        Courier(){}
        
        Courier(
        	std::string n,
        	std::string p,
        	Cost c,
        	std::vector<int> v,
        	std::vector<std::string> ss,
        	int md,
        	Window wt,
        	Point sl,
        	Point el)
        {
        	name = n;
        	profile = p;
        	cost = c;
        	value = v;
        	skills = ss;
        	max_distance = md;
        	work_time = wt;
        	start_location = sl;
        	end_location = el;
		}
        
        void print()
        {
            std::cout << "-------\n";
        	std::cout << "Courier:\n";
        	std::cout << name << "\n";
        	std::cout << profile << "\n";
        	cost.print();
        	for (auto i : value)
        		std::cout << i << " ";
        	std::cout << "\n";
        	for (auto i : skills)
        		std::cout << i << " ";
        	std::cout << "\n";
        	std::cout << max_distance << "\n";
        	work_time.print();
        	start_location.print();
        	end_location.print();
            std::cout << "-------\n";
		}
		
		Courier(const Courier& c)
		{
			name = c.name;
			profile = c.profile;
			cost = Cost(c.cost);
			for (auto i : c.value)
				value.push_back(i);
			for (auto i : c.skills)
				skills.push_back(i);
			max_distance = c.max_distance;
			work_time = Window(c.work_time);
			start_location = Point(c.start_location);
			end_location = Point(c.end_location);
		}
		
        bool operator==(const Courier& other)
        {
            return other.name == name;
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// State
class State 
{
    public:
        int travel_time;
        int distance;
        float cost;
        std::optional< std::vector<int> > value;
		
		State(){}
		
		State(
			int tt,
			int d,
			float c,
			std::optional< std::vector<int> > v)
		{
			travel_time = tt;
			distance = d;
			cost = c;
			value = v;
		}
		
		void print()
		{
            std::cout << "-------\n";
        	std::cout << "State:\n";
        	std::cout << travel_time << "\n";
        	std::cout << distance << "\n";
        	std::cout << cost << "\n";
        	if (value)
        	{
		    	for (auto i : value.value())
		    		std::cout << i << " ";
        		std::cout << "\n";
       		}
            std::cout << "-------\n";
		}
		
        State(const State& s)
        {
        	travel_time = s.travel_time;
        	distance = s.distance;
        	cost = s.cost;
        	std::vector<int> vv;
        	if (s.value)
        	{
        		for (auto i : s.value.value())
        			vv.push_back(i);
        		value = vv;
        	}
        }
        
        static std::optional< std::vector<int> > __value(State lt, State rt)
        {
            if ((!lt.value) && (!rt.value))
                return {};
            else if ((lt.value) && (!rt.value))
                return lt.value;
            else if ((!lt.value) && (rt.value))
                return rt.value;
            else
            {
                int sz = lt.value.value().size();
                std::vector<int> ret(sz);
                for (int i = 0; i < sz; i++)
                    ret.at(i) = lt.value.value()[i] + rt.value.value()[i];
                std::optional<std::vector<int> > f(ret);
                return f;
            }
        }
        
        const State operator+(const State& other)
        { 
            State temp = {travel_time + other.travel_time, distance + other.distance,
                            cost + other.cost, State::__value((*this), other)};
            return temp;
        }
         
        State& operator+=(const State& other)
        {
            travel_time += other.travel_time;
            distance += other.distance;
            cost += other.cost;
            value = State::__value((*this), other);
            return *this;
        }
        
        bool operator< (const State &other)
        {
            if (!(travel_time == other.travel_time))
                return travel_time < other.travel_time;
            if (!(cost == other.cost))
                return cost < other.cost;
            if (!(distance == other.distance))
                return distance < other.distance;
            return false;
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// Route
class Route  
{
    public:
        Storage storage;
        Courier courier;
        Matrix matrix;
        int start_time;
        std::vector<Job> jobs;
        int travel_time;
        int distance;
        float cost;
        
        Route(){}
        
        Route(
        	Storage s,
        	Courier c,
        	Matrix m,
        	int st,
        	std::vector<Job> j,
        	int tt,
        	int d,
        	float ct)
        {
        	storage = s;
        	courier = c;
        	matrix = m;
        	start_time = st;
        	jobs = j;
        	travel_time = tt;
        	distance = d;
        	cost = ct;
        }
        
		void print()
		{
            std::cout << "-------\n";
        	std::cout << "Route:\n";
        	storage.print();
        	courier.print();
        	matrix.print();
        	std::cout << start_time << "\n";
	    	for (auto i : jobs)
	    		i.print();
        	std::cout << "\n";
        	std::cout << travel_time << "\n";
        	std::cout << distance << "\n";
        	std::cout << cost << "\n";
            std::cout << "-------\n";
		}
		
		Route(const Route& r)
		{
			storage = Storage(r.storage);
			courier = Courier(r.courier);
			matrix = Matrix(r.matrix);
			start_time = r.start_time;
			for (auto i : r.jobs)
				jobs.push_back(Job(i));
			travel_time = r.travel_time;
			distance = r.distance;
			cost = r.cost;
		}

        void save_state(State state)
        {
            travel_time += state.travel_time;
            cost += state.cost;
            distance += state.distance;
        }

        Route new_route(std::vector<Job> jobs)
        {
            std::vector<Job> jb;
            for (auto j : jobs)
                jb.push_back(j);
            Route ret = {storage, courier, matrix, start_time, jb, -1, -1, -1.0};
            return ret;
        }

        int len()
        {
            return jobs.size();
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// Tour
//class Problem; // needed for Tour

class Tour  
{
    public:
        Storage storage;
        std::vector<Route> routes;
        std::vector<Job> unassigned_jobs;
        //Problem& problem;
        
        Tour(){}
        
        Tour(
        	Storage s,
        	std::vector<Route> r,
        	std::vector<Job> ujs)
        {
        	storage = s;
        	routes = r;
        	unassigned_jobs = ujs;
		}
        
		void print()
		{
            std::cout << "-------\n";
        	std::cout << "Tour:\n";
        	storage.print();
	    	for (auto i : routes)
	    		i.print();
        	std::cout << "\n";
	    	for (auto i : unassigned_jobs)
	    		i.print();
        	std::cout << "\n";
            std::cout << "-------\n";
		}
		
		Tour(const Tour& t)
		{
			storage = Storage(t.storage);
			for (auto i : t.routes)
				routes.push_back(Route(i));
			for (auto i : t.unassigned_jobs)
				unassigned_jobs.push_back(Job(i));
		}
		
        State get_state()
        {
            float cost = 0.0;
            int travel_time = 0;
            int distance = 0;
            for (auto route : routes)
            {
                cost += route.cost;
                travel_time += route.travel_time;
                distance += route.distance;
            }
            std::optional< std::vector<int> > sv;
            State s = {travel_time, distance, cost, sv};
            return s;
        }

        int len_jobs()
        {
            int s = 0;
            for (auto route : routes)
                s += route.len();
            s += unassigned_jobs.size();
            return s;
        }
        
        int len()
        {
            return routes.size();
        }
};
////////////////////////////////////////////////////////////////////////////////////////////////// Problem
class Problem 
{
    public:
		virtual Tour init(Storage storage, std::vector<Job> jobs, std::vector<Courier> couriers, std::map<std::string, Matrix> matrices) = 0;
		virtual std::optional <State> get_state(Route route) = 0;
		virtual std::string print() = 0;
		/** /
        static Tour init(Storage storage, std::vector<Job> jobs, std::vector<Courier> couriers);
        virtual std::optional<State> get_state(Route route) 
        {
        	std::optional<State> s;
        	return s;
        }
		/**/
};
////////////////////////////////////////////////////////////////////////////////////////////////// ClassicProblem
class ClassicProblem: public Problem //
{
    public:
        static bool __validate_skills(Job obj, Courier courier) // Job 
        {
            // Проверяем, что задача подходит курьеру 
            for (auto skill : obj.skills)\
            {
                bool found = (std::find(courier.skills.begin(), courier.skills.end(), skill) != courier.skills.end());
                if (!found)
                    return false;
            }
            return true;
        }
        
        static bool __validate_skills(Storage obj, Courier courier) // Storage 
        {
            // Проверяем, что склад подходит курьеру 
            for (auto skill : obj.skills)
            {
                bool found = (std::find(courier.skills.begin(), courier.skills.end(), skill) != courier.skills.end());
                if (!found)
                    return false;
            }
            return true;
        }
        
        static float __cost(int travel_time, int distance, Route route) 
        {
            // Получение стоимости 
            return travel_time * route.courier.cost.second + distance * route.courier.cost.meter;
        }
            
        static State __start(Route route) 
        {
            // Стартуем, едем от куда-то на склад
            array distance_matrix = route.matrix.distance;
            array travel_time_matrix = route.matrix.travel_time;
            int start_id = route.courier.start_location.matrix_id.value();
            int storage_id = route.storage.location.matrix_id.value();
            //route.courier.print();
            //route.storage.print();
            
            int tt = travel_time_matrix[start_id][storage_id];
            int d = distance_matrix[start_id][storage_id];

            Cost cost = route.courier.cost;
            float c = ClassicProblem::__cost(tt, d, route) + cost.start;
            std::optional< std::vector<int> > v;
            State st = {tt, d, c, v};
            return st;
        }
        
        static bool __validate_job(int travel_time, Job job, Route route) //
        {
            // Проверяем, что поездка на эту задачу возможна
            int start_time = route.start_time;
            for (auto window : job.time_windows)
            {
                std::tuple<int, int> seconds = window.get_seconds();
                int start_shift = std::get<0>(seconds);
                int end_shift = std::get<1>(seconds);
                
                if ((start_shift <= start_time + travel_time) && (start_time + travel_time <= end_shift)) //
                    return true;
            }
            return false;
        }
            
        static std::optional<State> __go_job(int curr_point, State state, Job job, Route route) //
        {
            // Оценка стоимости поездки на следующую задачу 
            int tt = route.matrix.travel_time[curr_point][job.location.matrix_id.value()] + job.delay;
            int d = route.matrix.distance[route.storage.location.matrix_id.value()][job.location.matrix_id.value()];
            //
            if (!ClassicProblem::__validate_job(state.travel_time + tt, job, route))
            {
                std::optional<State> st;
                return st;
            }
            std::vector<int> cp;
            for (auto i : job.value)
                cp.push_back(i);
            std::optional<std::vector<int> > f(cp);
            State tmp = {tt, d, ClassicProblem::__cost(tt, d, route), cp};
            if (!ClassicProblem::__validate_courier(tmp + state, route))
            {
                std::optional<State> st;
                return st;
            }

            return tmp;
        }
        
        static bool __validate_storage(int travel_time, Route route) //
        {
            // Проверяем, что поездка на склад возможна 
            std::tuple<int, int> seconds = route.courier.work_time.get_seconds();
            int start_shift = std::get<0>(seconds);
            int end_shift = std::get<1>(seconds);
            int start_time = route.start_time;
            
            if (!((start_shift <= start_time + travel_time) && (start_time + travel_time <= end_shift))) //
                return false;
            return true;
        }
        
        static std::optional<State> __go_storage(int curr_point, State state, Route route) //
        {
            // Оценка стоимости поездки на склад
            int tt = route.matrix.travel_time[curr_point][route.storage.location.matrix_id.value()] + route.storage.load;
            int d = route.matrix.distance[curr_point][route.storage.location.matrix_id.value()];

            if (!ClassicProblem::__validate_storage(state.travel_time + tt, route))
            {
                std::optional<State> st;
                return st;
            }
            std::optional< std::vector<int> > v;
            State s = {tt, d, ClassicProblem::__cost(tt, d, route), v};
            return s;
        }
            
        static std::optional<State> __next_job(int curr_point, State state, Job job, Route route) // //
        {
            // Получаем оценку стоимости поезкки на следующую задачу (со складом) """
            
            State new_state(state); //
            std::optional<State> answer = ClassicProblem::__go_job(curr_point, new_state, job, route);

            if (!answer)
            {
                // 1. если не влезло едем на склад, если склад открыт и успеваем загрузиться до закрытия
                std::optional<State> answer = ClassicProblem::__go_storage(curr_point, new_state, route);
                if (!answer)
                {
                    std::optional<State> st;
                    return st;
                }

                new_state += answer.value();
                
                std::vector<int> v(job.value.size());
                std::fill(v.begin(), v.end(), 0);
                new_state.value = v;

                // 2. едем на точку и успеваем отдать до конца окна
                answer = ClassicProblem::__go_job(route.storage.location.matrix_id.value(), new_state, job, route);
                if (!answer)
                {
                    std::optional<State> st;
                    return st;
                }
                
                new_state += answer.value();
            }else
                new_state += answer.value();
            
            return new_state;
        }
        
        static State __end(int curr_point, Route route) 
        {
            // Заканчиваем, едем с последней задачи в конечную точку 
            array distance_matrix = route.matrix.distance;
            array travel_time_matrix = route.matrix.travel_time;
            int end_id = route.courier.start_location.matrix_id.value();
			
			//std::cout << curr_point << "   " << end_id << "\n";
			
            int tt = travel_time_matrix[curr_point][end_id];
            int d = distance_matrix[curr_point][end_id];
            //std::cout << tt << "-" << d << "\n";
            std::optional< std::vector<int> >  v;
            State st = {tt, d, ClassicProblem::__cost(tt, d, route), v};
            return st;
        }
        
        static bool __validate_courier(State state, Route route) // //
        {
            // Проверяем, что курьер еще жив 

            // 1. проверяем время работы
            std::tuple<int, int> seconds = route.courier.work_time.get_seconds();
            int start_shift = std::get<0>(seconds);
            int end_shift = std::get<1>(seconds);
            
            int start_time = route.start_time;
            if (!((start_shift <= start_time + state.travel_time) && (start_time + state.travel_time <= end_shift))) //
                return false;

            // 2. проверяем максимальную дистанцию
            if (state.distance > route.courier.max_distance)
                return false;

            // 3. проверяем на перевес
            int size_v = state.value.value().size();
            for (int i = 0; i < size_v; i++)
                if (state.value.value()[i] > route.courier.value[i])
                    return false;

            return true;
        }
        
        static Route __greedy_route(Storage storage, std::vector<Job> jobs, Courier courier, std::map<std::string, Matrix> matrices) 
        {
            // Строим жадно тур: по ближайшим подходящим соседям 
            std::cout << "Creating Route, Courier: " << courier.name << ", jobs: " << jobs.size() << ", type: " << courier.profile << "\n";
            
            Matrix matrix = matrices[courier.profile];
            std::tuple<int, int> seconds = courier.work_time.get_seconds();
            int start_shift = std::get<0>(seconds);
            int end_shift = std::get<1>(seconds);
            std::vector<Job> j;
            Route route = {storage, courier, matrix, start_shift, j, 0, 0, 0.0};
			
            int curr_point = route.storage.location.matrix_id.value();
            State state = ClassicProblem::__start(route); // bug there
            
            std::vector<Job> jb;
            for (auto j : jobs)
                jb.push_back(j);
            std::vector<int> v(jb.at(0).value.size());
            std::fill(v.begin(), v.end(), 0);
            state.value = v;

            int length = jobs.size(); 
            int k = 0;
            std::vector<std::string> visited; 
            std::optional<Job> best_job;
            std::optional<State> best_state;
            while (k < length - 1)
            {
				//std::cout << k << " " << length - 1 << " NORMAL WORK\n";
                std::optional<Job> bj;
                best_job = bj;
                std::optional<State> bs;
                best_state = bs;
                for (auto job : jobs)
                {
                    if (std::find(visited.begin(), visited.end(), job.job_id) != visited.end())
                        continue;

                    std::optional<State> answer = ClassicProblem::__next_job(curr_point, state, job, route); 
                    if (!answer)
                        continue;

					//std::cout << job.location.matrix_id.value() << "\n";
                    State end = ClassicProblem::__end(job.location.matrix_id.value(), route);
					//std::cout << "NORMAL WORK4\n";
                    if (!ClassicProblem::__validate_courier(answer.value() + end, route)) 
                        continue;

					//std::cout << "NORMAL WORK5\n";
                    if ((!best_job) || (answer.value() < best_state.value())) 
                    {
                        best_job = job;
                        best_state = answer;
                    }
                }
                if (!best_job)
                    break;

                state = best_state.value();
                curr_point = best_job.value().location.matrix_id.value();
                visited.push_back(best_job.value().job_id);
                route.jobs.push_back(best_job.value());
                k += 1;
            }
            
            state += ClassicProblem::__end(curr_point, route);
            route.save_state(state);
            std::cout << "Created Route, Jobs: " << route.len() << "\n";
            return route;
        }
    
        static Tour __greedy_tour(Storage storage, std::vector<Job> jobs, std::vector<Courier> couriers, std::map<std::string, Matrix> matrices) //
        {
            // Строим жадно тур: по ближайшим подходящим соседям для каждого курьера 
            std::cout << "Creating Tour: " << storage.name << ", Couriers: " << couriers.size() << ", Jobs: " << jobs.size() << "\n";
            
            //random.shuffle(couriers) // pzdc
            
            std::vector<Route> r;
            std::vector<Job> j;
            Tour tour = {storage, r, j};
            std::vector<Courier> used_couriers; 
            
            for (auto courier : couriers) //
            {
                if (!ClassicProblem::__validate_skills(storage, courier))
                    continue;
                
                
                std::vector<Job> ret;
                for (auto job : jobs)
                    if (ClassicProblem::__validate_skills(job, courier))
                        ret.push_back(job);
                
                 
                Route route = ClassicProblem::__greedy_route(storage, ret, courier, matrices);
                if (route.len() == 0)
                    continue;

                used_couriers.push_back(courier);
                for (auto job : route.jobs)
                    jobs.erase(std::remove(jobs.begin(), jobs.end(), job), jobs.end());
                tour.routes.push_back(route);
            }

            for (auto courier : used_couriers)
				couriers.erase(std::remove(couriers.begin(), couriers.end(), courier), couriers.end());

            tour.unassigned_jobs = jobs;
            std::cout << "Created Tour, Routes: " << tour.len() << ", Assigned: " << tour.len_jobs() - jobs.size() << "/" << tour.len_jobs() << "\n";
            return tour;
        }
        
        // static Tour init(Storage storage, std::vector<Job> jobs, std::vector<Courier> couriers, std::map<std::string, Matrix> matrices)  ///////////////////////////////////
		Tour init(Storage storage, std::vector<Job> jobs, std::vector<Courier> couriers, std::map<std::string, Matrix> matrices)  override
		{
			std::cout << "init was called\n";
        	Tour t = ClassicProblem::__greedy_tour(storage, jobs, couriers, matrices);
            return t;
        }
        
		// std::optional<State> get_state(Route route)
		std::optional<State> get_state(Route route) override
        {
			std::cout << "get_state was called\n";
            int size_t = route.jobs.size();
            if (size_t == 0)
            {
                std::optional< std::vector<int> > v;
                State st = {0, 0, 0.0, v};
                return st;
            }

            int curr_point = route.storage.location.matrix_id.value();
            State state = ClassicProblem::__start(route);
            std::vector<int> vg((*route.jobs.begin()).value.size());
            std::fill(vg.begin(), vg.end(), 0);
            state.value = vg;

            for (auto job : route.jobs)
            {
                if (!ClassicProblem::__validate_skills(job, route.courier))
                {
                    std::optional<State> st;
                    return st;
                }

                if (!ClassicProblem::__validate_courier(state, route))
                {
                    std::optional<State> st;
                    return st;
                }

                std::optional<State> answer = ClassicProblem::__next_job(curr_point, state, job, route);
                if (!answer)
                {
                    std::optional<State> st;
                    return st;
                }
                if (!ClassicProblem::__validate_courier(answer.value(), route))
                {
                    std::optional<State> st;
                    return st;
                }

                state = answer.value();
                curr_point = job.location.matrix_id.value();
            }

            state += ClassicProblem::__end(curr_point, route);
            if (!ClassicProblem::__validate_courier(state, route))
            {
                std::optional<State> st;
                return st;
            }

            route.travel_time = state.travel_time;
            route.distance = state.distance;
            route.cost = state.cost;

            std::optional< std::vector<int> > sv;
            state.value = sv;
            return state;
        }

		std::string print() override
		{
			std::string x = "print was called";
			return x;
		}
};

class OverloadedProblem : public Problem
{
public:
	using Problem::Problem;

	
	std::string print() override
	{
		PYBIND11_OVERLOAD_PURE(
			std::string, // return type
			Problem, // parent class
			print, // name of the function
			// arguments (if any)
			);
	}
};


void go_print(py::object obj)
{
	Problem* casted = obj.cast<ClassicProblem*>();
	std::cout << casted->print() << std::endl;
}

/////////////////////////////////////////////////////////////////////////////////////////////
/*
int main(int argc, char **argv)
{    
    std::cout << "Running...\n";
    std::cout << "End.\n";
    return 0;
}
*/
