import time
import random
import string
from datetime import datetime
from django.utils.translation import gettext_lazy as _

def generate_random_code(prefix):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = int(time.time())
    date_part = datetime.now().strftime('%d%m%y')
    return f"{prefix}{random_part}{timestamp}{date_part}"