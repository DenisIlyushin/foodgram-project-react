from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.settings import MAX_COOKING_TIME
from recipes.validators import validate_color, validate_slug

User = get_user_model()


class DesignatedModel(models.Model):
    """Абстрактная модель, хранит именованные объекты."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )

    class Meta:
        abstract = True
        ordering = ('name',)


class Ingredient(DesignatedModel):
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_unique_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name[:30]}, {self.measurement_unit}'


class Tag(DesignatedModel):
    color = models.CharField(
        max_length=7,
        default='#3B0363',
        validators=(validate_color,),
        verbose_name='Цвет ярлыка'
    )
    slug = models.SlugField(
        max_length=200,
        db_index=True,
        unique=True,
        validators=(validate_slug,),
        verbose_name='Псевдоним'
    )

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Ярлык'
        verbose_name_plural = 'Ярлыки'

    def __str__(self):
        return f'{self.name[:30]}'


class Recipe(DesignatedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipe/',
        verbose_name='Изображение'
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Ярлыки'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше минуты.'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=('Мы не принимаем рецепты, которые '
                         'надо готовить больше {0} часов.').format(
                    MAX_COOKING_TIME / 60
                )
            )
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        default_related_name = 'recipes'
        ordering = ('-pub_date', 'author', 'name')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name[:30]} от @{self.author.username}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipe'  # м.б. get_recipes
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=True,
        related_name='ingredient'  # м.б. get_ingredients
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                message=('Нельзя добавить часть выбранного ингредиента! '
                         'Попробуйте выбрать такой же ингредиент с другой '
                         'единицей измерения.')
            ),
            MaxValueValidator(
                32767,
                message='Не многовато ли?'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return f'Ингридиент {self.ingredient} нужен для рецепта {self.recipe}'


class UserRecipeListGenerator(models.Model):
    """Абстрактная модель, хранит связь пользователя и рецепта.
    Используется для генерации списков."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class Favorite(UserRecipeListGenerator):

    class Meta(UserRecipeListGenerator.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_fav_list_for_user'
            )
        ]

    def __str__(self):
        return (f'@{self.user.username} добавил '
                f'{self.recipe.name[:30]} в избранное.')


class ShoppingCart(UserRecipeListGenerator):

    class Meta(UserRecipeListGenerator.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_cart_list_for_user'
            )
        ]

    def __str__(self):
        return f'Список покупок для {self.recipe.name[:30]}'
