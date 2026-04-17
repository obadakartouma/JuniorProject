# accounts/serializers.py - النسخة المحدثة الكاملة
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import CustomUser

# **سيريالايزر جديد لتسجيل المتعلمين**
class RegisterLearnerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password],style={'input_type': 'password'},min_length=8)
    password2 = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', )
    
    # التحقق من البيانات المدخلة من المستخدم validate
    def validate(self, attrs):
        #التحقق من تطابق كلمات المرور
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": ("كلمات المرور غير متطابقة")}
            )
        # التحقق من البريد الإلكتروني validate_email
        try:
            validate_email(attrs['email'])
        except ValidationError:
            raise serializers.ValidationError(
                {"email": ("البريد الإلكتروني غير صالح")}
            )
        # التحقق من وجود البريد مسبقاً
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": ("البريد الإلكتروني موجود مسبقاً")}
            )
        # إزالة تأكيد كلمة المرور من البيانات
        attrs.pop('password2')
        # تعيين نوع المستخدم كمتعلم
        attrs['user_type'] = 'learner'
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

# **سيريالايزر جديد لتسجيل المشرفين**
class RegisterAdminSerializer(serializers.ModelSerializer):
    """سيريالايزر خاص بإنشاء المشرفين """
    # **حقول كلمة المرور وتأكيدها**
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        min_length=8
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', )
    
    #تحقق من البيانات المدخلة من المستخدم
    def validate(self, attrs):
        # التحقق من تطابق كلمات المرور
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": ("كلمات المرور غير متطابقة")}
            )
        # التحقق من البريد الإلكتروني
        try:
            validate_email(attrs['email'])
        except ValidationError:
            raise serializers.ValidationError(
                {"email": ("البريد الإلكتروني غير صالح")}
            )
        # التحقق من وجود البريد مسبقاً
        if CustomUser.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": ("البريد الإلكتروني موجود مسبقاً")}
            )
        # إزالة تأكيد كلمة المرور من البيانات
        attrs.pop('password2')
        # تعيين نوع المستخدم كمشرف
        attrs['user_type'] = 'admin'
        return attrs
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

# **سيريالايزر جديد لتسجيل الدخول**
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    # التحقق من بيانات الدخول
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # التحقق من وجود البيانات
        if not email or not password:
            raise serializers.ValidationError(
                ("يجب إدخال البريد الإلكتروني وكلمة المرور")
            )
        # التحقق من البريد الإلكتروني
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError(
                {"email": ("البريد الإلكتروني غير صالح")}
            )
        
        # المصادقة
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError(
                ("بيانات الدخول غير صحيحة")
            )
        if not user.is_active:
            raise serializers.ValidationError(
                ("الحساب غير مفعل")
            )
        attrs['user'] = user
        return attrs

# **سيريالايزر جديد لعرض وتحديث ملف المستخدم**
class ProfileSerializer(serializers.ModelSerializer):
    # **خصائص ديناميكية بناءً على نوع المستخدم**
    enrolled_courses_count = serializers.SerializerMethodField()
    enrolled_courses_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'user_type', 'date_joined', 'last_login', 'enrolled_courses_count', 'enrolled_courses_titles')  
        read_only_fields = ('id', 'user_type', 'date_joined', 'last_login')
    
    # التحقق من تحديث البريد الإلكتروني
    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(("البريد الإلكتروني موجود مسبقاً"))
        return value
    
    # **دالة ديناميكية: الحصول على عدد المسارات (للمتعلمين فقط)**
    def get_enrolled_courses_count(self, obj):
        if obj.is_learner:
            return obj.get_enrolled_courses_count()
        return None  # إرجاع None للمشرفين
    
    # **دالة ديناميكية: الحصول على قائمة المسارات (للمتعلمين فقط)**
    def get_enrolled_courses_titles(self, obj):
        if obj.is_learner:
            return obj.get_enrolled_courses_list()
        return None  # إرجاع None للمشرفين
    
    # **تجاوز طريقة العرض: حذف الحقول الفارغة**
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # إزالة الحقول ذات القيمة None (خاصة للمشرفين)
        if representation.get('enrolled_courses_count') is None:
            representation.pop('enrolled_courses_count', None)
        if representation.get('enrolled_courses_titles') is None:
            representation.pop('enrolled_courses_titles', None)
        return representation