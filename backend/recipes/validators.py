import re

from django.core.exceptions import ValidationError


def validate_color(incoming_color):
    """Валидатор проверяет полученное значение color
    на соответствие формату записи в HEX."""
    if re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', incoming_color):
        return incoming_color
    raise ValidationError(f'Запись "{incoming_color}" это не цвет в HEX.')


def validate_slug(incomming_slug):
    """Валидатор проверяет полученное значение slug
    на соответствие разрешенному формату"""
    if re.match(r'^[-a-zA-Z0-9_]+', incomming_slug):
        return incomming_slug
    raise ValidationError(f'Псевдоним "{incomming_slug}" не допустим.')
