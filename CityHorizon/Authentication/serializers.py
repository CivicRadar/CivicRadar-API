from rest_framework import serializers

from .models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['FullName', 'Email', 'Password', 'Type']
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

class UserIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'FullName', 'Email', 'Type']