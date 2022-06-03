import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Upload initial data to db'

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            help="initial data file path",
            default=Path(__file__).parent,
        )

    def handle(self, *args, **options):
        file_path = options['path']

        with open(
                os.path.join(file_path, 'ingredients.json'),
                encoding='utf-8'
        ) as f:

            data = json.load(f)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
            f.close()

        tags = (
            ('Завтрак', '#AFB83B', 'breakfast'),
            ('Обед', '#FAD000', 'lunch'),
            ('Полдник', '#FF9933', 'brunch'),
            ('Ужин', '#DB4035', 'dinner'),
            ('Ночной дожор', '#B8255F', 'latenighteater'),
        )

        for tag in tags:
            name, color, slug = tag
            Tag.objects.get_or_create(
                name=name,
                color=color,
                slug=slug
            )

        self.stdout.write(self.style.SUCCESS('Imprint was successful.'))
