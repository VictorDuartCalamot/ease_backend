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

def generate_random_id(prefix):
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    timestamp = int(time.time())
    date_part = datetime.now().strftime('%d%m%y')
    return f"{prefix}{random_part}{timestamp}{date_part}"


def filter_by_date_time(queryset, start_date, end_date, start_time, end_time):
    print('Entro para filtrar 2')
    # Ensure start_date is not after end_date
    if (start_date and end_date) and (start_date > end_date):
        return Response({'error': 'Start date cannot be after end date.'}, status=status.HTTP_400_BAD_REQUEST)

    if (start_time and end_time) and (start_time > end_time):
        return Response({'error': 'Start time cannot be after end time.'}, status=status.HTTP_400_BAD_REQUEST)
    
    print('2nda phase')
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
        print('Date Query: ', date_query)
        
    print('despues date query')
        
    # Filter based on time range
    time_query = Q()
    if start_time or end_time:
        if start_time is not None and end_time is not None:
            if start_time == end_time:
                time_query &= Q(creation_time=start_time)
            else:
                time_query &= Q(creation_time__range=[start_time, end_time])
        elif start_date is not None:
            time_query &= Q(creation_time__gte=start_time)
        elif end_date is not None:   
            time_query &= Q(creation_time__lte=end_time)
        
    print('Time Query: ', time_query)
    print('Hora: ', start_time, end_time)
    print('despues time')
        
    # Apply combined date and time filtering
    combined_query = date_query & time_query
    print(combined_query)
    print(queryset.filter(combined_query))
    return queryset.filter(combined_query)