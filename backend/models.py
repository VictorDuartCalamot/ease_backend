from django.contrib.auth.models import User
from django.db import models
from backend.utils import generate_random_id
#Income/Expense models
"""
class auth_user_logs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    successful = models.BooleanField(default=False)
    description = models.CharField(max_length=50)
    """

    
class Expense(models.Model):
    id = models.CharField(('expense_id'), max_length=50, unique=True,primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    creation_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        print("Entro en el save del modelo")                
        self.id = generate_random_id('E-')
        print("ID: "+self.id)
        super().save(*args, **kwargs)
        print("Guardo las cosas?")
