# Generated by Django 5.1.5 on 2025-01-21 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConcertBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concert_name', models.CharField(max_length=255)),
            ],
        ),
    ]
