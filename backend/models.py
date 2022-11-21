from auth_user.models import User, Contact
from django.db import models


# Create your models here.

# модель магазина
class Shop(models.Model):
    user = models.OneToOneField(User,
                                verbose_name='Пользователь',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE
                                )
    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка на сайт', null=True, blank=True)
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} - {self.user}'


# модель категорий
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории', unique=True)
    shops = models.ManyToManyField(Shop,
                                   verbose_name='Магазины',
                                   related_name='categories',
                                   blank=True
                                   )

    class Meta:
        verbose_name = 'Категории'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


# модель продукта
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название продукта', unique=True)
    category = models.ForeignKey(Category,
                                 verbose_name='Категория',
                                 related_name='products',
                                 blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return f'{self.category} - {self.name}'


# модель информации о продукте
class ProductInfo(models.Model):
    product = models.ForeignKey(Product,
                                verbose_name='Продукт',
                                related_name='product_infos',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,
                             verbose_name='Магазин',
                             related_name='product_infos',
                             blank=True,
                             on_delete=models.CASCADE
                             )

    model = models.CharField(max_length=50, verbose_name='модель')
    article = models.PositiveIntegerField(verbose_name='артикул')
    quantity = models.PositiveIntegerField(verbose_name='кол-во')
    price = models.PositiveIntegerField(verbose_name='цена')
    price_rrc = models.PositiveIntegerField(verbose_name='рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'информация о продукте'
        verbose_name_plural = 'информация о продуктах'
        # исключения в базе
        constraints = [
            models.UniqueConstraint(fields=['shop', 'product', 'article'], name='unique_product_info')
        ]

    def __str__(self):
        return f'{self.shop.name} - {self.product.name}'


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название параметра')

    class Meta:
        verbose_name = 'Название параметра'
        verbose_name_plural = 'Список параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameter',
                                     on_delete=models.CASCADE,
                                     blank=True
                                     )
    parameter = models.ForeignKey(Product,
                                  verbose_name='параметр',
                                  related_name='product_parameter',
                                  on_delete=models.CASCADE,
                                  blank=True)
    value = models.CharField(max_length=50, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter')
        ]

    def __str__(self):
        return f'{self.product_info.model} - {self.parameter.name}'


class Order(models.Model):
    STATE_CHOICES = (
        ('basket', 'Статус корзины'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             related_name='order',
                             blank=True,
                             on_delete=models.CASCADE
                             )
    contact = models.ForeignKey(
        Contact,
        verbose_name='Контакт',
        related_name='orders',
        blank=True,
        on_delete=models.CASCADE
    )
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Статус', choices=STATE_CHOICES, max_length=14)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-dt',)

    def __str__(self):
        return f'{self.user} - {self.dt}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              verbose_name='Заказ',
                              related_name='ordered_items',
                              blank=True,
                              on_delete=models.CASCADE
                              )
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='ordered_items',
                                     blank=True,
                                     on_delete=models.CASCADE
                                     )
    quantity = models.PositiveIntegerField(default=1, verbose_name='количество')
    price = models.PositiveIntegerField(default=1, verbose_name='цена')
    total_amount = models.PositiveIntegerField(default=1, verbose_name='общая стоимость')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item')
        ]

    def __str__(self):
        return f'№{self.order} - {self.product_info.model}: {self.quantity} * {self.price} = {self.total_amount}'

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.price
        super(OrderItem, self).save(*args, **kwargs)
