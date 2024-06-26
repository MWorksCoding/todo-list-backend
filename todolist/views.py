from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TodoItem
from .serializers import TodoItemSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class TodoItemsView(APIView):
    authentication_classes = [TokenAuthentication] # token must be send every time; activate / deactivate authorization
    permission_classes = [IsAuthenticated] # token must be send every time; activate / deactivate authorization

    def get(self, request, format=None):
        # todos = TodoItem.objects.all() # get all todos from all users!
        todos = TodoItem.objects.filter(author=request.user) # get only todos from user
        serializer = TodoItemSerializer(todos, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        title = request.data.get('title')
        if title is None:
            return Response({"error": "Todo is missing"})
        author = request.user
        new_todo = TodoItem.objects.create(title=title, author=author)
        serializer = TodoItemSerializer(new_todo)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        print('pk:' , pk)
        try:
            todo = TodoItem.objects.get(pk=pk, author=request.user)
        except TodoItem.DoesNotExist:
            return Response({"error": "TodoItem does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if todo.author != request.user:
            return Response({"error": "You are not authorized to update this todo item"}, status=status.HTTP_403_FORBIDDEN)
        title = request.data.get('title')
        if title is None:
            return Response({"error": "Title is missing"}, status=status.HTTP_400_BAD_REQUEST)
        todo.title = title
        todo.checked = request.data.get('checked', todo.checked)
        todo.save()
        serializer = TodoItemSerializer(todo)
        return Response(serializer.data)
    
    def delete(self, request, pk, format=None):
        try:
            todo = TodoItem.objects.get(pk=pk)
        except TodoItem.DoesNotExist:
            return Response({"error": "TodoItem does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if todo.author != request.user:
            return Response({"error": "You are not authorized to delete this todo item"}, status=status.HTTP_403_FORBIDDEN)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

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
        

class LogoutView(APIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        request.auth.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)