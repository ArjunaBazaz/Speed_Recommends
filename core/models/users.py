from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Adapted from https://www.pyphilly.org/know-thy-user-custom-user-models-django-allauth/


class RecommendSiteUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError("Username must be set")

        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username=username, email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_site_admin = True
        user.save(using=self._db)
        return user

    
class RecommendSiteUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Email Address',
        blank=True
    )
    username = models.CharField(
        max_length=200,
        db_index=True,
        unique=True
    )

    first_name = models.CharField(
        max_length=200,
        blank=True
    )
    
    last_name = models.CharField(
        max_length=200,
        blank=True
    )

    is_staff = models.BooleanField(default=False)
    is_site_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    username = models.CharField(max_length=200, unique=True)
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"

    objects = RecommendSiteUserManager()

    def get_full_name(self):
        return self.first_name + " " + self.last_name
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"