# Generated by Django 3.2.5 on 2021-10-27 05:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pos_app', '0003_auto_20211027_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='added_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]