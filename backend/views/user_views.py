
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from rest_framework import status,viewsets
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from backend.serializers import UserSerializerWithToken, UserSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import AuthenticationFailed,PermissionDenied
from backend.models import AuthUserLogs
from backend.serializers import AuthUserLogsSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from datetime import datetime,timedelta
from django.utils import timezone
from backend.utils import filter_by_date_time, filter_by_datetime_with_custom_field, getUserObjectByEmail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from backend.permissions import HasEnoughPerms,HasMorePermsThanUser
from rest_framework.authtoken.models import Token
from backend.models import BlacklistedToken
from django.contrib.auth.hashers import check_password
'''
Este archivo es para las vistas de usuarios, admins y superadmins
'''
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # This login function validates the username(email) and password, to reduce problems, the username gets put in lowercase,
    # then we check if the user is blocked or not. Even if it is or not we create a new log and in case there are too many failed login attempts, the account will get blocked.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    # Funcion para login que valida el username y el password, el username lo pongo en minusculas para no tener problemas con caracteres.
    # Compruebo que el usuario no este bloqueado, y una vez todo esta correcto da login. 
    # Tanto si el login es correcto como no se creara un log de inicio de sesion.
    def validate(self,attrs):        
        emailToLower = attrs.get('username', '').strip().lower()                 
        userObject = getUserObjectByEmail(emailToLower)
        if not userObject['is_active']:
            raise PermissionDenied('The account is blocked. Contact your administrator for further information.')
        try:                                              
            attrs['username'] = emailToLower 
            data = super().validate(attrs)                                                                        
            serializer = UserSerializerWithToken(self.user).data            
            for k, v in serializer.items():
                data[k] = v             
            AuthUserLogsListView.createLogWithLogin(self.context['request'].data.get('os'),True,self.user.id)
            return data
        except AuthenticationFailed as e:            
            AuthUserLogsListView.createLogWithLogin(self.context['request'].data.get('os'),False,userObject.get('id'))                        
            blockUser(userObject.get('id'))
            raise AuthenticationFailed('Credentials are incorrect.')                     
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


