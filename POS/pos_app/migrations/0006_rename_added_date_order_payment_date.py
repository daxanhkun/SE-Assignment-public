# Generated by Django 3.2.8 on 2021-11-17 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pos_app', '0005_order_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='added_date',
            new_name='payment_date',
        ),
    ]