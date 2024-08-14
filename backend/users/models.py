from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from recipes import config
from users.utils import max_length_role
from users.validators import validation_username


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=config.MAX_LENGTH_NAME,
        unique=True
    )
    role = models.CharField(
        max_length=max_length_role(
            config.ROLES
        ),
        choices=config.ROLES,
        default=config.USER
    )
    username = models.CharField(
        'Пользователь',
        help_text='Ваш никнейм',
        max_length=config.MAX_LENGTH_NAME,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z'
            ),
            validation_username
        ],
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=config.MAX_LENGTH_NAME,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=config.MAX_LENGTH_NAME,
        blank=True
    )
    password = models.CharField(
        max_length=config.MAX_LENGTH_PASSWORD
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == config.ADMIN
            or self.is_staff
        )


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriptions',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribers',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-id']
        unique_together = ('user', 'author')
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'