import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram_backend import settings
from recipes.config import (MAX_LENGTH_LINK, MAX_LENGTH_NAME, MAX_LENGTH_TAG,
                            MAX_LENGTH_TEXT, MAX_LENGTH_TITLE, MAX_LENGTH_UNIT,
                            MAX_LENGTH_URL)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TAG,
        unique=True,
        null=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_LENGTH_TAG,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_LENGTH_TEXT]


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_UNIT,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TITLE
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        'Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления, мин',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    short_link = models.CharField(
        max_length=MAX_LENGTH_LINK,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:MAX_LENGTH_TEXT]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit} '
                f'{self.ingredient.name} для {self.recipe.name}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} добавил в корзину {self.recipe.name}'


class ShortLink(models.Model):
    original_url = models.URLField(
        max_length=MAX_LENGTH_URL
    )
    short_url = models.CharField(
        max_length=MAX_LENGTH_LINK,
        unique=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = self.generate_short_url()
        super().save(*args, **kwargs)

    def generate_short_url(self):
        length = 6
        chars = string.ascii_letters + string.digits
        short_url = ''.join(random.choice(chars) for _ in range(length))
        return short_url

    @property
    def full_short_url(self):
        return f"{settings.DOMAIN_NAME}/{self.short_url}"
