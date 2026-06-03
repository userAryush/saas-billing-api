from django.db import models
from django.db.models import CharField, SlugField, ForeignKey
from django.db.models import PROTECT, CASCADE
from accounts.models import User
from base.models import BaseModel


# Create your models here.
class Organisation(BaseModel):
    name = CharField(max_length=200)
    slug = SlugField(unique=True)          



class Membership(BaseModel):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]
    user = ForeignKey(User, on_delete=CASCADE)
    org = ForeignKey(Organisation, on_delete=CASCADE)
    role = CharField(choices=ROLE_CHOICES, max_length=10)

    class Meta:
        unique_together = [('user', 'org')]