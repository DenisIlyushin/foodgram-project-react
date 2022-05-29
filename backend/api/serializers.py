import base64
import binascii
import imghdr
import uuid

import six
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, Tag, Ingredient, IngredientRecipe
from users.models import Follow

User = get_user_model()


# todo code move to separate file gears.py
class Base64ImageField(serializers.ImageField):
    EMPTY_VALUES = (None, "", [], (), {})

    def to_internal_value(self, data):
        if data in self.EMPTY_VALUES:
            return None

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except (TypeError, binascii.Error, ValueError):
                self.fail('Ошибка загрузки изображения. Файл поврежден.')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = f'{file_name}.{file_extension}'
            # todo code cleanup
            #    "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        # todo code cleanup
        #   мне не очень нравится структура данного кода, кажется можно лучше
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj.id).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    # recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    # def get_recipes(self, obj):
    #     return 10

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


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
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=['ingredient', 'recipe'],
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField('get_ingredients')

    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})

        ingredient_list = []
        for ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=ingredient['id']
            )
            if ingredient in ingredient_list:
                raise serializers.ValidationError({
                    'ingredients': (
                        'Дважды один и тот же ингредиент '
                        'в рецепт положить нельзя. Может '
                        'быть стоит изменить его количество?'
                    )
                })
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError({
                    'ingredients': (
                        'Количество ингридиентов должно быть целым '
                        'и больше 1.'
                    )
                })
            ingredient_list.append(ingredient)
        data['ingredients'] = ingredients
        return data

    def get_ingredients(self, obj):
        return IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=obj),
            many=True
        ).data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientRecipeSerializer.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, obj, validated_data):
        obj.image = validated_data.get('image', obj.image)
        obj.name = validated_data.get('name', obj.name)
        obj.text = validated_data.get('text', obj.text)
        obj.cooking_time = validated_data.get(
            'cooking_time', obj.cooking_time
        )
        obj.tags.clear()
        tags_data = self.initial_data.get('tags')
        obj.tags.set(tags_data)
        IngredientRecipe.objects.filter(recipe=obj).all().delete()
        self.create_ingredients(validated_data.get('ingredients'), obj)
        instance.save()
        return obj

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=obj.id).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
