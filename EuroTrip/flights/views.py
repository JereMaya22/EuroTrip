from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import paypalrestsdk.payments
from Apps.Usuarios.models import usurio  # Asegúrate de importar desde el lugar correcto
import bcrypt
import requests
import json
from django.conf import settings
import paypalrestsdk
from django.core.mail import send_mail
import random
from .models import Vuelo  # Asegúrate de importar el modelo Vuelo

def CrearUsuario(request):
    error_message = None  # Inicializa el mensaje de error
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        edad = request.POST.get('edad')
        email = request.POST.get('email')
        direccion = request.POST.get('direccion')
        password = request.POST.get('password')

        if (request.POST.get('nombre') != "" or request.POST.get('apellido') != "" or request.POST.get('edad') != "" or request.POST.get('email') != "" or request.POST.get('direccion') != "" or request.POST['password'] != ""):
            # Encriptación de contraseña
            if (request.POST['password'] != ""):
                hashPass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            NuevoUsuario = usurio(nombre=nombre, apellido=apellido, edad=edad, email=email, direccion=direccion, password=hashPass.decode('utf-8'))
            NuevoUsuario.save()

            return redirect('home')
        
        else:
            hashPass = 00
            return HttpResponse("Rellene todos los campos correctamente")

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
                request.session['user_email'] = user.email  # Almacena el correo en la sesión
                return redirect('home')
            else:
                message = "Contraseña invalida"

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
    
    user = None
    if user_id:
        try:
            user = usurio.objects.get(id=user_id)
        except usurio.DoesNotExist:
            user = None

    context = {
        'guest': is_guest,
        'user': user
    }

    return render(request, 'home.html', context)
    
def UserProfile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirigir si no hay un usuario logueado

    try:
        user = usurio.objects.get(id=user_id)
    except usurio.DoesNotExist:
        return redirect('home')

    return render(request, 'User_Profile.html', {'user': user})

def Logout(request):
    request.session.flush()  # Elimina toda la información de la sesión
    return redirect('home')


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

            if (request.POST.get('newNombre') != "" and request.POST.get('newApellido') != "" and request.POST.get('newEmail') != "" and request.POST.get('newDireccion') != ""):
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


def ContactosView(request):
    # Lógica para mostrar contactos
    return render(request, 'Contactos.html')  # Asegúrate de que este archivo exista

