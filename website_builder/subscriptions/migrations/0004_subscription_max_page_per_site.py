# Generated by Django 3.1.7 on 2021-07-19 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_auto_20210719_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='max_page_per_site',
            field=models.IntegerField(default=5),
        ),
    ]
