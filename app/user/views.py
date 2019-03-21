from rest_framework import generics

from user.serializers import UserSeralizer


class CreateUserView(generics.CreateAPIView):
    """ Create a new user """
    serializer_class = UserSeralizer
