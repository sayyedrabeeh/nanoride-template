# Generated by Django 5.1 on 2024-10-20 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_alter_category_brand_alter_category_edition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='type1',
        ),
    ]
