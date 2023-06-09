# Generated by Django 3.1.7 on 2021-05-15 13:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0006_auto_20210503_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='domain_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[django.core.validators.RegexValidator('^(?!http:\\/\\/www\\.|https:\\/\\/www\\.|http:\\/\\/|https:\\/\\/)?[a-z0-9]+([\\-\\.]{1}[a-z0-9]+)*\\.[a-z]{2,5}(:[0-9]{1,5})?(\\/.*)?$', 'Domain is not valid (do not use http(s)://)')], verbose_name='domain name'),
        ),
    ]
