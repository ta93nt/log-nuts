# Generated by Django 3.0.2 on 2020-02-18 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lognutsapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personallog',
            name='code',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='personallog',
            name='food_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='personallog',
            name='price',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='personallog',
            name='tel',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='suggestionfoodsanalysis',
            name='food_name',
            field=models.CharField(max_length=50),
        ),
    ]
