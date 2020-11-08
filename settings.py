"""Здесь описаны основные настройки системы.

# TODO: добавить cplex, cbc, glpk, scip, ipopt, z3, etc # TODO: lkh2 и lkh3 и скомпиленные с разными
структурами # TODO: Мб большие буквы? Или маленькие? # TODO: И вообще забирать все из переменных среды. А их
ставить через мок файл или через .env
"""
import os
from pathlib import Path

from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

# ------------------------------------- Основные директории проекта -----------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
TMP_DIR = DATA_DIR / 'tmp'
CACHE_DIR = TMP_DIR / 'cache'

os.environ["LKH2"] = "/usr/local/bin/LKH2"
os.environ["LKH3"] = "/usr/local/bin/LKH3"

os.environ["LKH"] = "/usr/local/bin/LKH"
os.environ["CONCORDE"] = "/usr/local/bin/concorde"
os.environ["VRP_CLI"] = "/usr/local/bin/vrp-cli"

CONCORDE_PATH = os.environ["CONCORDE"]
LKH3_PATH = os.environ["LKH"]
VRP_CLI_PATH = os.environ["VRP_CLI"]
VROOM_PATH = os.environ["VROOM"]

HERE_API_KEY = "MOH6CaTy-5eQQmLRStCMT2wNujETT1ld7n8OZwOSGHo"

PROBLEM_FILE = f"/tmp/problem_lkh.{os.getpid()}.tsp"
LKH_PAR_FILE = f"/tmp/parameters_lkh.{os.getpid()}.par"
VRP_RES_FILE = f"/tmp/solution_lkh.{os.getpid()}.sol"

REDIS_HOST = '127.0.0.1'

# ------------------------------------------------ Адреса OSRM-серверов -------------------------------------------
OSRM_CAR_HOST = 'dimitrius.keenetic.link'
OSRM_CAR_PORT = '5000'

OSRM_FOOT_HOST = 'dimitrius.keenetic.link'
OSRM_FOOT_PORT = '5001'

OSRM_BICYCLE_HOST = 'dimitrius.keenetic.link'
OSRM_BICYCLE_PORT = '5002'

# ------------------------------------------------- Minio -----------------------------
MINIO_HOST = 'dimitrius.keenetic.link:19000'
MINIO_ACCESS_KEY = 'Madrich',
MINIO_SECRET_KEY = 'RbbitsAsshole_o_',
MINIO_SECURE = False,
