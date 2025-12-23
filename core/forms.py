from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Votre nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jean Dupont'})
    )
    email = forms.EmailField(
        label="Votre email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jean@exemple.com'})
    )
    subject = forms.CharField(
        label="Sujet",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Demande de renseignement'})
    )
    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Bonjour, je souhaiterais...'})
    )
