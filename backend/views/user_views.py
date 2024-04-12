
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status,viewsets
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from backend.serializers import UserSerializerWithToken, UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed
from backend.models import AuthUserLogs
from backend.serializers import AuthUserLogsSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from datetime import datetime,timedelta
from django.utils import timezone
from backend.utils import filter_by_date_time, getUserObjectByEmail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from backend.permissions import PermissionLevel

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self,attrs):        
        emailToLower = attrs.get('username', '').strip().lower()                 
        userObject = getUserObjectByEmail(emailToLower)
        print(userObject)
        if (userObject.get('is_active') == False):
            return Response({'detail':'The account is blocked. Contact your administrator for further information.'},status=status.HTTP_403_FORBIDDEN, )
        try:                                
            #emailToLower = attrs.get('username', '').strip().lower()  
            attrs['username'] = emailToLower 
            data = super().validate(attrs)                                                                        
            serializer = UserSerializerWithToken(self.user).data            
            for k, v in serializer.items():
                data[k] = v             
            AuthUserLogsListView.createLogWithLogin(self.context['request'].data.get('os'),True,self.user.id)
            print(f'Inicio de sesión exitoso para el usuario: {self.user.username}')
            return data
        except AuthenticationFailed as e:            
            AuthUserLogsListView.createLogWithLogin(self.context['request'].data.get('os'),False,userObject.get('id'))                        
            blockUser(userObject.get('id'))
            print('Intento de inicio de sesión fallido')            
            raise ValidationError(detail=str(e),status=status.HTTP_400_BAD_REQUEST)
            

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
        validate_password(password)
    except ValidationError as e:
        return Response(e,status=status.HTTP_400_BAD_REQUEST)
        
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

def blockUser(userID):
    '''Block user (Is_Active field to False)'''
    userObject = User.objects.get(id=userID)
    currentDate = datetime.now()
    three_minutes_ago = currentDate - timedelta(minutes=3)

    # Convert the date and time to strings in ISO format and extract date and time separately
    new_date = three_minutes_ago.date().isoformat()
    new_time = three_minutes_ago.time().isoformat()[:8]
    query = AuthUserLogs.objects.filter(user=userID,creation_date=new_date,creation_time__range=[new_time, currentDate.time()],successful=False)
    if (query.count() >=3):
        print('Ha sobrepasado los logins fallidos posibles ! ! !')
        userObject.is_active = False                                          
        userObject.save()
        print('Saved??!!')
        return Response({'detail':'The account has been blocked because of several unsuccessful login attempts.'},status=status.HTTP_403_FORBIDDEN, )
        
    
class AuthUserLogsListView(viewsets.ModelViewSet):
    queryset = AuthUserLogs.objects.all()
    serializer_class = AuthUserLogsSerializer
    permission_classes = [IsAuthenticated]

    #@permission_classes(permission_classes=[IsAuthenticated, IsAdminUser])
    def get(self, request):
        '''
            Get to retrieve data filtered by dates 
        '''
        # Get query parameters for date range
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_time_str = request.query_params.get('start_time')
        end_time_str = request.query_params.get('end_time')                

        # Convert date strings to datetime objects, handling potential errors
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else timezone.now().date()
            start_time = datetime.strptime(start_time_str, '%H:%M:%S').time() if start_time_str else None
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time() if end_time_str else None
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
              
        authUserLog = filter_by_date_time(AuthUserLogs.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)        
        # Serialize the authUserLog
        serializer = AuthUserLogs.serializer(authUserLog, many=True)        
        # Return a JSON response containing the serialized authUserLog
        return Response(serializer.data, status=status.HTTP_200_OK)
    def createLogWithLogin(OS,isSuccess,user_id):
        print(OS,isSuccess,user_id)
        # Get the current date and time
        date = datetime.now()
        # Convert the date and time to string in ISO format and extract date and time separately
        new_date = date.isoformat()[:10]
        new_time = date.isoformat()[11:19]
        data = {             
            'user': user_id,
            'creation_date': new_date,
            'creation_time': new_time,
            'platform_OS': OS,
            'successful': isSuccess,
            'description': '',
        }                
        if isSuccess:
            data['description'] = 'Login Successful'
                                  
        else:            
            data['description'] = 'Login Failed'
            
        serializer = AuthUserLogsSerializer(data=data)
        if serializer.is_valid():                
                serializer.save()  
        return         
    #@permission_classes(IsAuthenticated)
    def create(self, request, *args, **kwargs):  
            #Post request to create new income object
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
            authUserLog = AuthUserLogs.objects.get(id=pk)
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
            #Update log object with specified PK
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


class SuperAdminManagementListView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,PermissionLevel]

    def getAllUsers(self,request):
        '''Get all users'''
        try:
            users = User.objects.all()
            #print(users)
            serializer = UserSerializerWithToken(users, many=True)
            #print(serializer.data)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def createUserWithRoles(self,request):
        '''Create user with role'''        
        #print(request.data,request.user)
        data = request.data
        email = (data['email']).strip().lower()
        name = (data['name']).strip()
        last_name = (data['last_name']).strip()
        password = (data['password']).strip()
        if data['is_staff'] is not None:
            is_staff = data['is_staff']
        else:
            is_staff = False
        if data['is_superuser'] is not None:
            is_superuser = data['is_superuser']
        else:
            is_superuser = False
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(e,status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create(
                first_name=name,
                last_name=last_name,
                username=email,
                email=email,
                is_staff=is_staff,  # Default to False if not provided
                is_superuser=is_superuser,  # Default to False if not provided
                password=make_password(password)
            )
            print(user)
            serializer = UserSerializerWithToken(user, many=False)
            print(f'Usuario registrado con éxito: {email}.')
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

class SuperAdminManagementDetailView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,PermissionLevel]

    def deleteUser(self,request,pk):        
        '''Being a superuser delete users from the database'''        
        try:              
            user = User.objects.get(id=pk)             
            user.delete()                                  
            return Response("User deleted successfully", status=status.HTTP_204_NO_CONTENT)        
        except User.DoesNotExist:
                return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        
    def updateUser(self,request,pk):
        '''Being a superuser update user from the database'''
        try:
            user = User.objects.get(id=pk)                        
            serializer = UserSerializerWithToken(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except User.DoesNotExist:
                return Response("User not found", status=status.HTTP_404_NOT_FOUND)

