from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, time, timedelta

from .models import Servicio, Reserva
from .forms import RegistroForm, ReservaForm, ServicioForm, UserAdminUpdateForm


def es_staff(user):
    return user.is_staff

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

def home(request):
    servicios = Servicio.objects.all()
    return render(request, 'public/home.html', {'servicios': servicios})

def servicio_detail(request, id_servicio):
    servicio = get_object_or_404(Servicio, id=id_servicio)
    return render(request, 'public/servicio_detail.html', {'servicio': servicio})

def vista_registro(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenida, {user.username}! Tu cuenta ha sido creada.")
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})

def vista_login(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff: return redirect('panel_dashboard')
                else: return redirect('mis_reservas')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def vista_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión exitosamente.")
    return redirect('home')

@login_required
def mis_reservas(request):
    ahora = timezone.now()
    reservas_proximas = Reserva.objects.filter(clienta=request.user, fecha_hora__gte=ahora).order_by('fecha_hora')
    reservas_pasadas = Reserva.objects.filter(clienta=request.user, fecha_hora__lt=ahora).order_by('-fecha_hora')
    context = {'proximas': reservas_proximas, 'pasadas': reservas_pasadas}
    return render(request, 'public/mis_reservas.html', context)

@login_required
def cancelar_mi_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id=id_reserva, clienta=request.user)
    if reserva.estado in ['pendiente', 'confirmada']:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, f"Tu reserva para '{reserva.servicio.nombre}' ha sido cancelada.")
    else:
        messages.error(request, "No es posible cancelar esta reserva.")
    return redirect('mis_reservas')

@login_required
def crear_reserva(request, id_servicio):
    servicio = get_object_or_404(Servicio, id=id_servicio)
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        if not fecha_str or not hora_str:
            messages.error(request, "Debes seleccionar una fecha y una hora.")
            return redirect('crear_reserva', id_servicio=id_servicio)
        try:
            fecha_hora_reserva = timezone.make_aware(datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M'))
        except ValueError:
            messages.error(request, "El formato de fecha u hora es incorrecto.")
            return redirect('crear_reserva', id_servicio=id_servicio)
        if fecha_hora_reserva < timezone.now():
            messages.error(request, "No puedes agendar una cita en una fecha u hora pasada.")
        else:
            Reserva.objects.create(servicio=servicio, clienta=request.user, fecha_hora=fecha_hora_reserva, estado='pendiente')
            messages.success(request, f"Tu reserva para '{servicio.nombre}' ha sido agendada.")
            return redirect('mis_reservas')
    context = {'servicio': servicio}
    return render(request, 'public/crear_reserva.html', context)

@login_required
def get_horarios_disponibles(request, id_servicio):
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse({'error': 'No se proporcionó fecha'}, status=400)
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    horario_inicio_salon = time(9, 0)
    horario_fin_salon = time(20, 0)
    servicio = get_object_or_404(Servicio, id=id_servicio)
    duracion_servicio = timedelta(minutes=servicio.duracion_minutos)
    reservas_del_dia = Reserva.objects.filter(fecha_hora__date=fecha, estado__in=['confirmada', 'pendiente'])
    bloques_ocupados = [(r.fecha_hora, r.fecha_hora + timedelta(minutes=r.servicio.duracion_minutos)) for r in reservas_del_dia]
    horarios_disponibles = []
    posible_inicio_bloque = timezone.make_aware(datetime.combine(fecha, horario_inicio_salon))
    limite_ultimo_inicio = timezone.make_aware(datetime.combine(fecha, horario_fin_salon)) - duracion_servicio
    while posible_inicio_bloque <= limite_ultimo_inicio:
        posible_fin_bloque = posible_inicio_bloque + duracion_servicio
        es_futuro = posible_inicio_bloque > timezone.now()
        hay_colision = any(posible_inicio_bloque < fin_ocupado and posible_fin_bloque > inicio_ocupado for inicio_ocupado, fin_ocupado in bloques_ocupados)
        if es_futuro and not hay_colision:
            horarios_disponibles.append({"value": posible_inicio_bloque.strftime('%H:%M'), "display": f"{posible_inicio_bloque.strftime('%H:%M')} - {posible_fin_bloque.strftime('%H:%M')}"})
        posible_inicio_bloque += timedelta(minutes=15)
    return JsonResponse({'horarios': horarios_disponibles})

@user_passes_test(es_staff)
def get_chart_data(request):
    now = timezone.now()
    reservas_por_mes = (Reserva.objects.filter(fecha_hora__year=now.year, estado__in=['confirmada', 'completada']).values('fecha_hora__month').annotate(total=Count('id')).order_by('fecha_hora__month'))
    meses_labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    data_reservas = [0] * 12
    for r in reservas_por_mes:
        mes_index = r['fecha_hora__month'] - 1
        data_reservas[mes_index] = r['total']
    servicios_populares = (Reserva.objects.filter(estado__in=['confirmada', 'completada']).values('servicio__nombre').annotate(total=Count('id')).order_by('-total')[:5])
    labels_servicios = [s['servicio__nombre'] for s in servicios_populares]
    data_servicios = [s['total'] for s in servicios_populares]
    return JsonResponse({'reservasMensuales': {'labels': meses_labels, 'data': data_reservas}, 'serviciosPopulares': {'labels': labels_servicios, 'data': data_servicios}})
@login_required
@user_passes_test(es_staff)
def panel_dashboard(request):
    # Calculamos los 3 números clave
    total_usuarios = User.objects.filter(is_staff=False).count() # Contamos solo clientas
    total_servicios = Servicio.objects.count()
    total_reservas = Reserva.objects.count()
    
    # Calculamos el dato para la alerta: ¿cuántas reservas necesitan atención?
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_servicios': total_servicios,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
    }
    return render(request, 'panel/dashboard.html', context)

