# Generated by Django 3.0.4 on 2020-05-12 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingcart', '0003_auto_20200512_0308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_order',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
