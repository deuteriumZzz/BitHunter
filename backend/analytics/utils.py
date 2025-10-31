"""
Модуль для работы с Amazon S3.

Этот модуль предоставляет функции для загрузки и скачивания файлов моделей
в облачное хранилище Amazon S3 с использованием библиотеки boto3.
"""

import boto3
from django.conf import settings

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def save_model_to_s3(model_path, bucket_name, key):
    """
    Загружает файл модели в Amazon S3.

    Args:
        model_path (str): Локальный путь к файлу модели.
        bucket_name (str): Название бакета S3.
        key (str): Ключ (путь) файла в S3.

    Returns:
        None
    """
    s3.upload_file(model_path, bucket_name, key)


def load_model_from_s3(bucket_name, key, local_path):
    """
    Скачивает файл модели из Amazon S3.

    Args:
        bucket_name (str): Название бакета S3.
        key (str): Ключ (путь) файла в S3.
        local_path (str): Локальный путь для сохранения файла.

    Returns:
        None
    """
    s3.download_file(bucket_name, key, local_path)
