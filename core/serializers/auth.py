from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import Family, Parent


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ["id", "name", "email", "family"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    name = serializers.CharField(max_length=100)
    family_name = serializers.CharField(max_length=100)

    def validate_email(self, value):
        """Check that email is not already registered"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # Create Django user
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        # Create family
        family = Family.objects.create(name=validated_data["family_name"])

        # Create parent profile
        parent = Parent.objects.create(
            email=validated_data["email"], name=validated_data["name"], family=family
        )

        return {"user": user, "parent": parent}


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("Account is disabled")
            data["user"] = user
        else:
            raise serializers.ValidationError("Must include email and password")

        return data
