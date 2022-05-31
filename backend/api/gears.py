import base64
import binascii
import imghdr
import uuid

import six
from django.core.files.base import ContentFile
from rest_framework import serializers


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
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension
