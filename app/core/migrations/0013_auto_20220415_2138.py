# Generated by Django 2.1.15 on 2022-04-15 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20220415_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceline',
            name='amount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
