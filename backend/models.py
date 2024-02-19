from django.db import models
from django.contrib.auth.models import User
from django.db import models
from utils import generate_random_code
#Income/Expense models
class Income(models.Model):
    id = models.CharField(_('Code'), max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_random_code('I-')
        super().save(*args, **kwargs)

    
class Expense(models.Model):
    id = models.CharField(_('Code'), max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
            if not self.code:
                self.code = generate_random_code('E-')
            super().save(*args, **kwargs)
