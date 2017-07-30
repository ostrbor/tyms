from datetime import datetime
from django.db import models
from django.db.transaction import atomic


def get_discount(discounts):
    """
    Helper func to get valid current discount that is
    the maximum among all active discounts.
    NOTE: depends on discount interface 'is_active'
    """
    amounts = [x.amount for x in discounts if x.is_active()]
    if amounts:
        return max(amounts)
    else:
        return 0


class Brand(models.Model):
    name = models.CharField(max_length=200)


class Category(models.Model):
    name = models.CharField(max_length=200)


class Client(models.Model):
    name = models.CharField(max_length=200)

    def get_client_discount(self):
        return get_discount(self.discounts)


class Item(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.OneToOneField('Brand')
    categories = models.ManyToManyField('Category')

    @atomic
    def save(self, *args, **kwargs):
        # cache item with each save
        super().save(*args, **kwargs)
        item_cache = ItemCache(item=self)
        item_cache.update_record()

    def get_item_discount(self):
        return get_discount(self.discounts)

    def get_brand_discount(self):
        return get_discount(self.brand.discounts)

    def get_category_discount(self):
        discounts = []
        for category in self.categories:
            discounts.append(get_discount(category.discounts))
        if discounts:
            return max(discounts)
        else:
            return 0


class DiscountAbstract(models.Model):
    beginning = models.DateField()
    end = models.DateField()
    amount = models.PositiveSmallIntegerField()

    class Meta:
        abstract = True

    def is_active(self):
        now = datetime.now()
        if now < self.end and now > self.beginning:
            return True


class ItemDiscount(DiscountAbstract):
    item = models.ForeignKey('Item', related_name='discounts')


class BrandDiscount(DiscountAbstract):
    brand = models.ForeignKey('Brand', related_name='discounts')


class CategoryDiscount(DiscountAbstract):
    category = models.ForeignKey('Category', related_name='discounts')


class ClientDiscount(DiscountAbstract):
    item = models.ForeignKey('Client', related_name='discounts')


class ItemCache(models.Model):
    """To save dynamic values in db for sorting/filtering
    Must be updated daily. NOTE: if necessary use memory cache."""
    item = models.OneToOneField('Item', on_delete=models.CASCADE)
    real_price = models.DecimalField(max_digits=10, decimal_places=2)
    # current active discounts
    category_discount = models.PositiveSmallIntegerField()
    brand_discount = models.PositiveSmallIntegerField()
    item_discount = models.PositiveSmallIntegerField()

    def update_record(self):
        self._calculate_discounts()
        self._calculate_real_price()
        self.save()

    def _calculate_discounts(self):
        self.item_discount = self.item.get_item_discount()
        self.category_discount = self.item.get_category_discount()
        self.brand_discount = self.item.get_brand_discount()

    def _calculate_real_price(self):
        total_discount = (
            self.item_discount + self.category_discount + self.brand_discount)
        self.real_price = (
            self.item.price - self.item.price * total_discount / 100)

    @classmethod
    def update_table(cls):
        # run it daily
        items = cls.objects.all()
        for item in items:
            item.update_record()


if __name__ == '__main__':
    items = Item.objects.select_related('itemcache').filter(
        itemcache__real_price__gte=1000,
        itemcache__real_price__lte=10000).order_by('itemcache__real_price')
