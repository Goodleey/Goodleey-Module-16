# Generated by Django 3.0.4 on 2020-04-01 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('p_library', '0005_auto_20200401_1341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='age',
        ),
    ]
