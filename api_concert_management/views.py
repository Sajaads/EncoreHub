from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework import status
from user_management.forms import CustomUserCreationForm
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from concert_management.forms import ConcertForm
from concert_management.models import Concert
from .serializers import ConcertSerializer

# Custom permission to check if the user is an admin
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff  # Checks if the user is marked as staff (admin)

# Publicly accessible endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    form = CustomUserCreationForm(data=request.data)
    if form.is_valid():
        user = form.save(commit=False)
        user.first_name = form.cleaned_data.get('name')
        user.save()
        return Response('User created successfully', status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'Token': token.key}, status=status.HTTP_200_OK)

# Admin-only endpoint to create concerts
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_create(request):
    form = ConcertForm(data=request.data)
    if form.is_valid():
        concert = form.save()
        return Response(f'Concert created successfully with id: {concert.id}', status=status.HTTP_201_CREATED)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

# Authenticated users can retrieve concert details
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_retrieve(request):
    concerts = Concert.objects.all()
    serializer = ConcertSerializer(concerts, many=True)
    return Response(serializer.data)

# Admin-only endpoint to update a concert
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_update(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    form = ConcertForm(request.data, instance=concert)
    if form.is_valid():
        form.save()
        serializer = ConcertSerializer(concert)
        return Response(serializer.data)
    return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

# Admin-only endpoint to delete a concert
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def api_delete(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    concert.delete()
    return Response('Concert deleted successfully', status=status.HTTP_204_NO_CONTENT)
