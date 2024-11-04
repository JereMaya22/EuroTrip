from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from .models import usurio
import bcrypt
import re

def CrearUsuario(request):
    error_message = None  # Inicializa el mensaje de error
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        edad = request.POST.get('edad')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')  # Campo para confirmar la contraseña
        
        # Verificar si el correo ya existe
        if usurio.objects.filter(email=email).exists():
            error_message = "El correo ya está registrado. Por favor, use otro correo."
            return render(request, 'Register.html', {'error_message': error_message})
        
        # Verificar que todos los campos estén llenos
        if nombre and apellido and edad and email and direccion and password:
            # Validaciones de contraseña
            if len(password) < 8:
                error_message = "La contraseña debe tener al menos 8 caracteres."
            elif not re.search(r'[A-Z]', password):
                error_message = "La contraseña debe contener al menos una letra mayúscula."
            elif not re.search(r'[a-z]', password):
                error_message = "La contraseña debe contener al menos una letra minúscula."
            elif not re.search(r'[0-9]', password):
                error_message = "La contraseña debe contener al menos un número."
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                error_message = "La contraseña debe contener al menos un carácter especial."
            
            else:
                # Encriptación de contraseña
                hashPass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                # Crear y guardar el nuevo usuario
                NuevoUsuario = usurio(nombre=nombre, apellido=apellido, edad=edad, email=email, direccion=direccion, password=hashPass.decode('utf-8'))
                NuevoUsuario.save()

                return redirect('login')
        
        else:
            error_message = "Rellene todos los campos correctamente"

        return render(request, 'Register.html', {'error_message': error_message})

    return render(request, 'Register.html')

def Login(request):
    message = ""
    
    if request.method == 'POST':
        email = request.POST.get('correo')
        password = request.POST.get('contra')
           
        try:
            user = usurio.objects.get(email=email)
            
            contra = bytes(password, 'utf-8')
            hashPwd = user.password.encode('utf-8')
            
            if bcrypt.checkpw(contra, hashPwd):
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                message = "Contraseña inválida"
                
        except usurio.DoesNotExist:
            message = 'Usuario no existente'
        
    return render(request, 'Login.html', {'message': message})

def GuestLogin(request):
    request.session['is_guest'] = True
    request.session['user_id'] = None
    return redirect('home')

def Home(request):
    user_id = request.session.get('user_id')
    is_guest = request.session.get('is_guest', False)
    
    if user_id:
        user = usurio.objects.get(id=user_id)
        return render(request, 'Home.html', {'user': user, 'guest': False})
    
    elif is_guest:
        return render(request, 'Home.html', {'user': None, 'guest': True})
    else:
        return render(request, "Login.html")
    
def UpdateUser(request):
    message = ""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        if user_id:
            user = usurio.objects.get(id=user_id)
            
            newNombre = request.POST.get('newNombre')
            newApellido = request.POST.get('newApellido')
            newEmail = request.POST.get('newEmail')
            newDireccion = request.POST.get('newDireccion')
            
            if newNombre and newApellido and newEmail and newDireccion:
                user.nombre = newNombre
                user.apellido = newApellido
                user.email = newEmail
                user.direccion = newDireccion
                
                user.save()
                
                return redirect('home')
            else:
                message = "Debe de rellenar todos los campos correctamente"
        else:
            return redirect('login')
            
    return render(request, 'Update_User.html', {'message': message})

def ViajesView(request):
    # Lógica para mostrar viajes
    return render(request, 'Viajes.html')  # Asegúrate de que este archivo exista

def ReservasView(request):
    # Lógica para mostrar reservas
    return render(request, 'Reservas.html')  # Asegúrate de que este archivo exista

def ContactosView(request):
    # Lógica para mostrar contactos
    return render(request, 'Contactos.html')  # Asegúrate de que este archivo exista

def UsuarioView(request):
    # Lógica para mostrar información del usuario
    return render(request, 'Usuario.html')  # Asegúrate de que este archivo exista

def error_404_view(request, exception):
    return render(request, '404.html', status=404)