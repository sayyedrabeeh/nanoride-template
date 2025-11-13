from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
# from image_cropping import ImageRatioField

class CustomUser(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', default='images/profile.jpeg')
    phone = models.CharField(max_length=15, blank=True, null=True) 
    address = models.TextField(blank=True, null=True)  
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_auth_set',  
        blank=True,
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_auth_set',  
        blank=True,
    )


  









 