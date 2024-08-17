import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

PATH_SRC = 'static/data/'

src = (
    (f'{PATH_SRC}ingredients.csv', Ingredient, ['name', 'measurement_unit']),
    (f'{PATH_SRC}tags.csv', Tag, ['name', 'slug']),
)


class Command(BaseCommand):
    help = 'Загрузка данных из файла csv в базу данных'

    def import_csv(self, filename, model, fields):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                db_objects = []
                for row in reader:
                    args = {fields[i]: row[i] for i in range(len(fields))}
                    db_objects.append(model(**args))
                model.objects.bulk_create(
                    db_objects,
                    ignore_conflicts=True
                )
                self.stdout.write(self.style.SUCCESS(f'{filename} обработан'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при загрузке {filename}: {e}'))

    def handle(self, *args, **kwargs):
        for filename, model, fields in src:
            self.import_csv(filename, model, fields)
