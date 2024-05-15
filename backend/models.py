from django.contrib.auth.models import User
from django.db import models
import uuid
from django.conf import settings
#from guardian.shortcuts import assign_perm,remove_perm

#Income/Expense models

class AuthUserLogs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField()
    creation_time = models.TimeField()
    platform_OS = models.CharField(max_length=50)
    successful = models.BooleanField(default=False)
    description = models.CharField(max_length=50)
    
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    hexColor = models.CharField(max_length=7)
    
class SubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    hexColor = models.CharField(max_length=7)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
   
class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #_id = models.CharField(('expense_id'), max_length=50, unique=True,primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #category = models.CharField(max_length=100)
    creation_date = models.DateField()
    creation_time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT)


class Income(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #_id = models.CharField(('income_id'), max_length=50, unique=True,primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #category = models.CharField(max_length=100)
    creation_date = models.DateField()
    creation_time = models.TimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT)

   

class BlacklistedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token

#DJANGO CHANNELS
class ChatSession(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True, verbose_name="Chat Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="customer_chats", on_delete=models.CASCADE, verbose_name="Cliente")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="admin_chats", on_delete=models.CASCADE, verbose_name="Admin/Superusuario")
    
    def __str__(self):
        return f"Chat {self.id} entre {self.customer} y {self.admin}"