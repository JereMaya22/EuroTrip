from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from Apps.Usuarios.views import CrearUsuario, Login, Home, UpdateUser, GuestLogin, ViajesView, ReservasView, ContactosView, UsuarioView, error_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', CrearUsuario, name='register'),
    path('login/', Login, name='login'),
    path('home/', Home, name='home'),
    path('updateUser/', UpdateUser, name='updateUser'),
    path('guestLogin/', GuestLogin, name='guestLogin'),
    path('viajes/', ViajesView, name='Viajes'),
    path('reservas/', ReservasView, name='Reservas'),
    path('contactos/', ContactosView, name='Contactos'),
    path('usuario/', UsuarioView, name='Usuario'),
    path('', include('flights.urls')),  # Incluir las URLs de la aplicación flights
]

# Manejo de errores 404
handler404 = error_404_view