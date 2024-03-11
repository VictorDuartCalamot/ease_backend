from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
#from .models import Income, Expense,auth_user_logs
from .models import Expense

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'creation_date', 'user']
        read_only_fields = ['id']
        
    '''def create(self, validated_data):
        # Retrieve the user from the validated data
        user = validated_data.pop('user', None)
        if user:
            # If user is present, create the Expense object with it
            expense = Expense.objects.create(user=user, **validated_data)
            return expense
        else:
            # Handle the case where user is not provided
            raise serializers.ValidationError("User data is required.")'''
    """def create(self, validated_data):
        print("He entrado en el create dentro del serializer y antes de hacer el self.context")
        # Retrieve the user from the context        
        try:
            user = validated_data.pop('user', None)
            print(user)  # Verify if this prints anything
    # Add other operations with user_pk here
        except Exception as e:
            print(f"Error retrieving user_pk: {str(e)}")
                            
        print("Despues de hacer el self.context El usuario: "+ str(user))
        # Add the user to the validated data before saving
        #validated_data['user'] = user
        print("Despues de validated_data")
        created_object = Expense.objects.create(user=user, **validated_data)
        print("Object created",str(created_object))
        return created_object"""