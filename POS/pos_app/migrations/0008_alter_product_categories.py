# Generated by Django 3.2.8 on 2021-11-18 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos_app', '0007_auto_20211118_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(null=True, to='pos_app.Category'),
        ),
    ]