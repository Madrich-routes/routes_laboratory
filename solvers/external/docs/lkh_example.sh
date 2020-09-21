PROBLEM_FILE=/tmp/problem_lkh.1134974.tsp
TOUR_FILE=/tmp/solution_lkh.1134974.sol
CANDIDATE_FILE=/tmp/candidates_lkh.1134974.cand
PI_FILE=/tmp/candidates_lkh.1134974.pi

SPECIAL

ASCENT_CANDIDATES=50   #
EXCESS=0.231211
BACKBONE_TRIALS = 0
BACKTRACKING = NO

CANDIDATE_SET_TYPE = POPMUSIC
# Добавить дополнительных кандидатов до кучи
# EXTRA_CANDIDATES = 0
# EXTRA_CANDIDATE_SET_TYPE = QUADRANT | NN

# ------------------------------------------ Начальный тур -------------------------------------------------

INITIAL_TOUR_ALGORITHM=WALK
# Нормальные парни: NEAREST-NEIGHBOR, MOORE, WALK

#BORUVKA — работает везде, но небыстро
#SOP — похоже, что только для сопов,
#CVRP, MTSP — мб только для своих? (всяко только для симметричных)
#TSPDL — только для 1 сейслмена
#SIERPINSKI, QUICK-BORUVKA — только для метрических


DEPOT = 1
# EDGE_FILE =


EXTERNAL_SALESMEN = 0
# BWTSP =

GAIN23 = NO
GAIN_CRITERION = YES
INITIAL_PERIOD = 26984
INITIAL_STEP_SIZE = 1
# INITIAL_TOUR_FILE =
INITIAL_TOUR_FRACTION = 1.000
# INPUT_TOUR_FILE =
KICK_TYPE = 4
KICKS = 1
# MAX_BREADTH =
MAKESPAN = NO
MAX_CANDIDATES = 5
MAX_SWAPS = 0
MAX_TRIALS = 500
# MERGE_TOUR_FILE =
MOVE_TYPE = 5 SPECIAL
MTSP_MIN_SIZE = 1
MTSP_MAX_SIZE = 1000
# MTSP_SOLUTION_FILE =
# NONSEQUENTIAL_MOVE_TYPE = 5
# OPTIMUM =
# OUTPUT_TOUR_FILE =
PATCHING_A = 1
PATCHING_C = 0
# PI_FILE =
POPMUSIC_INITIAL_TOUR = YES
POPMUSIC_MAX_NEIGHBORS = 10
POPMUSIC_SAMPLE_SIZE = 20
POPMUSIC_SOLUTIONS = 100
POPMUSIC_TRIALS = 1
POPULATION_SIZE = 20
PRECISION = 100
PROBLEM_FILE = /tmp/problem_lkh.1134974.tsp
RECOMBINATION = IPT
RESTRICTED_SEARCH = YES
RUNS = 1
SALESMEN = 6239
SCALE = 1
SEED = 1
# SINTEF_SOLUTION_FILE =
STOP_AT_OPTIMUM = YES
SUBGRADIENT = NO
# SUBPROBLEM_SIZE =
# SUBPROBLEM_TOUR_FILE =
SUBSEQUENT_MOVE_TYPE = 5 SPECIAL
SUBSEQUENT_PATCHING = YES
TIME_LIMIT = 1200.0
TOUR_FILE = /tmp/solution_lkh.1134974.sol
TRACE_LEVEL = 3
VEHICLES = 6239