# Generated by Django 4.2.1 on 2023-06-07 04:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episodios',
            name='episodio',
        ),
    ]
