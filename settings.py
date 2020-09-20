import os

# TODO: добавить cplex, cbc, glpk, scip, ipopt, etc
# TODO: lkh2 и lkh3
# TODO: Мб большие буквы? Или маленькие?
# TODO: И вообще забирать все из переменных среды. А их ставить через мок файл или через .env

os.environ["LKH2"] = "/usr/local/bin/LKH2"
os.environ["LKH"] = "/usr/local/bin/LKH"
os.environ["CONCORDE"] = "/usr/local/bin/concorde"
os.environ["VRP_CLI"] = "/usr/local/bin/vrp-cli"

CONCORDE_PATH = os.environ["LKH"]
LKH3_PATH = os.environ["CONCORDE"]
VRP_CLI_PATH = os.environ["VRP_CLI"]

HERE_API_KEY = "MOH6CaTy-5eQQmLRStCMT2wNujETT1ld7n8OZwOSGHo"

PROBLEM_FILE = f"/tmp/problem_lkh.{os.getpid()}.tsp"
LKH_PAR_FILE = f"/tmp/parameters_lkh.{os.getpid()}.par"
VRP_RES_FILE = f"/tmp/solution_lkh.{os.getpid()}.sol"

REDIS_HOST = '127.0.0.1'
