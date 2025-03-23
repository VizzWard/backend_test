from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# Roles: Default, SuperUser, Staff, Admin
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        related_name="users",
        default=1  # ID del rol por defecto
    )