@login_required
@user_passes_test(es_staff)
def panel_lista_reservas(request):
    reservas = Reserva.objects.all().select_related('servicio', 'clienta').order_by('-fecha_hora')
    return render(request, 'panel/lista_reservas.html', {'reservas': reservas})

@login_required
@user_passes_test(es_staff)
def confirmar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id=id_reserva)
    reserva.estado = 'confirmada'
    reserva.save()
    messages.success(request, f"Reserva de {reserva.clienta.username} ha sido CONFIRMADA.")
    return redirect('panel_lista_reservas')

@login_required
@user_passes_test(es_staff)
def cancelar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id=id_reserva)
    reserva.estado = 'cancelada'
    reserva.save()
    messages.warning(request, f"Reserva de {reserva.clienta.username} ha sido CANCELADA.")
    return redirect('panel_lista_reservas')

@login_required
@user_passes_test(es_staff)
def completar_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id=id_reserva)
    reserva.estado = 'completada'
    reserva.save()
    messages.success(request, f"Reserva de {reserva.clienta.username} marcada como COMPLETADA.")
    return redirect('panel_lista_reservas')

class ServicioListView(StaffRequiredMixin, ListView):
    model = Servicio
    template_name = 'panel/servicio_list.html'
    context_object_name = 'servicios'

class ServicioCreateView(StaffRequiredMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'panel/servicio_form.html'
    success_url = reverse_lazy('panel_lista_servicios')

class ServicioUpdateView(StaffRequiredMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'panel/servicio_form.html'
    success_url = reverse_lazy('panel_lista_servicios')

class ServicioDeleteView(StaffRequiredMixin, DeleteView):
    model = Servicio
    template_name = 'panel/servicio_confirm_delete.html'
    success_url = reverse_lazy('panel_lista_servicios')

class UserListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'panel/user_list.html'
    context_object_name = 'usuarios'
    queryset = User.objects.all().order_by('username')

class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserAdminUpdateForm
    template_name = 'panel/user_form.html'
    success_url = reverse_lazy('panel_lista_usuarios')