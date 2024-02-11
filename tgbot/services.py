import boto3
from django.conf import settings


def upload_media_tgbot_to_yandex_cloud(self):
    if self.photo:
        # Получаем ключи доступа к Yandex.Cloud из переменных окружения
        access_key = settings.YANDEX_CLOUD_ACCESS_KEY
        secret_key = settings.YANDEX_CLOUD_SECRET_KEY
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
        file_path = (
            f"tgbot_images/{self.photo.name}"  # Путь к изображению в Yandex.Cloud
        )
        file_data = self.photo.read()
        client.put_object(Bucket=bucket_name, Key=file_path, Body=file_data)

        self.photo = f"{settings.MEDIA_URL}{file_path}"
