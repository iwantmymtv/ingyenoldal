# Generated by Django 3.1.7 on 2021-05-15 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0003_auto_20210503_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='is_defered',
            field=models.BooleanField(default=False),
        ),
    ]
