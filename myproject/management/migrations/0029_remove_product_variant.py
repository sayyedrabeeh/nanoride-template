# Generated by Django 5.1 on 2024-10-23 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0028_alter_product_variant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='Variant',
        ),
    ]
