from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
#from .models import Income, Expense,auth_user_logs
from .models import Expense, Income, AuthUserLogs, Category , SubCategory

class UserSerializer(serializers.ModelSerializer):
    #name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    #isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'is_staff','is_active','is_superuser','first_name','last_name']

        #read_only_fields = ['id','_id','username','email']
    def get__id(self, obj):
        return obj.id

    #def get_isAdmin(self, obj):
    #    return obj.is_staff 
    
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'is_staff','is_active','is_superuser','token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class ExpenseSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Expense
        fields = ['id','title','description','amount','creation_date','creation_time','user','category','subCategory']
        read_only_fields = ['id']

class IncomeSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Income
        fields = ['id','title','description','amount','creation_date','creation_time','user','category','subCategory']
        read_only_fields = ['id']        


class AuthUserLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUserLogs
        fields = ['id','user','creation_date','creation_time','platform_OS','successful','description']
        read_only_fields = ['id']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id']

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'
        read_only_fields = ['id']