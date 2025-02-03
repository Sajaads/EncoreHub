# models.py
from django.db import models
from django.contrib.auth.models import User
from concert_management.models import Concert
#for generating qr code based on need
import qrcode
import io
import base64

class TicketBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    tickets_booked = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.concert.concert_name} ({self.tickets_booked} tickets)"
    
    #generate qr code for the ticket
    def generate_qr_code(self):
        """
        Generates a QR code containing booking details and returns it as a base64-encoded image.
        """
        # Data to encode in the QR code
        qr_data = f"User: {self.user.username}\nConcert: {self.concert.concert_name}\nDate: {self.concert.date_time}\nVenue: {self.concert.venue}\nTickets: {self.tickets_booked}"

        #generate the qr code
        qr = qrcode.make(qr_data)

        #save the qr code as an image in buffer
        qr_image = io.BytesIO() #this creates a BytesIO object that we can use to store the image
        qr.save(qr_image, format='PNG') #save the qr code as a PNG image in the BytesIO object
        qr_image.seek(0) #move the cursor to the beginning of the BytesIO object because it is at the end after saving the image

        qr_base64 = base64.b64encode(qr_image.getvalue()).decode() #encode the image as base64 and decode it to a string

        return f"data:image/png;base64,{qr_base64}" #return the base64-encoded image as a string
