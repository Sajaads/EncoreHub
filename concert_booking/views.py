from pyexpat.errors import messages
import re
import unicodedata
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TicketBooking
from concert_management.models import Concert
from django.urls import reverse
#for pdf generation
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO

@login_required(login_url='/login/')
def book_ticket(request, pk):
    concert = get_object_or_404(Concert, pk=pk)

    if request.method == "POST":
        try:
            tickets_booked = int(request.POST.get("tickets_booked", 0))

            if tickets_booked <= 0:
                return render(request, 'book_ticket.html', {
                    'concert': concert,
                    'error': 'Please book at least one ticket.'
                })

            # Ensure the user does not book more than 3 tickets for this concert
            existing_booking = TicketBooking.objects.filter(user=request.user, concert=concert).first()
            if existing_booking:
                total_tickets = existing_booking.tickets_booked + tickets_booked
                if total_tickets > 3:
                    return render(request, 'book_ticket.html', {
                        'concert': concert,
                        'error': 'You cannot book more than 3 tickets for this concert.'
                    })
                else:
                    existing_booking.tickets_booked = total_tickets
                    existing_booking.save()
            else:
                if tickets_booked > 3:
                    return render(request, 'book_ticket.html', {
                        'concert': concert,
                        'error': 'You cannot book more than 3 tickets for this concert.'
                    })
                TicketBooking.objects.create(
                    user=request.user,
                    concert=concert,
                    tickets_booked=tickets_booked
                )

            # Reduce the available tickets
            if concert.available_tickets < tickets_booked:
                return render(request, 'book_ticket.html', {
                    'concert': concert,
                    'error': 'Not enough tickets available.'
                })

            concert.available_tickets -= tickets_booked
            concert.save()

            #genenrate the qr code after succesfull booking
            booking = TicketBooking.objects.filter(user=request.user, concert=concert).first()
            qr_code = booking.generate_qr_code()

            return render(request, 'book_ticket.html', {
                'concert': concert,
                'success': f'Successfully booked {tickets_booked} tickets!',
                'qr_code': qr_code,
            })

        except ValueError:
            return render(request, 'book_ticket.html', {
                'concert': concert,
                'error': 'Invalid ticket count. Please enter a valid number.'
            })
        except IntegrityError:
            return render(request, 'book_ticket.html', {
                'concert': concert,
                'error': 'An unexpected error occurred while booking your tickets. Please try again.'
            })

    return render(request, 'book_ticket.html', {'concert': concert})

@login_required
def show_bookings(request):
    """
    Display all the concerts booked by the logged-in user, including the user's first name, 
    concert name, date and time, and the number of tickets booked.
    """
    bookings = TicketBooking.objects.filter(user=request.user).select_related('concert')
    user_first_name = request.user.first_name
    return render(request, 'show_bookings.html', {
        'bookings': bookings,
        'user_first_name': user_first_name,
    })


# Helper function to check if the user is a superuser
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)  # Ensures only superusers can access this view
def view_concert_bookings(request, concert_id):
    # Get the concert details
    concert = get_object_or_404(Concert, id=concert_id)

    # Fetch all bookings for this concert
    bookings = TicketBooking.objects.filter(concert=concert).select_related('user')

    context = {
        'concert': concert,
        'bookings': bookings,
    }

    return render(request, 'view_concert_bookings.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(TicketBooking, id=booking_id)
    concert = booking.concert

    # If the user is a superuser, delete all bookings for this user for this concert
    if request.user.is_superuser:
        user_bookings = TicketBooking.objects.filter(user=booking.user, concert=concert)
        tickets_to_return = sum([b.tickets_booked for b in user_bookings])
        concert.available_tickets += tickets_to_return
        concert.save()
        user_bookings.delete()

        return render(request, 'redirect_modal.html', {
            'message': f"All bookings for {booking.user.username} for {concert.concert_name} have been cancelled.",
            'redirect_url': reverse('view_concert_bookings', kwargs={'concert_id': concert.id}),
        })

    # For regular users, cancel only their specific booking
    if booking.user != request.user:
        return render(request, '403.html', status=403)  # Render a "403 Forbidden" page

    concert.available_tickets += booking.tickets_booked
    concert.save()
    booking.delete()

    return render(request, 'redirect_modal.html', {
        'message': f"Your booking for {concert.concert_name} has been successfully cancelled.",
        'redirect_url': reverse('my_bookings'),
    })



#for admin to view all the bookings for a concert
@login_required
def view_concert_bookings(request, concert_id):
    concert = get_object_or_404(Concert, id=concert_id)
    
    # Get all bookings for this concert
    bookings = TicketBooking.objects.filter(concert=concert)
    
    return render(request, 'view_concert_bookings.html', {'concert': concert, 'bookings': bookings})

#pdf generation of tickets
# Function to generate the ticket PDF
@login_required
def generate_ticket_pdf(ticket_booking):
    # Get the base64-encoded QR code
    qr_code_base64 = ticket_booking.generate_qr_code()

    context = {
        'concert_name': ticket_booking.concert.concert_name,
        'concert_date_time': ticket_booking.concert.date_time,
        'concert_venue': ticket_booking.concert.venue,
        'tickets_booked': ticket_booking.tickets_booked,
        'user_name': ticket_booking.user.username,
        'qr_code': qr_code_base64  # Pass QR code to the template
    }
    
    # Render HTML content with the provided context
    html_content = render_to_string('ticket_pdf.html', context)
    
    # Convert HTML to PDF using xhtml2pdf (Pisa)
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def sanitize_filename(name):
    # Normalize the string to remove accents and other diacritical marks
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    # Replace any non-alphanumeric characters (except spaces and underscores) with underscores
    name = re.sub(r'[^a-zA-Z0-9 _-]', '_', name)
    return name

# View to handle ticket download
@login_required
def download_ticket(request, booking_id):
    ticket_booking = get_object_or_404(TicketBooking, id=booking_id)
    pdf = generate_ticket_pdf(ticket_booking)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    sanitized_concert_name = sanitize_filename(ticket_booking.concert.concert_name)
    response['Content-Disposition'] = f'attachment; filename="ticket_for_{sanitized_concert_name}.pdf"'
    return response

