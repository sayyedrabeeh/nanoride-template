# Generated by Django 5.1 on 2024-10-23 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0023_alter_categories_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
        migrations.AddField(
            model_name='variants',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1000, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variants',
            name='stock',
            field=models.IntegerField(default=1000),
            preserve_default=False,
        ),
    ]
