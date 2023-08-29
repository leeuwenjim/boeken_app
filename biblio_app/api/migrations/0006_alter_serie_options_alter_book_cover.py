# Generated by Django 4.2.2 on 2023-06-27 21:29

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_book_back_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serie',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, max_length=250, null=True, upload_to=api.models.cover_upload_location),
        ),
    ]
