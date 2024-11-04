from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.Home, name='home'),
    path('search-flights/', views.search_flights, name='search_flights'),
    path('register/', views.CrearUsuario, name='register'),
    path('login/', views.Login, name='login'),
    path('guest-login/', views.GuestLogin, name='guest_login'),
    path('update-user/', views.UpdateUser, name='updateUser'),
    path('viajes/', views.ViajesView, name='viajes'),
    path('contactos/', views.ContactosView, name='contactos'),
    path('usuario/', views.UsuarioView, name='usuario'),
    path('logout/', views.Logout,name='logout'),
    path('user_profile/', views.UserProfile, name='user_profile'),
    path('historial/', views.Historial,name='historial'),
    path("create-payment/", views.create_payment, name="create_payment"),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('recivo/', views.Recivo, name='recivo'),
    path('recivo/<int:pago_id>/', views.PDFRecibo.as_view(), name='recivo'),
]