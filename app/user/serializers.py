from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSeralizer(serializers.ModelSerializer):
    """ Serailizes user objects """

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
