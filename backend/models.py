from django.contrib.auth.models import User
from django.db import models
import uuid
from guardian.shortcuts import assign_perm,remove_perm
from guardian.models import UserObjectPermission
import logging
#Income/Expense models
logger = logging.getLogger(__name__)

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
   
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
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.DO_NOTHING)

    permissions = [
            ("can_view_expense", "Can view expense"),
            ("can_add_expense", "Can add expense"),
            ("can_change_expense", "Can change expense"),
            ("can_delete_expense", "Can delete expense"),
        ]    
    
    
    def save(self, *args, **kwargs):
        # Call the parent save method to save the expense first
        super().save(*args, **kwargs)        
        # Assign permissions to the user who created the expense
        assign_perm('change_expense', self.user, self)
        assign_perm('delete_expense', self.user, self)

    def delete_object_permissions(sender, instance, **kwargs):
        # Delete associated object permissions
        UserObjectPermission.objects.filter(object_pk=str(instance.pk)).delete()
    '''def delete(self, *args, **kwargs):
        # Remove permissions when expense is deleted
        try:
            user = self.user
            super().delete(*args, **kwargs)
            remove_perm('change_expense', user, self)
            remove_perm('delete_expense', user, self)
        except Exception as e:
            logger.error(f"Error deleting expense: {e}")
            # Handle the error appropriately, such as raising or logging it
            raise'''

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
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.DO_NOTHING)

    permissions = [
            ("can_view_income", "Can view income"),
            ("can_add_income", "Can add income"),
            ("can_change_income", "Can change income"),
            ("can_delete_income", "Can delete income"),
        ]    
    
    def save(self, *args, **kwargs):
        # Call the parent save method to save the expense first
        super().save(*args, **kwargs)
        
        # Assign permissions to the user who created the income
        assign_perm('change_income', self.user, self)
        assign_perm('delete_income', self.user, self)

    '''def delete(self, *args, **kwargs):
        # Remove permissions when income is deleted
        user = self.user
        super().delete(*args, **kwargs)
        remove_perm('change_income', user, self)
        remove_perm('delete_income', user, self)  '''      



