from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    author = filters.AllValuesMultipleFilter(
        field_name='author__id'
    )
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget, method="filter_is_favorited"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget, method="filter_is_in_shopping_cart"
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'is_in_shopping_cart',
            'is_favorited',
        )