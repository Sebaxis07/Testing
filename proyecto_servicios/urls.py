from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from reservas import views as vistas_reservas

urlpatterns = [
    # URLs de Autenticación
    path('registro/', vistas_reservas.vista_registro, name='registro'),
    path('login/', vistas_reservas.vista_login, name='login'),
    path('logout/', vistas_reservas.vista_logout, name='logout'),

    # URLs del Panel de Administración
    path('panel/', include('reservas.panel_urls')),

    # URLs Públicas y de Clienta
    path('', vistas_reservas.home, name='home'),
    path('servicio/<int:id_servicio>/', vistas_reservas.servicio_detail, name='servicio_detail'),
    path('reservar/<int:id_servicio>/', vistas_reservas.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', vistas_reservas.mis_reservas, name='mis_reservas'),
    path('mis-reservas/cancelar/<int:id_reserva>/', vistas_reservas.cancelar_mi_reserva, name='cancelar_mi_reserva'),
    
    # === LA RUTA CLAVE PARA LA API ===
    path('api/horarios-disponibles/<int:id_servicio>/', vistas_reservas.get_horarios_disponibles, name='get_horarios_disponibles'),
    path('api/chart-data/', vistas_reservas.get_chart_data, name='get_chart_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])