from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import paypalrestsdk.payments
from Apps.Usuarios.models import usurio
from flights.models import Pago
import bcrypt
import requests
import json
from django.conf import settings
import paypalrestsdk
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.views.generic import View
from datetime import datetime, timedelta

def CrearUsuario(request):
    # Inicializa el mensaje de error como None
    error_message = None  
    
    # Si el método de la petición es POST
    if request.method == 'POST':
        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        edad = request.POST.get('edad')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        password = request.POST.get('password')

        # Verifica que ningún campo esté vacío
        if (request.POST.get('nombre') != "" or request.POST.get('apellido') != "" or request.POST.get('edad') != "" or request.POST.get('email') != "" or request.POST.get('direccion') != "" or request.POST['password'] != ""):
            # Si la contraseña no está vacía, la encripta
            if (request.POST['password'] != ""):
                hashPass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Crea una nueva instancia de usuario y la guarda en la base de datos
            NuevoUsuario = usurio(nombre=nombre, apellido=apellido, edad=edad, email=email, direccion=direccion, password=hashPass.decode('utf-8'))
            NuevoUsuario.save()

            # Redirecciona a la página principal
            return redirect('home')
        
        else:
            # Si hay campos vacíos, establece hashPass a 00 y retorna mensaje de error
            hashPass = 00
            return HttpResponse("Rellene todos los campos correctamente")

    # Si el método no es POST, renderiza el formulario de registro
    return render(request, 'Register.html')


def Login(request):
    # Inicializa el mensaje vacío
    message = ""

    # Si el método es POST (cuando se envía el formulario)
    if request.method == 'POST':
        # Obtiene el correo y contraseña del formulario
        email = request.POST.get('correo')
        password = request.POST.get('contra')

        try:
            # Intenta obtener el usuario con el email proporcionado
            user = usurio.objects.get(email=email)

            # Convierte la contraseña a bytes para la comparación
            contra = bytes(password, 'utf-8')
            hashPwd = user.password.encode('utf-8')

            # Verifica si la contraseña coincide con el hash almacenado
            if bcrypt.checkpw(contra, hashPwd):
                # Si coincide, guarda el ID del usuario en la sesión
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                # Si no coincide, establece mensaje de error
                message = "Contraseña invalida"

        except usurio.DoesNotExist:
            # Si no existe el usuario, establece mensaje de error
            message = 'Usuario no existente'

    # Renderiza la plantilla con el mensaje
    return render(request, 'Login.html', {'message': message})

def GuestLogin(request):
    # Guarda en la sesión que el usuario es un usuario invitado
    request.session['is_guest'] = True
    # Establece el ID del usuario como None
    request.session['user_id'] = None
    # Redirecciona a la página principal
    return redirect('home')

def Home(request):
    # Obtiene el ID del usuario de la sesión
    user_id = request.session.get('user_id')
    # Obtiene si el usuario es un invitado de la sesión
    is_guest = request.session.get('is_guest', False)
    # Inicializa el usuario como None
    user = None
    # Si el ID del usuario existe, intenta obtener el usuario de la base de datos
    if user_id:
        try:
            # Obtiene el usuario de la base de datos
            user = usurio.objects.get(id=user_id)
        except usurio.DoesNotExist:
            # Si no existe, establece el usuario como None
            user = None

    # Crea el contexto para la plantilla
    context = {
        'guest': is_guest,
        'user': user
    }

    # Renderiza la plantilla con el contexto
    return render(request, 'home.html', context, {'user_id', user_id})
    
def UserProfile(request):
    # Obtiene el ID del usuario de la sesión
    user_id = request.session.get('user_id')
    # Si no hay un usuario logueado, redirige a la página de login
    if not user_id:
        return redirect('login')  

    try:
        # Obtiene el usuario de la base de datos
        user = usurio.objects.get(id=user_id)
    except usurio.DoesNotExist:
        return redirect('home')

    # Renderiza la plantilla con el usuario
    return render(request, 'User_Profile.html', {'user': user})

def Logout(request):
    # Elimina toda la información de la sesión
    request.session.flush()  
    # Redirecciona a la página principal
    return redirect('home')


