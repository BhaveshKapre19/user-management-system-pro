from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import os, uuid
from django.conf import settings

# Function to upload avatar to user-specific directory
def user_avatar_path(instance, filename):
    unique_filename = f'{uuid.uuid4()}.{filename.split(".")[-1]}'
    return os.path.join('images', instance.username, 'avatars', unique_filename)

# Function to upload user files to user-specific directory
def user_file_path(instance, filename):
    return f'user_files/{instance.owner.slug}/{filename}'

class CustomUserModel(AbstractUser):
    email = models.EmailField(unique=True)
    slug = models.SlugField(unique=True, blank=True)
    is_disable = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username + str(uuid.uuid4()))
        super().save(*args, **kwargs)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

class UserFiles(models.Model):
    owner = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_file_path)
    allowed_users = models.ManyToManyField(CustomUserModel, related_name="allowed_files", blank=True)

    def __str__(self):
        return os.path.basename(self.file.name)