def UsuarioView(request):
    # Lógica para mostrar información del usuario
    return render(request, 'Usuario.html')  # Asegúrate de que este archivo exista

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def search_flights(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        origen = data.get('origen')
        destino = data.get('destino')
        fecha_salida = data.get('fechaSalida')
        fecha_llegada = data.get('fechaLlegada')
        numero_de_adultos = data.get('numeroDeAdultos')
        
        # Diccionario de ciudades y sus códigos IATA
        city_codes = {
            'Madrid': 'MAD',
            'Barcelona': 'BCN',
            'Tokio': 'NRT',
            'Nueva York': 'JFK',
            'Los Ángeles': 'LAX',
            'Miami': 'MIA',
            'Toronto': 'YYZ',
            'Ciudad de México': 'MEX',
            'São Paulo': 'GRU',
            'Seúl': 'ICN',
            'Bangkok': 'BKK',
            'Pekín': 'PEK',
            'Singapur': 'SIN',
            'Dubai': 'DXB',
            'Londres': 'LHR',
            'París': 'CDG',
            'Berlín': 'TXL',
            'Ámsterdam': 'AMS',
            'Roma': 'FCO',
            'Sídney': 'SYD',
            'Melbourne': 'MEL',
            'Hong Kong': 'HKG',
            'Estambul': 'IST',
            'Moscú': 'SVO',
            'Johannesburgo': 'JNB',
            'El Cairo': 'CAI',
            'Kuala Lumpur': 'KUL',
            'Atenas': 'ATH',
            'Lisboa': 'LIS',
            'Bruselas': 'BRU',
            'Dublín': 'DUB',
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
            'Bogotá': 'BOG',
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

        # Obtener los códigos IATA a partir de los nombres de las ciudades
        origen_code = city_codes.get(origen, origen)  # Si no se encuentra, usa el valor original
        destino_code = city_codes.get(destino, destino)
        
        # Aquí puedes hacer la llamada a la API de Amadeus
        amadeus_api_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
        amadeus_api_key = 'AHMw6GAbnIdynAw2gUpEEjQ7yiJq'  # Reemplaza con tu token de acceso

        params = {
            'originLocationCode': origen_code,
            'destinationLocationCode': destino_code,
            'departureDate': fecha_salida,
            'returnDate': fecha_llegada,
            'adults': numero_de_adultos,
            'max': 5
        }

        headers = {
            'Authorization': f'Bearer {amadeus_api_key}'
        }

        response = requests.get(amadeus_api_url, params=params, headers=headers)
        flights = response.json()

        # Guardar los vuelos en la base de datos
        for flight in flights.get('data', []):
            # Extraer la fecha y convertirla al formato correcto
            departure_datetime = flight['itineraries'][0]['segments'][0]['departure']['at']
            departure_date = departure_datetime.split("T")[0]  # Obtener solo la parte de la fecha

            Vuelo.objects.create(
                departure_city=flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                arrival_city=flight['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                price=flight['price']['total'],
                date=departure_date  # Guardar solo la fecha
            )

        return JsonResponse(flights, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def Historial(request):
    return render(request, 'Historial.html')

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_payment(request):
    if request.method == "POST":
        
        data = json.loads(request.body)
        price = data.get("price")
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer":{"payment_method":"paypal"},
            "redirect_urls":{
                "return_url": "http://127.0.0.1:8000/payment/execute",
                "cancel_url": "http://127.0.0.1:8000/payment/cancel",
            },
            "transactions": [{
                "amount":{
                    "total": f"{float(price):.2f}",
                    "currency": "USD"
                },
                "description": "compra de vuelo"
            }]
        })
        
        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return JsonResponse({"approval_url": link.href})
        else:
            return JsonResponse({"error": payment.error}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        return JsonResponse({"error": "Faltan parámetros de pago"}, status=400)

    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        flight_id = request.session.get('flight_id')  # Asegúrate de guardar el ID del vuelo en la sesión
        flight_details = get_flight_details(flight_id)  # Obtener los detalles del vuelo

        # Verifica si hubo un error al obtener los detalles del vuelo
        if "error" in flight_details:
            return JsonResponse({"error": flight_details["error"]}, status=404)

        # Envía el recibo al correo electrónico del usuario
        user_email = request.session.get('user_email')  # Asegúrate de que el correo del usuario esté en la sesión
        send_receipt(user_email, flight_details)  # Envía el recibo al correo del usuario

        # Renderiza la plantilla con los detalles del vuelo
        return render(request, 'receipt.html', {
            'success': True,
            'flight_details': flight_details,
            'message': "Pago realizado con éxito. Recibo enviado."
        })
    else:
        return JsonResponse({"error": payment.error}, status=500)

def get_flight_details(flight_id):
    try:
        vuelo = Vuelo.objects.get(id=flight_id)  # Asegúrate de que el modelo Vuelo exista
        confirmation_number = random.randint(100000, 999999)  # Número de 6 dígitos

        return {
            "flight_id": vuelo.id,
            "departure": vuelo.departure_city,
            "arrival": vuelo.arrival_city,
            "price": f"${vuelo.price:.2f}",
            "date": vuelo.date.strftime("%Y-%m-%d"),
            "confirmation_number": confirmation_number
        }
    except Vuelo.DoesNotExist:
        return {
            "error": "Vuelo no encontrado"
        }

def send_receipt(email, flight_details):
    subject = "Recibo de tu compra de vuelo"
    message = f"""
    <html>
        <body>
            <h2>Gracias por tu compra!</h2>
            <p>Detalles de tu vuelo:</p>
            <ul>
                <li><strong>ID de vuelo:</strong> {flight_details['flight_id']}</li>
                <li><strong>Salida:</strong> {flight_details['departure']}</li>
                <li><strong>Llegada:</strong> {flight_details['arrival']}</li>
                <li><strong>Precio:</strong> {flight_details['price']}</li>
                <li><strong>Fecha:</strong> {flight_details['date']}</li>
                <li><strong>Número de confirmación:</strong> {flight_details['confirmation_number']}</li>
            </ul>
            <p>¡Esperamos que disfrutes de tu viaje!</p>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=message  # Asegúrate de enviar el mensaje como HTML
        )
        print("Correo enviado exitosamente a:", email)  # Mensaje de éxito
    except Exception as e:
        print("Error al enviar el correo:", e)  # Mensaje de error

def save_flight_id(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        flight_id = data.get('flight_id')
        request.session['flight_id'] = flight_id  # Guardar el ID del vuelo en la sesión
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

def test_email(request):
    subject = "Prueba de envío de correo"
    message = "Este es un correo de prueba desde Django."
    recipient_list = ['destinatario@example.com']  # Cambia esto por tu correo

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        return HttpResponse("Correo enviado exitosamente.")
    except Exception as e:
        return HttpResponse(f"Error al enviar el correo: {e}")
