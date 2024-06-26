import time
import random
import string
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed,ValidationError,NotFound
from backend.serializers import UserSerializer


def generate_random_id(prefix):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = int(time.time())
    date_part = datetime.now().strftime('%d%m%y')
    return f"{prefix}{random_part}{timestamp}{date_part}"

#Funcion para crear filtros de query por fecha y tiempo
def filter_by_date_time(queryset, start_date, end_date, start_time, end_time,):    
    '''
        Returns queries for the given datetime, date and/or time 
    '''
    # Ensure start_date is not after end_date
    if (start_date and end_date) and (start_date > end_date):
        raise ValidationError({'detail': 'Start date cannot be after end date.'})

    if (start_time and end_time) and (start_time > end_time):
        raise ValidationError({'detail': 'Start time cannot be after end time.'})

    # Filter based on date range
    date_query = Q()
    if start_date or end_date:
        if start_date is not None and end_date is not None:
            if start_date == end_date:
                date_query &= Q(creation_date=start_date)
            else:
                date_query &= Q(creation_date__range=[start_date, end_date])
        elif start_date is not None:
            date_query &= Q(creation_date__gte=start_date)
        elif end_date is not None:   
            date_query &= Q(creation_date__lte=end_date)
        #print('Date Query: ', date_query)
        
    #print('despues date query')
        
    # Filter based on time range
    time_query = Q()
    if start_time or end_time:                
        if start_time is not None and end_time is not None:
            #print('Both not none',start_time,end_time)
            if start_time == end_time:
                time_query &= Q(creation_time=start_time)
            else:
                time_query &= Q(creation_time__range=[start_time, end_time])
        elif start_time is not None:
            time_query &= Q(creation_time__gte=start_time)            
        elif end_time is not None:   
            time_query &= Q(creation_time__lte=end_time)
    #print('Time Query: ', time_query)
    #print('Hora: ', start_time, end_time)
    #print('despues time')
        
    # Apply combined date and time filtering
    combined_query = date_query & time_query
    return queryset.filter(combined_query)

def filter_by_datetime_with_custom_field(queryset, start_value, end_value,fieldname):  
    '''Function to filter by datetime, date or time and using a custom field'''
    if (start_value and end_value) and (start_value > end_value):
        raise ValidationError({'detail': 'Start time cannot be after end time.'})

    # Filter based on date range
    value_query = Q()
    if start_value or end_value:
        if start_value is not None and end_value is not None:
            if start_value == end_value:
                value_query &= Q(**{fieldname: start_value})
            else:
                value_query &= Q(**{f"{fieldname}__range": [start_value, end_value]})
        elif start_value is not None:
            value_query &= Q(**{f"{fieldname}__gte": start_value})
        elif end_value is not None:   
            value_query &= Q(**{f"{fieldname}__lte": end_value})
    
    return queryset.filter(value_query)

#Funcion para recuperar el usuario utilizando el email)
def getUserObjectByEmail(email):
    '''Returns User Object by email'''    
    try:
        user = User.objects.get(email=email)   
        return user
    except User.DoesNotExist:
        # Handle the case where the user with the provided email does not exist
        raise NotFound({'detail':'User does not exist'})        