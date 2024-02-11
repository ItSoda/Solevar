# Generated by Django 4.2 on 2024-02-11 08:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tgbot", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="admin",
            options={
                "verbose_name": "админа",
                "verbose_name_plural": "ТГ бот - админы",
            },
        ),
        migrations.AddField(
            model_name="news",
            name="title",
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]
