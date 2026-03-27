from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# =====================
# UTILISATEUR
# =====================
class Utilisateur(AbstractUser):

    telephone = models.CharField(max_length=20)

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBRE', 'Membre')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)


