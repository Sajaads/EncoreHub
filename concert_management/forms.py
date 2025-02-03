from django import forms
from .models import Concert

class ConcertForm(forms.ModelForm):
    class Meta:
        model = Concert
        fields = '__all__'
        widgets = {
            'date_time': forms.DateTimeInput(attrs={
                'class': 'form-control datetimepicker',  # Custom class for Flatpickr initialization
            }),
        }
