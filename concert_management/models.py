from django.db import models

# Create your models here.
class Concert(models.Model):  # Use singular for model names
    concert_name = models.CharField(max_length=255, null=False, blank=False)  # `required` removed
    date_time = models.DateTimeField(null=False, blank=False)  # For date and time of the concert
    venue = models.TextField(max_length=500, null=False, blank=False)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)  # Ensure proper precision for price
    available_tickets = models.PositiveIntegerField(null=False, blank=False)

    class Meta:
        ordering = ['date_time']  # Order by date_time

    def __str__(self):
        return self.concert_name
