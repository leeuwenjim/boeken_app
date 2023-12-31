# Generated by Django 4.2.2 on 2023-06-23 19:42

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=150)),
                ('alias_for', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.author')),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('original_title', models.CharField(blank=True, max_length=200, null=True)),
                ('isbn', models.CharField(blank=True, max_length=15, null=True)),
                ('language', models.CharField(choices=[('NL', 'Nederlands'), ('GB', 'Engels'), ('SE', 'Zweeds'), ('DE', 'Duits'), ('FR', 'Frans'), ('ES', 'Spaans')], default='NL', max_length=3)),
                ('cover', models.ImageField(max_length=250, upload_to=api.models.cover_upload_location)),
                ('back_text', models.TextField()),
                ('publish_year', models.IntegerField(blank=True, null=True)),
                ('authors', models.ManyToManyField(to='api.author')),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Serie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('books', models.ManyToManyField(to='api.book')),
            ],
        ),
        migrations.CreateModel(
            name='SeriesOrdering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering_name', models.CharField(max_length=100)),
                ('book_order', models.CharField(blank=True, max_length=250, null=True)),
                ('serie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.serie')),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.genre')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.publisher'),
        ),
    ]
