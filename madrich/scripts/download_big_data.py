import os
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

names = minio_client.list_objects(big_data_bucket, recursive=True)
names = [name.object_name for name in names]
for name in names:
    print(f'Скачиваем {name}')
    file = big_data_dir / name
    os.makedirs(file.parent, exist_ok=True)
    minio_client.fget_object(big_data_bucket, name, str(file))

# minio_client.copy_object()
