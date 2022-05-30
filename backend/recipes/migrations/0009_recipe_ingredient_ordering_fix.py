# Generated by Django 2.2.19 on 2022-05-30 20:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_recipes_models_str_fix'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('id',), 'verbose_name': 'Ингридиент', 'verbose_name_plural': 'Ингридиенты'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть меньше минуты.'), django.core.validators.MaxValueValidator(720, message='Мы не принимаем рецепты, которые надо готовить больше 12.0 часов.')], verbose_name='Время приготовления, мин'),
        ),
    ]