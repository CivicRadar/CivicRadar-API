import copy
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['FullName', 'Email', 'Password', 'Type', 'Verified']
        extra_kwargs = {
            'Password': {'write_only': True}
        }

    def create(self, validated_data):
        Password = validated_data.pop('Password', None)
        instance = self.Meta.model(**validated_data)
        if Password is not None:
            instance.set_password(Password)
        instance.save()
        return instance

    def update(self, validated_data, key, value):
        new_data = copy.deepcopy(validated_data)
        new_data[key] = value
        return new_data


class UserIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'FullName', 'Email', 'Type']

class ResetPasswordRequestSerializer(serializers.Serializer):
    def validate(self, attrs):
        return super().validate(attrs)

class SetNewPasswordSerializer(serializers.Serializer):
    Password = serializers.CharField(min_length=3, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    ui64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['Password', 'token', 'ui64']

    def validate(self, attrs):
        try:
            password = attrs.pop('Password')
            token = attrs.pop('token')
            ui64 = attrs.pop('ui64')

            id=force_str(urlsafe_base64_decode(ui64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid')

            user.set_password(password)
            user.save()

            return attrs
        except:
            raise AuthenticationFailed('The reset link is invalid')

class ProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['FullName', 'Email', 'user_type', 'Picture']

    def get_user_type(self, obj):
        if obj.Type == 'Citizen':
            return 'شهروند'
        elif obj.Type == 'Mayor':
            return 'شهردار'
        elif obj.Type == 'Admin':
            return 'ادمین'
        return None