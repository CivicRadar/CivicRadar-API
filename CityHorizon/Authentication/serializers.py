from rest_framework import serializers
from twisted.python.formmethod import Password

from .models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['FullName', 'Email', 'Password']
        extra_kwargs = {
            'Password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('Password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance