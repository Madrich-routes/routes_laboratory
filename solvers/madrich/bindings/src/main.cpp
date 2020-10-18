#include "generate_vrp.h"
#include "intra_operators.h"
#include "inter_operators.h"
#include "improve.h"


int main ()
{
    ClassicProblem c;
	vrp v = generate_vrp(100);
	
	std::map<std::string, Matrix> mm;
	mm["driver"] = v.matrix;
	Tour t = c.init(v.storage, v.jobs, v.couriers, mm);
	
	improve_tour(t, &c);
    return 0;
}


