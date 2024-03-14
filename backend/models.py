from django.contrib.auth.models import User
from django.db import models
from backend.utils import generate_random_id
import uuid
#Income/Expense models
"""
class auth_user_logs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    successful = models.BooleanField(default=False)
    description = models.CharField(max_length=50)
    """

    
class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #_id = models.CharField(('expense_id'), max_length=50, unique=True,primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    creation_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    permissions = [
            ("can_view_expense", "Can view expense"),
            ("can_add_expense", "Can add expense"),
            ("can_change_expense", "Can change expense"),
            ("can_delete_expense", "Can delete expense"),
        ]
    
    """def save(self, *args, **kwargs):
        print("Entro en el save del modelo")                
        #self.id = generate_random_id('E-')
        print("ID: "+ str(self.id))
        object = super().save(*args, **kwargs)        
        print("Despues de guardar el objeto" + str(object))
        return object"""
