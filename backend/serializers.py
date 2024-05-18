from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
#from .models import Income, Expense,auth_user_logs
from .models import Expense, Income, AuthUserLogs, Category , SubCategory, ChatSession,ChatMessage

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

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','username','is_staff','is_active','is_superuser','first_name','last_name']
        # Fields optional during update
        extra_kwargs = {
            'email': {'required': False},
            'is_staff': {'required': False},
            'is_active': {'required': False},
            'is_superuser': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'username':{'required': False}
        }

class ExpenseSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Expense
        fields = ['id','title','description','amount','creation_date','creation_time','user','category','subcategory']
        read_only_fields = ['id']

class ExpenseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'user', 'category', 'subcategory']
        # Fields optional during update
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'amount': {'required': False},
            'user': {'required': False},
            'category': {'required': False},
            'subcategory': {'required': False}
        }
        
class IncomeSerializer(serializers.ModelSerializer):
    #user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Income
        fields = ['id','title','description','amount','creation_date','creation_time','user','category']
        read_only_fields = ['id']        

class IncomeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['title', 'description', 'amount', 'user', 'category']
        # Fields optional during update
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'amount': {'required': False},
            'user': {'required': False},
            'category': {'required': False},
            'subcategory': {'required': False}
        }
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

class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['name','description','hexColor']
        # Fields optional during update
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'hexColor': {'required': False},         
        }

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'
        read_only_fields = ['id']

class SubCategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['name','description','hexColor','category']
        # Fields optional during update
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'hexColor': {'required': False},
            'category': {'required': False},            
        }
class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'is_active', 'created_at', 'customer', 'admin']        
        
        
class ChatMessageSerializer(serializers.ModelSerializer):  
    user = serializers.StringRelatedField()  # Use StringRelatedField for simple representation of related objects

    class Meta:
        model = ChatMessage
        fields = ['user', 'message','timestamp']