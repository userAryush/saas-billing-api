from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import EmailField, CharField, BooleanField, DateTimeField
from .usermanager import UserManager
from base.models import BaseModel
# PermissionMixin -> Without it, user has no is_superuser, no groups, no user_permissions - Django admin breaks and has_perm() won't work.
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    full_name = CharField(max_length=150)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    email_verified = BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']    
    objects = UserManager()