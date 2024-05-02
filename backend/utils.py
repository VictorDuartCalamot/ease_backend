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
from rest_framework.exceptions import AuthenticationFailed
from backend.serializers import UserSerializer

def generate_random_id(prefix):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = int(time.time())
    date_part = datetime.now().strftime('%d%m%y')
    return f"{prefix}{random_part}{timestamp}{date_part}"

#Funcion para crear filtros de query por fecha y tiempo
def filter_by_date_time(queryset,start_datetime,end_datetime, start_date, end_date, start_time, end_time):    
    '''
        Returns queries for the given datetime, date and/or time 
    '''
    # Ensure start_date is not after end_date
    if (start_date and end_date) and (start_date > end_date):
        return Response({'error': 'Start date cannot be after end date.'}, status=status.HTTP_400_BAD_REQUEST)

    if (start_time and end_time) and (start_time > end_time):
        return Response({'error': 'Start time cannot be after end time.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if start_datetime and end_datetime and start_datetime > end_datetime:
        return Response({'error': 'Start datetime cannot be after end datetime.'}, status=status.HTTP_400_BAD_REQUEST)
    
    datetime_query = Q()
    if start_datetime or end_datetime:
        if start_datetime is not None and end_datetime is not None:
            datetime_query &= Q(creation_datetime__range=[start_datetime, end_datetime])
        elif start_datetime is not None:
            datetime_query &= Q(creation_datetime__gte=start_datetime)
        elif end_datetime is not None:   
            datetime_query &= Q(creation_datetime__lte=end_datetime) 
               
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
    combined_query = datetime_query & date_query & time_query
    return queryset.filter(combined_query)

#Funcion para recuperar el usuario utilizando el email)
def getUserObjectByEmail(email):
    '''Returns User Object by email'''    
    try:
        user = User.objects.get(email=email)    
    except ObjectDoesNotExist:
        # Handle the case where the user with the provided email does not exist
        raise AuthenticationFailed(_('Invalid username or password'), code='invalid_credentials')    
    return UserSerializer(user).data