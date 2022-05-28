# Generated by Django 2.2.19 on 2022-05-25 20:33

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0002_recipes_Tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Нельзя добавить часть выбранного ингредиента! Попробуйте выбрать такой же ингредиент с другой единицей измерения.'), django.core.validators.MaxValueValidator(32767, message='Не многовато ли?')], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
            },
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингридиент', 'verbose_name_plural': 'Ингридиенты'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('slug',), 'verbose_name': 'Ярлык', 'verbose_name_plural': 'Ярлыки'},
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('image', models.ImageField(upload_to='recipe/', verbose_name='Изображение')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не может быть меньше минуты.'), django.core.validators.MaxValueValidator(720, message='Мы не принимаем рецепты, которые надо готовить больше 12 часов.')], verbose_name='Время приготовления, мин')),
                ('pub_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Рецепт')),
                ('ingredients', models.ManyToManyField(related_name='recipes', through='recipes.IngredientRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты')),
                ('tags', models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Ярлыки')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date', 'author', 'name'),
                'default_related_name': 'recipes',
            },
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingredient', to='recipes.Recipe'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('ingredient', 'recipe'), name='unique_ingredient_in_recipe'),
        ),
    ]