from django.contrib.auth import get_user_model
from django.db import IntegrityError
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter
from api.permissions import IsAdminOrReadOnly
from recipes.models import Tag, Ingredient
from users.models import Follow

from api.serializers import FollowSerializer, IngredientSerializer, TagSerializer

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitOffsetPagination

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
    def del_subscribe(self, request, id=None):
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

    @action(detail=False, permission_classes=(IsAuthenticated,))
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
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    pass