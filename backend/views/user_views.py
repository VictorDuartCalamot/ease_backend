
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status,viewsets
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from backend.serializers import UserSerializerWithToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from backend.models import AuthUserLogs
from backend.serializers import AuthUserLogsSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from datetime import datetime
from django.utils import timezone

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)            
            serializer = UserSerializerWithToken(self.user).data
            for k, v in serializer.items():
                data[k] = v

            username = self.user.username
            print(f'Inicio de sesión exitoso para el usuario: {username}')
            return data
        except AuthenticationFailed:
            print('Intento de inicio de sesión fallido')
            raise
            

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def registerUser(request):
    data = request.data
    email = (data['email']).strip().lower()
    name = (data['name']).strip()
    last_name = (data['last_name']).strip()
    password = (data['password']).strip()

    try:
        user = User.objects.create(
            first_name=name,
            last_name=last_name,
            username=email,
            email=email,
            password=make_password(password)
        )
        serializer = UserSerializerWithToken(user, many=False)
        print(f'Usuario registrado con éxito: {email}.')
        return Response(serializer.data)
    except Exception as e:
        print(f'Error al registrar usuario: {str(e)}.')
        message = {'detail': 'La información proporcionada no es válida, revisa el formato de tu correo'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


class AuthUserLogsListView(viewsets.ModelViewSet):
    queryset = AuthUserLogs.objects.all()
    serializer_class = AuthUserLogsSerializer
    #permission_classes = [IsAuthenticated,IsAdminUser]

    @permission_classes(IsAuthenticated, IsAdminUser)
    def get(self, request):
        '''
            Get to retrieve data filtered by dates 
        '''   
        #print('Inside get request')
        # Get query parameters for date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        #print(start_date_str,'-',end_date_str)

        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure start_date is not after end_date
        if start_date and end_date and start_date > end_date:
            return Response({'error': 'Start date cannot be after end date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter authUserLog based on date range
        authUserLog = AuthUserLogs.objects.filter(user=request.user.id)
        
        if start_date is not None and end_date is not None:
            #print('Inside both fullfilled values')
            if start_date == end_date:
                #print('Both are the same dates')
                authUserLog = AuthUserLogs.filter(creation_date=start_date)
            else:
                #print('Different dates, range')
                authUserLog = authUserLog.filter(creation_date__range=[start_date, end_date])
        elif start_date is not None:
            #print('Start date is fullfilled')
            authUserLog = authUserLog.filter(creation_date__gte=start_date)
        elif end_date is not None:   
            #print('End date is fullfilled')         
            authUserLog = authUserLog.filter(creation_date__lte=end_date)
        #print('Filtered authUserLog:', authUserLog)        
        # Serialize the authUserLog
        serializer = AuthUserLogs.serializer(authUserLog, many=True)        
        # Return a JSON response containing the serialized authUserLog
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @permission_classes(IsAuthenticated)
    def create(self, request, *args, **kwargs):  
        '''
            Post request to create new income object
        '''                      
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)            
        #Insert userID into the request.data array
        request.data['user'] = request.user.id                        
        # Create a serializer instance with the data in the array
        serializer = AuthUserLogsSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the income object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class AuthUserLogsDetailView(viewsets.ModelViewSet):
    queryset = AuthUserLogs.objects.all()
    serializer_class = AuthUserLogsSerializer
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self,request,pk):
        
           #Get single income object with specified PK
           
        try:
        # Retrieve the income object based on the primary key (pk) and user
            authUserLog = AuthUserLogs.objects.get(id=pk, user=request.user.id)
        except authUserLog.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            return Response({'error': 'Income not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        #print(income)
        serializer = AuthUserLogsSerializer(authUserLog) 
        #print(serializer.data)        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        
            #Delete income object with specified PK 

        #print('Inside delete request')
        try:
            authUserLog = AuthUserLogs.objects.get(pk=pk)
            #print(income)
            authUserLog.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AuthUserLogs.DoesNotExist:
            return Response("Income not found.", status=status.HTTP_404_NOT_FOUND)
    
    def update(self,request,*args,**kwargs):
        '''
            Update log object with specified PK
        '''
        authUserLog = self.get_object()
        request.data['user'] = authUserLog.user
        # Serialize the income data with the updated data from request
        serializer = AuthUserLogsSerializer(authUserLog, data=request.data)
        
        # Validate the serializer data
        if serializer.is_valid():
            # Save the updated income object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Return error response if serializer data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
