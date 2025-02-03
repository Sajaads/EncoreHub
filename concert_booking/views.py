from pyexpat.errors import messages
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import TicketBooking
from concert_management.models import Concert
from django.urls import reverse

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

            return render(request, 'book_ticket.html', {
                'concert': concert,
                'success': f'Successfully booked {tickets_booked} tickets!'
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