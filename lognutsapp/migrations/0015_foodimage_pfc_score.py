# Generated by Django 3.0.2 on 2020-02-25 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lognutsapp', '0014_auto_20200225_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodimage',
            name='pfc_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
