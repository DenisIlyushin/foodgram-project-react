from django.contrib import admin

from recipes.models import Ingredient, Tag, Recipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name', 'slug')


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('author', 'name', 'text', )
    search_fields = ('name',)
    ordering = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def is_favorite(self, obj):
        return obj.favorites.count()
