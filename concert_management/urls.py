from django.urls import path
from . import views

urlpatterns = [
    path('', views.retrieve_concerts, name='list_concerts'),
    path('create_concert/', views.create_concert, name='create_concert'),
    path('update_concert/<int:pk>/', views.update_concert, name='update_concert'),
    path('delete_concert/<int:pk>/', views.delete_concert, name='delete_concert'),
    path('api/visits/', views.get_visit_data, name='get_visits'),
    path('visit-analytics/', views.visit_analytics, name='visit_analytics'),
]
