from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Student, Employer
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "student_id",
            "degree",
            "year_of_study",
            "cv",
            "cover_letter",
        ]


class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employer
        fields = [
            "id",
            "user",
            "employer_id",
            "company_name",
            "industry",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "first_name", "last_name", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == "student":
            Student.objects.update_or_create(
                user=user,
                defaults={
                    "student_id": self.initial_data.get("student_id"),
                    "degree": self.initial_data.get("degree"),
                    "year_of_study": self.initial_data.get("year_of_study"),
            },
    )
        elif user.role == "employer":
            Employer.objects.update_or_create(
                user=user,
                defaults={
                    "employer_id": f"EMP{user.id}",
                    "company_name": self.initial_data.get("company_name"),
                    "industry": self.initial_data.get("industry"),
                },
            )

        return user
    
    def validate(self, data):
        if data.get("role") == "student":
            if not data.get("first_name") or not data.get("last_name"):
                raise serializers.ValidationError("First name and last name are required for students.")
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # use Django's built-in password validators
        validate_password(value)
        return value

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is not correct."})
        return data

    def save(self, **kwargs):
        user: User = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is registered with this email.")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid UID"})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        return self.user



class StudentCVUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["cv"]

    def update(self, instance, validated_data):
        instance.cv = validated_data.get("cv", instance.cv)
        instance.save()
        return instance
