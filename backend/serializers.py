from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Income, Expense,auth_user_logs

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


class AuthUserLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_user_logs
        fields = ['id', 'date','successful', 'description']
        read_only_fields = ['id', 'date','successful', 'description']

class IncomeSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
    class Meta:
        model = Income
        fields = ['amount', 'category', 'creation_date', 'user']
        read_only_fields = ['user']  

    def create(self, validated_data):
        # Assign authenticated user's ID to the 'user' field
        validated_data['user_id'] = self.context['request'].user
        return super().create(validated_data)

class ExpenseSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(format="%d-%m-%Y", input_formats=['%d-%m-%Y', 'iso-8601'])
    class Meta:
        model = Expense
        #fields = ['amount', 'category', 'creation_date']
        fields = ['amount', 'category', 'creation_date', 'user']
        #fields = ['amount', 'category', 'user']
        #fields = ['amount', 'category']
        read_only_fields = ['user']  

    def create(self, validated_data):
        # Assign authenticated user's ID to the 'user' field
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



