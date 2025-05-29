from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    username = models.CharField(max_length=50, unique=True, null=False)
    email = models.EmailField()
    password_hash = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, null=False)
    phone = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password):
        self.password_hash = make_password(raw_password)

    class Meta:
        ordering = ['username']
        db_table = 'user'
        indexes = [
            models.Index(fields=['username']),
        ]
