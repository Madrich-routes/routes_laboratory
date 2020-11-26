"""Здесь описаны основные настройки системы.

# TODO: добавить cplex, cbc, glpk, scip, ipopt, z3, etc # TODO: lkh2 и lkh3 и скомпиленные с разными
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
UPLOAD_DIR = BASE_DIR / 'api/data'
CACHE_DIR = TMP_DIR / 'cache'

CONCORDE_PATH = env.path('CONCORDE')
LKH3_PATH = env.path('LKH3')
LKH2_PATH = env.path('LKH2')
VRP_CLI_PATH = env.path('VRP_CLI')
VROOM_PATH = env.path('VROOM')

os.environ["LKH"] = "/usr/local/bin/LKH"
os.environ["CONCORDE"] = "/usr/local/bin/concorde"
os.environ["VRP_CLI"] = "/usr/local/bin/vrp-cli"
os.environ["VRP_CLI_UBUNTU"] = "vrp-cli"
os.environ["VROOM"] = ""  # Nikita Vyukov - временная заглушка
HERE_API_KEY = env.str('HERE_API_KEY')

REDIS_HOST = env.str('REDIS_HOST')

# ------------------------------------------------ Адреса OSRM-серверов -------------------------------------------
OSRM_CAR_HOST = 'dimitrius.keenetic.link'
OSRM_CAR_PORT = '5000'

OSRM_FOOT_HOST = 'dimitrius.keenetic.link'
OSRM_FOOT_PORT = '5001'

OSRM_BICYCLE_HOST = 'dimitrius.keenetic.link'
OSRM_BICYCLE_PORT = '5002'

# -------------------------------------------------------- Minio --------------------------------------------------
MINIO_HOST = 'dimitrius.keenetic.link:19000'
MINIO_ACCESS_KEY = 'Madrich'
MINIO_SECRET_KEY = 'RbbitsAsshole_o_'
MINIO_SECURE = False
