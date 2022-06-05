from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    FollowSerializer, IngredientSerializer, TagSerializer, RecipeSerializer,
    FavoriteOrFollowSerializer
)
from foodgram.settings import SHOPPING_LIST_FILE_NAME, SHOPPING_LIST_FORMAT
from recipes.models import (
    Tag, Ingredient, Recipe, Favorite, IngredientRecipe, ShoppingCart
)
from users.models import Follow

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        try:
            follow = Follow.objects.create(
                user=request.user,
                author=get_object_or_404(User, id=id)
            )
        except IntegrityError:
            return Response(
                {'errors': (
                    'Ошибка подписки. Нельзя подписываться '
                    'повторно или на самого себя.'
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        try:
            Follow.objects.filter(
                user=request.user,
                author=get_object_or_404(User, id=id)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {'errors': f'Ошибка отписки. {e}'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        serializer = FollowSerializer(
            self.paginate_queryset(Follow.objects.filter(user=request.user)),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsOwnerOrReadOnly,)

    def _add_object(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже добавлен.'},
                status=status.HTTP_400_BAD_REQUEST)
        if model == Favorite or model == ShoppingCart:
            recipe = get_object_or_404(Recipe, id=pk)
            model.objects.create(user=user, recipe=recipe)
            serializer = FavoriteOrFollowSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Неизвестный метод или модель.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _delete_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if model == Favorite or model == ShoppingCart:
            return Response(
                {'errors': 'Объект не существует или уже удален'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'errors': 'Неизвестный метод или модель.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_object(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self._delete_object(Favorite, request.user, pk)
        return None

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_object(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self._delete_object(ShoppingCart, request.user, pk)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        shopping_list = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                name=F('ingredient__name'),
                measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))
        text = '\n'.join([
            SHOPPING_LIST_FORMAT.format(
                item['name'],
                item['measurement_unit'],
                item['amount']
            )
            for item in shopping_list
        ])
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; '
            f'filename={SHOPPING_LIST_FILE_NAME}'
        )
        return response
