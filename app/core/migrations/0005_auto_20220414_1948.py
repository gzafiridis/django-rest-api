# Generated by Django 2.1.15 on 2022-04-13 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_invoiceline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='date',
        ),
        migrations.AddField(
            model_name='invoice',
            name='month',
            field=models.CharField(default='4', max_length=15),
        ),
    ]