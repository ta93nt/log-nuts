# Generated by Django 3.0.2 on 2020-02-19 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lognutsapp', '0006_auto_20200219_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodimage',
            name='file',
            field=models.ImageField(blank=True, null=True, upload_to='images', verbose_name='food_image'),
        ),
    ]
