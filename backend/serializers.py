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
    user = serializers.IntegerField(read_only=True)
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'category', 'creation_date', 'user']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        print("He entrado en el create dentro del serializer y antes de hacer el self.context")
        # Retrieve the user from the context        
        try:
            user = self.context.get('user')
            print(user)  # Verify if this prints anything
    # Add other operations with user_pk here
        except Exception as e:
            print(f"Error retrieving user_pk: {str(e)}")
                            
        print("Despues de hacer el self.context El usuario: "+ str(user_pk))
        # Add the user to the validated data before saving
        validated_data['user'] = user
        print("Despues de validated_data")
        created_object = super().create(validated_data)
        print("Object created")
        return created_object