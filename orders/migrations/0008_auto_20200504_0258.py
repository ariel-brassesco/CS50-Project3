# Generated by Django 3.0.4 on 2020-05-04 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20200504_0237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='image',
            field=models.ImageField(upload_to='owner/%Y/%m/%d'),
        ),
    ]