#Function to register a user and create a token
#Funcion para registrar un usuario y crear un token.
@api_view(['POST'])
def registerUser(request):
    '''Register new user'''
    data = request.data
    email = (data['email']).strip().lower()
    name = (data['first_name']).strip()
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
        return Response(serializer.data)
    except Exception as e:
        message = {'detail': 'La información proporcionada no es válida, revisa el formato de tu correo'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''Logouts current user and blacklists the token'''
        token = request.auth

        if token:
            # Blacklist the token
            BlacklistedToken.objects.create(token=token)

            # Delete the token
            request.auth = None

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No token found."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    '''Change password for the current user'''
    try:
        user_obj = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    current_password = request.data.get("current_password", "").strip()
    new_password = request.data.get("new_password", "").strip()

    # Check if the provided current password matches the hash with the one in the database
    if not check_password(current_password, user_obj.password):
        raise ValidationError('Incorrect current password.')

    # Set the new password and save the user object
    user_obj.set_password(new_password)
    user_obj.save()
    return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
    
# Funtion to block the user.
# In this function when the user has tried to log-in more than 3 times in a range of 3 minutes, the account will be blocked (field "is_active" = false )
def blockUser(userID):
    '''Block user (Is_Active field to False)'''
    userObject = User.objects.get(id=userID)
    currentDate = datetime.now()
    three_minutes_ago = currentDate - timedelta(minutes=3)
    # Transform the date and time to strings in ISO format and extract date and time separately    
    new_date = three_minutes_ago.date().isoformat()
    new_time = three_minutes_ago.time().isoformat()[:8]
    query = AuthUserLogs.objects.filter(user=userID,creation_date=new_date,creation_time__range=[new_time, currentDate.time()],successful=False)
    if (query.count() >=3):        
        userObject.is_active = False                                          
        userObject.save()        
        return Response({'message':'The account has been blocked because of several unsuccessful login attempts.'},status=status.HTTP_403_FORBIDDEN, )
        
    
class AuthUserLogsListView(viewsets.ModelViewSet):
    queryset = AuthUserLogs.objects.all()
    serializer_class = AuthUserLogsSerializer
    permission_classes = [IsAuthenticated,HasMorePermsThanUser]    
    def get(self, request):        
        '''
            Retrieve data filtered by dates 
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
            return Response({'error': 'Invalid date or time format, must be YYYY-MM-DD for date and HH:MM:SS for time. '}, status=status.HTTP_400_BAD_REQUEST)
              
        authUserLog = filter_by_date_time(AuthUserLogs.objects.filter(user=request.user.id), start_date, end_date, start_time, end_time)        
        # Serialize the authUserLog
        serializer = AuthUserLogs.serializer(authUserLog, many=True)        
        # Return a JSON response containing the serialized authUserLog
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def createLogWithLogin(OS,isSuccess,user_id):
        '''
            Creates a log with when a user tries to login
        '''        
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

    def create(self, request, *args, **kwargs): 
        '''
        Function to manually create a log
        '''                                      
        #Insert userID into the request.data array
        request.data['user'] = request.user.id                        
        # Create a serializer instance with the data in the array
        serializer = AuthUserLogsSerializer(data=request.data) 
        #Check if the serializer is valid
        if serializer.is_valid():            
            serializer.save()  # Save the log object to the database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            #print(serializer.errors)  # Print out the errors for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class AuthUserLogsDetailView(viewsets.ModelViewSet):
    queryset = AuthUserLogs.objects.all()
    serializer_class = AuthUserLogsSerializer
    permission_classes = [IsAuthenticated,HasMorePermsThanUser]

    def get(self,request,pk):
        '''
           Get single log object with specified PK
        ''' 
        try:
        # Retrieve the income object based on the primary key (pk) and user
            authUserLog = AuthUserLogs.objects.get(pk=pk)
        except authUserLog.DoesNotExist:
        # If the income object does not exist for the specified user, return a 404 Not Found response
            return Response({'error': 'Income not found.'}, status=status.HTTP_404_NOT_FOUND)                
        serializer = AuthUserLogsSerializer(authUserLog)         
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        '''Delete a log with specified PK'''                    
        try:
            authUserLog = AuthUserLogs.objects.get(pk=pk)            
            authUserLog.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AuthUserLogs.DoesNotExist:
            return Response("Income not found.", status=status.HTTP_404_NOT_FOUND)
    
    def update(self,request,*args,**kwargs):
        '''
        Update log with specified PK
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


class SuperAdminManagementListView(viewsets.ModelViewSet):    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,HasMorePermsThanUser]

    def getAllUsers(self,request):
        '''Get all users with optional parameters'''
        try:
            is_activeValue = request.query_params.get('is_active', None)
            is_staffValue = request.query_params.get('is_staff', None)
            is_superuserValue = request.query_params.get('is_superuser', None)
            start_datetime_str = request.query_params.get('start_date', None)
            end_datetime_str = request.query_params.get('end_date', None)
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S') if start_datetime_str else None
            end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S') if end_datetime_str else timezone.now()
            
            
            # Start with an initial queryset that includes all users
            users_queryset = User.objects.all()
            
            # Exclude Anonymous user
            users_queryset = users_queryset.exclude(id=1)
            
            # Apply filters based on query parameters
            if is_activeValue is not None:                              
                is_active_bool = True if is_activeValue.lower() == 'true' else False
                users_queryset = users_queryset.filter(is_active=is_active_bool)                                   
            if is_staffValue is not None:                
                is_staff_bool = True if is_staffValue.lower() == 'true' else False
                users_queryset = users_queryset.filter(is_staff=is_staff_bool)
            if is_superuserValue is not None:                
                is_staff_bool = True if is_superuserValue.lower() == 'true' else False
                users_queryset = users_queryset.filter(is_superuser=is_staff_bool)            
            # Add filtering by datetime if provided
            if start_datetime is not None or end_datetime is not None:                                
                users_queryset = filter_by_datetime_with_custom_field(users_queryset, start_datetime, end_datetime,'date_joined')                                        
            serializer = UserSerializer(users_queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
    
    def createUserWithRoles(self,request):
        '''
            Create user with role 
            SuperUser can create users with any roles
            Staff can only create users and staff             
            
        '''                
        data = request.data
        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        password = data.get('password', '').strip()
        is_staff = data.get('is_staff', False)
        is_superuser = data.get('is_superuser', False)                        
        
        if is_superuser is not None:
            if request.user.is_staff and is_superuser:
                return Response(status=status.HTTP_403_FORBIDDEN) 
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(e,status=status.HTTP_400_BAD_REQUEST)        
        try:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=email,
                email=email,
                is_staff=is_staff,  # Default to False if not provided
                is_superuser=is_superuser,  # Default to False if not provided
                is_active=True,
                password=make_password(password)
            )
            
            serializer = UserSerializerWithToken(user)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e),status=status.HTTP_400_BAD_REQUEST)

class SuperAdminManagementDetailView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,HasEnoughPerms]    

    def getSingleUser(self, request,pk):
        '''Get data from single user'''
        try:
            user = User.objects.exclude(id=1)
            user = User.objects.get(id=pk) 
            serializer = UserSerializer(user)                    
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND)
    
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
            serializer = UserSerializer(user)
            data = serializer.data
            if request.data['first_name'] is not None:data['first_name'] = request.data['first_name']
            if request.data['last_name'] is not None:data['last_name'] = request.data['last_name']
            if request.data['email'] is not None:data['email'] = request.data['email']
            if request.data['is_staff'] is not None:data['is_staff'] = request.data['is_staff']
            if request.data['is_superuser'] is not None:data['is_superuser'] = request.data['is_superuser']
            if request.data['is_active'] is not None:data['is_active'] = request.data['is_active']
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except User.DoesNotExist as error:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

    def blockUnblockUser(self,request,pk):        
        '''Being a superuser update user from the database'''
        try:                     
            user = User.objects.get(id=pk) 
            serializer = UserSerializer(user)                    
            data = serializer.data            
            data['is_active'] = request.data['is_active']               
            serializer = UserSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        
        except User.DoesNotExist as error:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
