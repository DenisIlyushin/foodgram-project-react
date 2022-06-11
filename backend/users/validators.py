import re

from django.core.exceptions import ValidationError

from foodgram.settings import INCORRECT_USERNAMES


def validate_username(incoming_username):
    for username in INCORRECT_USERNAMES:
        if re.match(username, incoming_username):
            raise ValidationError(f'Имя "{incoming_username}" запрещено.')
    return incoming_username
