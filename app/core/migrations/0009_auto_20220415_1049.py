# Generated by Django 2.1.15 on 2022-04-15 10:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20220415_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