def UpdateUser(request):
    # Inicializa el mensaje vacío
    message = ""
    # Si el método es POST (cuando se envía el formulario)
    if request.method == 'POST':
        # Obtiene el ID del usuario de la sesión
        user_id = request.session.get('user_id')

        if user_id:
            # Obtiene el usuario de la base de datos
            user = usurio.objects.get(id=user_id)

            # Obtiene los nuevos datos del formulario
            newNombre = request.POST.get('newNombre')
            newApellido = request.POST.get('newApellido')
            newEmail = request.POST.get('newEmail')
            newDireccion = request.POST.get('newDireccion')

            # Verifica que ningún campo esté vacío
            if (request.POST.get('newNombre') != "" and request.POST.get('newApellido') != "" and request.POST.get('newEmail') != "" and request.POST.get('newDireccion') != ""):
                # Actualiza los datos del usuario
                user.nombre = newNombre
                user.apellido = newApellido
                user.email = newEmail
                user.direccion = newDireccion

                user.save()

                # Redirecciona a la página principal
                return redirect('home')
            else:
                # Si hay campos vacíos, establece mensaje de error
                message = "Debe de rellenar todos los campos correctamente"
        else:
            # Si no hay un usuario logueado, redirige a la página de login
            return redirect('login')

    # Renderiza la plantilla con el mensaje
    return render(request, 'Update_User.html', {'message': message})

def ViajesView(request):
    # Renderiza la plantilla de viajes
    return render(request, 'Viajes.html')  


def ContactosView(request):
    # Renderiza la plantilla de contactos
    return render(request, 'Contactos.html')  

def UsuarioView(request):
    return render(request, 'Usuario.html')  

def error_404_view(request, exception):
    return render(request, '404.html', status=404)


# Función para buscar vuelos
def search_flights(request):
    # Verifica si la petición es POST
    if request.method == 'POST':
        # Obtiene los datos del cuerpo 
        data = json.loads(request.body)
        origen = data.get('origen')
        destino = data.get('destino')
        fecha_salida = data.get('fechaSalida')
        fecha_llegada = data.get('fechaLlegada')
        numero_de_adultos = data.get('numeroDeAdultos')
        
        # Diccionario que mapea ciudades a sus códigos IATA
        city_codes = {
            'Madrid': 'MAD',
            'Barcelona': 'BCN',
            'Tokio': 'NRT',
            'Nueva York': 'JFK',
            'Los Angeles': 'LAX',
            'Miami': 'MIA',
            'Toronto': 'YYZ',
            'Ciudad de Mexico': 'MEX',
            'Sao Paulo': 'GRU',
            'Seul': 'ICN',
            'Bangkok': 'BKK',
            'Pekin': 'PEK',
            'Singapur': 'SIN',
            'Dubai': 'DXB',
            'Londres': 'LHR',
            'Paris': 'CDG',
            'Berlin': 'TXL',
            'Amsterdam': 'AMS',
            'Roma': 'FCO',
            'Sidney': 'SYD',
            'Melbourne': 'MEL',
            'Hong Kong': 'HKG',
            'Estambul': 'IST',
            'Moscu': 'SVO',
            'Johannesburgo': 'JNB',
            'El Cairo': 'CAI',
            'Kuala Lumpur': 'KUL',
            'Atenas': 'ATH',
            'Lisboa': 'LIS',
            'Bruselas': 'BRU',
            'Dublin': 'DUB',
            'Estocolmo': 'ARN',
            'Oslo': 'OSL',
            'Helsinki': 'HEL',
            'Copenhague': 'CPH',
            'Zurich': 'ZRH',
            'Ginebra': 'GVA',
            'Viena': 'VIE',
            'Budapest': 'BUD',
            'Praga': 'PRG',
            'Varsovia': 'WAW',
            'Buenos Aires': 'EZE',
            'Santiago': 'SCL',
            'Lima': 'LIM',
            'Bogota': 'BOG',
            'Caracas': 'CCS',
            'Manila': 'MNL',
            'Jakarta': 'CGK',
            'Nueva Delhi': 'DEL',
            'Mumbai': 'BOM',
            'Tel Aviv': 'TLV',
            'San Francisco': 'SFO',
            'Boston': 'BOS',
            'Chicago': 'ORD',
            'Washington D.C.': 'IAD',
            'Atlanta': 'ATL',
            'Houston': 'IAH',
            'San Salvador': 'SAL',
        }

        # Obtiene los códigos IATA para origen y destino
        origen_code = city_codes.get(origen, origen)  # Si no encuentra el código, usa el valor original
        destino_code = city_codes.get(destino, destino)
        
        # Configuración para la llamada a la API de Amadeus
        amadeus_api_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
        amadeus_api_key = 'AiZTq87UYT6jhXjbneAs3OilaeBC'

        # Parámetros para la búsqueda de vuelos
        params = {
            'originLocationCode': origen_code,
            'destinationLocationCode': destino_code,
            'departureDate': fecha_salida,
            'returnDate': fecha_llegada,
            'adults': numero_de_adultos,
            'max': 5
        }

        # Headers para la autenticación
        headers = {
            'Authorization': f'Bearer {amadeus_api_key}'
        }

        # Realiza la petición a la API
        response = requests.get(amadeus_api_url, params=params, headers=headers)
        flights = response.json()

        # Retorna los resultados
        return JsonResponse(flights, safe=False)
    
    # Si la petición no es POST, retorna error
    return JsonResponse({'error': 'Invalid request'}, status=400)


