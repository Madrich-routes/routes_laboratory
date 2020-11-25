import os
import pathlib

from minio import Minio

from madrich.config import settings

minio_client = Minio(
    endpoint=settings.MINIO_HOST,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)

big_data_bucket = "bigdata"
big_data_dir = settings.DATA_DIR / 'big'

# Создаем бакет, если нужно
if not minio_client.bucket_exists(big_data_bucket):
    print(f'Создаем {big_data_bucket}')
    minio_client.make_bucket(big_data_bucket, location="us-east-1")
else:
    print('Бакет уже существует...')

for p in pathlib.Path(big_data_dir).rglob("*"):
    if p.is_file():
        name = os.path.relpath(p, big_data_dir)
        print(f'Загружаем {name}')
        minio_client.fput_object(big_data_bucket, name, p)
