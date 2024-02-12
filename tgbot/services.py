import boto3
from django.conf import settings
import requests


def upload_media_tgbot_to_yandex_cloud(self):
    if self.photo:
        # Получаем ключи доступа к Yandex.Cloud из переменных окружения
        access_key = settings.YANDEX_CLOUD_ACCESS_KEY
        secret_key = settings.YANDEX_CLOUD_SECRET_KEY
        tgbot_token = settings.TELEGRAM_BOT_TOKEN
        region_name = "ru-central1-c"
        # Инициализируем клиент boto3 для работы с Yandex Object Storage
        client = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net/",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )

        # Загружаем изображение в Yandex.Cloud
        bucket_name = "solevar-bucket"

        response = requests.get(f"https://api.telegram.org/bot{tgbot_token}/getFile?file_id={self.photo}")
        file_path = response.json()["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{tgbot_token}/{file_path}"
        # Загружаем изображение из URL
        file_data = requests.get(file_url).content

        # Формируем путь к файлу в Yandex.Cloud
        file_path_yandex = f"tgbot_images/{file_path.split('/')[-1]}"

        client.put_object(Bucket=bucket_name, Key=file_path_yandex, Body=file_data)

        self.photo = f"https://storage.yandexcloud.net/{bucket_name}/{file_path_yandex}"