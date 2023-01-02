# Generated by Django 2.2.16 on 2022-12-29 21:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20220512_2221'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['name'], 'verbose_name': 'Genre', 'verbose_name_plural': 'Genres'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Review', 'verbose_name_plural': 'Reviews'},
        ),
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ['name', 'year'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(help_text='Name of the category of the work', max_length=256, unique=True, verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(help_text='The unique address of the category, part of the URL(for example, for category movies slug could be films).', unique=True, verbose_name='Category address'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(help_text='Comment author', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, help_text='Automatically set when publishing', verbose_name='Date and time of publication'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='review',
            field=models.ForeignKey(help_text='The review for which the comment was written', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='reviews.Review', verbose_name='Review'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(help_text='Feedback text', verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(help_text='Name of the genre of the work', max_length=256, unique=True, verbose_name='Genre'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(help_text='The unique address of the genre, part of the URL(for example, for the genre a fantasy slug can be fantastic).', unique=True, verbose_name='Genre address'),
        ),
        migrations.AlterField(
            model_name='review',
            name='author',
            field=models.ForeignKey(help_text='Review autor', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='review',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, help_text='Automatically set when publishing', verbose_name='Date and time of publication'),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], help_text='Rating works from 1 to 10', verbose_name='Rating'),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(help_text='Feedback text', verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.ForeignKey(help_text='The name of the product for which the review', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='reviews.Title', verbose_name='Product'),
        ),
        migrations.AlterField(
            model_name='title',
            name='category',
            field=models.ForeignKey(help_text='Name of the category of the work', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='titles', to='reviews.Category', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, help_text='Brief description of the work', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(help_text='Genre', related_name='titles', to='reviews.Genre', verbose_name='Genre'),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.CharField(help_text='Product name', max_length=256, verbose_name='Product'),
        ),
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(blank=True, help_text='Product rating based on user reviews', null=True, verbose_name='Product Rating'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveIntegerField(help_text='Year of creation of the product', validators=[reviews.validators.validator_year], verbose_name='Year'),
        ),
    ]
