# Generated by Django 3.1.7 on 2021-04-26 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0003_auto_20210426_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostedwebsite',
            name='certificate_arn',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]