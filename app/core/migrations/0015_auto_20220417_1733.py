# Generated by Django 2.1.15 on 2022-04-17 17:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20220416_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='membership', to=settings.AUTH_USER_MODEL),
        ),
    ]
