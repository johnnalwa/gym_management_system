# Generated by Django 5.0.3 on 2024-04-01 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_payment_delete_paymenttable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='transaction_id',
        ),
    ]