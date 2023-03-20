# Generated by Django 3.1.7 on 2021-04-26 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0002_hostedwebsite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostedwebsite',
            name='user_url',
        ),
        migrations.AddField(
            model_name='hostedwebsite',
            name='is_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='hostedwebsite',
            name='validation_host',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='hostedwebsite',
            name='validation_value',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
