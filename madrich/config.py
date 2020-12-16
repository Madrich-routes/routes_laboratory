from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    # ------------------------------------ Основные директории проекта ------------------------------------
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATA_DIR: Path = BASE_DIR / 'data'
    TMP_DIR: Path = DATA_DIR / 'tmp'
    UPLOAD_DIR: Path = BASE_DIR / 'api/data'  # куда апишка сливает файлы
    CACHE_DIR: Path = TMP_DIR / 'cache'

    # ------------------------------------ Пути к движкам проекта -----------------------------------------
    CONCORDE_PATH: str = ''
    LKH3_PATH: str = ''
    LKH2_PATH: str = ''
    VRP_CLI_PATH: str = 'vrp-cli'
    VROOM_PATH: str = ''

    # ------------------------------------ Адреса OSRM-серверов -------------------------------------------
    OSRM_CAR_HOST = 'desktop.dimitrius.club'
    OSRM_CAR_PORT = '5000'

    OSRM_FOOT_HOST = 'desktop.dimitrius.club'
    OSRM_FOOT_PORT = '5001'

    OSRM_BICYCLE_HOST = 'desktop.dimitrius.club'
    OSRM_BICYCLE_PORT = '5002'

    # ------------------------------------- Minio ---------------------------------------------------------
    MINIO_HOST = 'desktop.dimitrius.club:19000'
    MINIO_ACCESS_KEY = 'Madrich'
    MINIO_SECRET_KEY = 'RbbitsAsshole_o_'
    MINIO_SECURE = False

    # ------------------------------------- Other ----------------------------------------------------------
    REDIS_HOST: str = '127.0.0.1'
    HOST: str = '0.0.0.0'
    PORT: str = '5000'

    class Config:
        case_sensitive = True
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
