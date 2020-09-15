import os

# TODO: И вообще забирать все из переменных среды. А их ставить через мок файл или через .env

CONCORDE_PATH = "/usr/local/bin/concorde"
LKH2_PATH = "/usr/local/bin/LKH"  # TODO: Мб большие буквы? Или маленькие?
LKH3_PATH = "/usr/local/bin/LKH"  # TODO: lkh2 и lkh3
VRP_CLI_PATH = "/usr/local/bin/vrp-cli"  # TODO: пофиксить (пока что его нету :( )

# TODO: добавить cplex, cbc, glpk, scip, ipopt, etc

os.environ["LKH"] = "/usr/local/bin/LKH"
os.environ["CONCORDE"] = "/usr/local/bin/concorde"
os.environ["VRP_CLI"] = "/usr/local/bin/vrp-cli"  # TODO: солвер раст

# TODO: будет пересекаться, все поменять!
PROBLEM_FILE = "/tmp/myroute_lkh.tsp"
LKH_PAR_FILE = "/tmp/myroute_lkh.tsp"
VRP_RES_FILE = "/tmp/myroute_lkh.tsp"