def Historial(request):
    # Obtiene el ID del usuario de la sesión actual
    user_id = request.session.get('user_id')
    
    # Si no hay usuario logueado, redirige al login
    if not user_id:
        return redirect('login')
    
    # Filtrar pagos por el ID del usuario
    pagos = Pago.objects.filter(usuario=user_id)
    
    # Crea el contexto con los pagos filtrados
    context = {
        'pagos': pagos,
    }
    # Renderiza la plantilla historial.html con el contexto
    return render(request, 'historial.html', context)

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_payment(request):
    # Verifica si el método de la petición es POST
    if request.method == "POST":
        
        # Obtiene los datos del cuerpo de la petición y extrae el precio
        data = json.loads(request.body)
        price = data.get("price")
        
        # Crea un objeto de pago de PayPal con la configuración necesaria
        payment = paypalrestsdk.Payment({
            "intent": "sale", # Indica que es una venta
            "payer":{"payment_method":"paypal"}, # Método de pago: PayPal
            "redirect_urls":{ # URLs de redirección después del pago
                "return_url": "http://127.0.0.1:8000/payment/execute", # URL si el pago es exitoso
                "cancel_url": "http://127.0.0.1:8000/payment/cancel", # URL si se cancela el pago
            },
            "transactions": [{ # Detalles de la transacción
                "amount":{ # Monto y moneda
                    "total": f"{float(price):.2f}",
                    "currency": "USD"
                },
                "description": "compra de vuelo" # Descripción de la compra
            }]
        })
        
        # Intenta crear el pago
        if payment.create():
            # Si se crea exitosamente, busca la URL de aprobación
            for link in payment.links:
                if link.rel == "approval_url":
                    return JsonResponse({"approval_url": link.href})
        else:
            # Si hay un error al crear el pago, retorna el error
            return JsonResponse({"error": payment.error}, status=500)

    # Si el método no es POST, retorna error
    return JsonResponse({"error": "Invalid request method"}, status=405)

def Recivo(request):
    # Verifica si el método de la petición es POST
    if request.method == 'POST':
        # Obtiene los datos del cuerpo de la petición
        data = json.loads(request.body)
    
        # Extrae los datos necesarios del JSON
        userId = data.get('userId')
        flight_id = data.get('flight_id')
        price = data.get('price')
        origen = data.get('origen')
        destino = data.get('destino')
        fechaSalida = data.get('fechaSalida')
        fechaLlegada = data.get('fechaLlegada')
        
        # Crea un nuevo registro de pago con los datos recibidos
        Registro = Pago(
            usuario=userId,
            monto=price,
            flight_id=flight_id,
            origen=origen,
            destino=destino,
            fecha_salida=fechaSalida,
            fecha_llegada=fechaLlegada
        )
        # Guarda el registro en la base de datos
        Registro.save()

        # Retorna respuesta exitosa
        return JsonResponse({"success": True})
    
    
class PDFRecibo(View):
    def get(self, request, *args, **kwargs):
        # Obtiene el ID del pago
        pago_id = kwargs.get('pago_id')
        pago = Pago.objects.get(id=pago_id)

        # Renderiza el HTML para el PDF
        context = {
            'origen': pago.origen,
            'destino': pago.destino,
            'monto': pago.monto,
            'fecha_salida': pago.fecha_salida,
            'fecha_llegada': pago.fecha_llegada,
        }
        # Convierte el contexto en HTML usando la plantilla recibo.html
        html = render_to_string('recibo.html', context)

        # Configura la respuesta HTTP para descargar un PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recibo_{pago_id}.pdf"'
        
        # Crea el PDF a partir del HTML usando pisa
        pisa_status = pisa.CreatePDF(html, dest=response)

        # Si hay error al generar el PDF, retorna mensaje de error
        if pisa_status.err:
            return HttpResponse('Error generando PDF')

        # Retorna el PDF generado
        return response


def execute_payment(request):
    # Obtiene los IDs de pago y pagador de los parámetros GET
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    # Verifica que se hayan proporcionado ambos IDs
    if not payment_id or not payer_id:
        return JsonResponse({"error": "Faltan parámetros de pago"}, status=400)

    # Busca el pago en PayPal usando el ID
    payment = paypalrestsdk.Payment.find(payment_id)
    # Ejecuta el pago con el ID del pagador
    if payment.execute({"payer_id": payer_id}):
        # Si el pago es exitoso, redirige a la página principal
        return redirect('/home/?success=true')
    else:
        # Si hay error, retorna el error en formato JSON
        return JsonResponse({"error": payment.error}, status=500)
    

