# Generated by Django 5.1 on 2024-10-23 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0029_remove_product_variant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(default='listed', max_length=10),
        ),
    ]
