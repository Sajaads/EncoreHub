from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import ConcertForm
from .models import Concert
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



def retrieve_concerts(request):
    concert_list = Concert.objects.all()
    paginator = Paginator(concert_list, 10)  # Show 15 concerts per page
    page_number = request.GET.get('page')
    concerts = paginator.get_page(page_number)
    return render(request, 'list_concerts.html', {'concerts': concerts})

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

def delete_concert(request, pk):
    concert = get_object_or_404(Concert, pk=pk)
    if request.method == 'POST':
        concert.delete()
        return redirect('list_concerts')
    return render(request, 'delete_concert.html', {'concert':concert})