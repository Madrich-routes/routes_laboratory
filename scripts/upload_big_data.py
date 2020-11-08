from minio import Minio
from minio.error import ResponseError

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

try:
    minio_client.fput_object(big_data_bucket, 'pumaserver_debug.log', '/tmp/pumaserver_debug.log')
except ResponseError as err:
    print(err)

minio_client.copy_object()
