# Generated by Django 3.1.7 on 2021-07-19 12:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0008_auto_20210707_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templateextrapage',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='builder.template'),
        ),
    ]
