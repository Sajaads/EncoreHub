# models.py
from django.db import models
from django.contrib.auth.models import User
from concert_management.models import Concert

class TicketBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    tickets_booked = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.concert.concert_name} ({self.tickets_booked} tickets)"

