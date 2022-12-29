from django.contrib.auth.models import AbstractUser, Permission
from django.core.management.utils import get_random_secret_key
from django.db import models


class User(AbstractUser):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    ROLE_CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Administrator"),
    )

    def get_secret_key():
        return get_random_secret_key()

    email = models.EmailField(
        "E-mail",
        blank=False,
        null=False,
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        "Role",
        choices=ROLE_CHOICES,
        default=USER,
        blank=False,
        max_length=32,
    )
    bio = models.TextField(
        "Bio",
        blank=True,
        null=True,
        default=None,
    )
    confirmation_code = models.CharField(
        "Confirmation code", max_length=64, default=get_secret_key
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    def save(self, *args, **kwargs):
        if self.role == self.ADMIN:
            self.is_staff = True
        super(User, self).save(*args, **kwargs)
        if self.role == self.ADMIN:
            save_user = User.objects.get(username=self.username)
            needet_permission = ("add_user", "change_user")
            for permission_code in needet_permission:
                permission = Permission.objects.get(codename=permission_code)
                save_user.user_permissions.add(permission)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["role", "username"]

    def __str__(self):
        return self.username
