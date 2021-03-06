# Generated by Django 3.0.4 on 2020-05-05 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_number', models.AutoField(primary_key=True, serialize=False)),
                ('date_order', models.DateField(auto_now_add=True)),
                ('deli_mode', models.CharField(choices=[('D', 'Delivery'), ('T', 'Takeaway')], default='T', max_length=15)),
                ('address', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('D', 'Delivery'), ('T', 'Takeaway')], default=1, max_length=15)),
                ('total', models.FloatField(default=0.0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('product', models.CharField(max_length=100)),
                ('presentation', models.CharField(max_length=100)),
                ('size', models.CharField(max_length=30)),
                ('additional', models.TextField()),
                ('price_unitary', models.FloatField()),
                ('total', models.FloatField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shoppingcart.Order')),
            ],
        ),
    ]
