from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Reserva, Servicio

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Se enviarán las confirmaciones a este correo.")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class ReservaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Fecha y Hora de la Reserva"
    )
    class Meta:
        model = Reserva
        fields = ['fecha_hora']

class ServicioForm(forms.ModelForm):
    """Formulario para Crear y Editar Servicios."""
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UserAdminUpdateForm(forms.ModelForm):
    """Formulario para que un admin edite a otra usuaria."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }