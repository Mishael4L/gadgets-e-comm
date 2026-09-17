# storeapp/forms.py
from django import forms
from .models import Messageform, NewsletterSubscriber

class ContactForm(forms.ModelForm):
    class Meta:
        model = Messageform
        fields = ['first_name', 'last_name', 'email', 'phone', 'subject', 'order_number', 'message']

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']