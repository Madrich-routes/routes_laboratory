import pathlib

from minio import Minio

import settings

minio_client = Minio(
    'desktop:19000',
    access_key='Madrich',
    secret_key='RbbitsAsshole_o_',
    secure=False,
)

big_data_bucket = "big_data"
big_data_dir = settings.DATA_DIR / 'big_data'

# Создаем бакет, если нужно
if not minio_client.bucket_exists(big_data_bucket):
    print(f'Создаем {big_data_bucket}')
    minio_client.make_bucket(big_data_bucket, location="us-east-1")
else:
    print('Бакет уже существует...')

for p in pathlib.Path(big_data_dir).rglob("*"):
    if p.is_file():
        print(f'Загружаем {p}')
        minio_client.fput_object(big_data_bucket, p, p)

minio_client.copy_object()
