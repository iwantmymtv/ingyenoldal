# Generated by Django 3.1.7 on 2021-07-19 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_subscription_max_page_per_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='max_page_per_site',
        ),
        migrations.AddField(
            model_name='plan',
            name='max_page_per_site',
            field=models.IntegerField(default=5),
        ),
    ]
