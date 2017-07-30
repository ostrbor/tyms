import random
import factory
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "second.settings")
django.setup()

from myapp.models import Category, Product


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'category{n}')


class ProductFactory(factory.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'name{n}')
    price = factory.LazyFunction(lambda: random.randint(90, 110))
    # category = factory.SubFactory(CategoryFactory)


if __name__ == '__main__':
    for _ in range(5):
        CategoryFactory.create()
    categories = Category.objects.all()
    for cat in categories:
        for _ in range(10):
            product = ProductFactory.build()
            product.category = cat
            product.save()
