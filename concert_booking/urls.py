# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('book_ticket/<int:pk>/', views.book_ticket, name='book_ticket'),
    path('my-bookings/', views.show_bookings, name='my_bookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('concerts/all_bookings/<int:concert_id>/', views.view_concert_bookings, name='view_concert_bookings'),
]
