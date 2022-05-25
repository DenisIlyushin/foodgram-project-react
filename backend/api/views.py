from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.pagination import LimitOffsetPagination

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    pagination_class = LimitOffsetPagination
