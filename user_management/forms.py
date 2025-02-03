from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(
        max_length=150,
        required=True,
        help_text = "Only letters, spaces, and periods (.) are allowed."
    )

    email = forms.EmailField(
        required=True,
        max_length=254,
    )

    class Meta:
        model = User
        fields = ['username','name', 'email', 'password1', 'password2']

    def clean_name(self):
        """
        Validate the name field to ensure only valid characters are used.
        """
        name = self.cleaned_data.get("name")
        if not all(char.isalpha() or char.isspace() or char == "." for char in name):
            raise forms.ValidationError("Name can only contain letters, spaces, and periods.")
        return name

    def clean_email(self):
        """
        Validate that the email is unique.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
