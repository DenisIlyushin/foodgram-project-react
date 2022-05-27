from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        max_length=254,
        blank=False,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        validators=(validate_username, ),
        verbose_name='Псевдоним',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='username_unique_email',
            )
        ]

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'@{self.username}: {self.email}.'

    @property
    def is_admin(self):
        return self.is_staff

    @property
    def is_user(self):
        return self.is_user


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name="follow_unique_relationships",
                fields=["user", "author"],
            ),
            models.CheckConstraint(
                name="follow_prevent_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        ]

    def __str__(self):
        return f'@{self.user.username} подписан на @{self.author.username}'
