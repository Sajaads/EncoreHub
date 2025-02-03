from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='api_signup'),
    path('login/', views.login, name = 'api_login'), 
    path('api_create/', views.api_create, name = 'api_create'),
    path('api_retrieve/', views.api_retrieve, name = 'api_retrieve'),
    path('api_update/<int:pk>/', views.api_update, name = 'api_update'),
    path('api_delete/<int:pk>/', views.api_delete, name = 'api_delete'),
]
