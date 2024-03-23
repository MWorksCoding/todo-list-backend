from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TodoItem
from .serializers import TodoItemSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class TodoItemsView(APIView):
    authentication_classes = [TokenAuthentication] # token must be send every time; activate / deactivate authorization
    permission_classes = [IsAuthenticated] # token must be send every time; activate / deactivate authorization

    def get(self, request, format=None):
        print('request' , request)
        print('request' , request.user)
        # todos = TodoItem.objects.all() # get all todos from all users!
        todos = TodoItem.objects.filter(author=request.user) # get only todos from user
        print('todos' , todos)
        serializer = TodoItemSerializer(todos, many=True)
        print('serializer' , serializer)
        print('serializer' , serializer.data)
        return Response(serializer.data)

class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # serializer takes the incoming data (user / password)
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        # check validation
        serializer.is_valid(raise_exception=True)
        # get user from validated data
        user = serializer.validated_data['user']
        # create token or get token if user already logged in
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })  