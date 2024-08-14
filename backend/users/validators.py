import re

from django.core.exceptions import ValidationError


def validation_username(value):
    if value == 'me':
        raise ValidationError(
            ({'username': 'me - недопустимое имя пользователя'}),
        )
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError({'username': 'Недопустимые символы'})
