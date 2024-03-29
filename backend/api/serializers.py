from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from foodgram.settings import MAX_COOKING_TIME
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import Follow

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=('ingredient', 'recipe'),
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def _create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            ) for ingredient in ingredients
        ])

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def validate(self, data):
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Нужен хоть один ингредиент для рецепта')
        ingredients_set = []
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                errors.append(
                    'Количество ингредиента с id {0} должно '
                    'быть целым и больше 0.'.format(ingredient["id"])
                )
            if ingredient['id'] in ingredients_set:
                errors.append(
                    'Дважды ингредиента с id {0} в рецепт положить нельзя. '
                    'Может быть стоит изменить его количество?'.format(
                        ingredient["id"]
                    )
                )
            ingredients_set.append(ingredient['id'])
        tags = data.get('tags')
        if len(tags) > len(set(tags)):
            errors.append('Дважды один и тот же ярлык повторять нельзя.')
        cooking_time = float(data.get('cooking_time'))
        if cooking_time < 1 or cooking_time > MAX_COOKING_TIME:
            errors.append(
                'Время приготовления должно быть больше 1 минуты и '
                'меньше {0} часов.'.format(MAX_COOKING_TIME / 60)
            )
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        data['tags'] = tags
        data['cooking_time'] = cooking_time
        return data

    def get_ingredients(self, obj):
        return IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=obj),
            many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(
            favorites__user=user,
            id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return Recipe.objects.filter(
            shopping_cart__user=user,
            id=obj.id
        ).exists()

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self._create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance


class FavoriteOrFollowSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def to_internal_value(self, data):
        return data

    def validate(self, data):
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки. Нельзя подписаться на самого себя.'
            })
        if Follow.objects.filter(
                user=user_id,
                author=author_id
        ).exists():
            raise serializers.ValidationError({
                'errors': 'Ошибка подписки. Нельзя подписаться повторно.'
            })
        get_object_or_404(User, id=author_id)
        data['user'] = User.objects.get(id=user_id)
        data['author'] = User.objects.get(id=author_id)
        return data

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        recipes_set = Recipe.objects.filter(author=obj.author)
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            recipes_set = recipes_set[:int(limit)]
        return FavoriteOrFollowSerializer(
            recipes_set,
            many=True
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
