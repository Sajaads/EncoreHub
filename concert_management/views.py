from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import ConcertForm
from .models import Concert

from django.http import JsonResponse
from encorehub.settings import VISITS_COLLECTION
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
# Create your views here.
@login_required
def create_concert(request):
    if request.method == 'POST':
        form = ConcertForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_concerts')
    else:
        form = ConcertForm()  # Pass an empty form for GET requests
    return render(request, 'create_concert.html', {'form': form})


@login_required
def retrieve_concerts(request):
    concert_list = Concert.objects.all()
    paginator = Paginator(concert_list, 10)  # Show 15 concerts per page
    page_number = request.GET.get('page')
    concerts = paginator.get_page(page_number)
    return render(request, 'list_concerts.html', {'concerts': concerts})

@login_required
def update_concert(request, pk):
    concert = get_object_or_404(Concert, pk= pk)
    if request.method == 'POST':
        form = ConcertForm(request.POST, instance=concert)
        if form.is_valid:
            form.save()
            return redirect('list_concerts')
    else:
        form = ConcertForm(instance=concert)
    return render(request, 'update_concert.html', {'form': form})

@login_required
def delete_concert(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    if request.method == 'POST':
        concert.delete()
        return redirect('list_concerts')
    return render(request, 'delete_concert.html', {'concert':concert})

def admin_required(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(admin_required)
def visit_analytics(request):
    """Render the visit analytics page (admin only)."""
    return render(request, "visit_analytics.html")

def get_visit_data(request): # Use the existing connection
    visits_collection = VISITS_COLLECTION

    # Get the start and end date from the request parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # If no dates provided, default to last 7 days
    if not start_date or not end_date:
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=6)
    else:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

    # Fetch visit data within the date range
    visit_data = list(visits_collection.find(
        {"date": {"$gte": str(start_date), "$lte": str(end_date)}},
        {"_id": 0, "date": 1, "count": 1}
    ))

    return JsonResponse(visit_data, safe=False)