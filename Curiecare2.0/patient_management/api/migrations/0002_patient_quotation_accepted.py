# Generated by Django 5.1.2 on 2024-10-30 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='quotation_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
