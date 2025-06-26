from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.panel_dashboard, name='panel_dashboard'),

    # Gestión de Reservas
    path('reservas/', views.panel_lista_reservas, name='panel_lista_reservas'),
    path('reservas/confirmar/<int:id_reserva>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reservas/completar/<int:id_reserva>/', views.completar_reserva, name='completar_reserva'),

    # CRUD de Servicios
    path('servicios/', views.ServicioListView.as_view(), name='panel_lista_servicios'),
    path('servicios/crear/', views.ServicioCreateView.as_view(), name='panel_crear_servicio'),
    path('servicios/editar/<int:pk>/', views.ServicioUpdateView.as_view(), name='panel_editar_servicio'),
    path('servicios/borrar/<int:pk>/', views.ServicioDeleteView.as_view(), name='panel_borrar_servicio'),

    # CRUD de Usuarios
    path('usuarios/', views.UserListView.as_view(), name='panel_lista_usuarios'),
    path('usuarios/editar/<int:pk>/', views.UserUpdateView.as_view(), name='panel_editar_usuario'),
]