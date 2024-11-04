function closeModal() {
    document.getElementById('successModal').style.display = 'none';
}

window.onload = function() {
    if (new URLSearchParams(window.location.search).get('success')) {
        document.getElementById('successModal').style.display = 'block';
    }
};


function openTab(evt, tabName) {
    var tabcontent = document.getElementsByClassName("tabcontent");
    for (var i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    var tablinks = document.getElementsByClassName("tablinks");
    for (var i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('.tablinks').click();
});

document.getElementById('flightForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData(this);

    fetch('/search-flights/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            origen: formData.get('origen'),
            destino: formData.get('destino'),
            fechaSalida: formData.get('fechaSalida'),
            fechaLlegada: formData.get('fechaLlegada'),
            numeroDeAdultos: formData.get('numeroDeAdultos')
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        displayResults(data);
    })
    .catch(error => console.error('Error:', error));
});

function displayResults(flights) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (flights.errors) {
        resultsDiv.innerHTML = `<p>Error: ${flights.errors[0].detail}</p>`;
        document.getElementById('floatingPanel').style.display = 'block'; // Mostrar panel flotante
        return;
    }

    if (!Array.isArray(flights.data)) {
        resultsDiv.innerHTML = '<p>No se encontraron vuelos.</p>';
        document.getElementById('floatingPanel').style.display = 'block'; // Mostrar panel flotante
        return;
    }

    flights.data.forEach(flight => {
        const flightInfo = document.createElement('div');
        flightInfo.innerHTML = `
            <p>Vuelo de ${flight.itineraries[0].segments[0].departure.iataCode} a ${flight.itineraries[0].segments[0].arrival.iataCode}</p>
            <p>Salida: ${flight.itineraries[0].segments[0].departure.at}</p>
            <p>Llegada: ${flight.itineraries[0].segments[0].arrival.at}</p>
            <p>Precio: ${flight.price.total} ${flight.price.currency}</p>
            <button class="buy-button" data-flight-id="${flight.id}" data-flight-price="${flight.price.total}">Comprar</button> 
        `;
        resultsDiv.appendChild(flightInfo);
    });

    document.getElementById('floatingPanel').style.display = 'block'; // Mostrar panel flotante

}

document.getElementById('closePanel').addEventListener('click', function() {
    document.getElementById('floatingPanel').style.display = 'none';
});

document.getElementById("Home").style.display = "block";

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('buy-button')) {
        const flightId = event.target.getAttribute('data-flight-id');
        const flightPrice = event.target.getAttribute('data-flight-price');  // Extraer el precio del vuelo

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Obtén el token CSRF aquí

        fetch('/create-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Usa el token CSRF obtenido
            },
            body: JSON.stringify({
                flight_id: flightId,
                price: flightPrice  // Enviar el precio
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.approval_url) {
                // Guardar el ID del vuelo en la sesión del servidor
                fetch('/save-flight-id/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ flight_id: flightId })
                });

                window.location.href = data.approval_url;  // Redirige a PayPal
            } else {
                console.error("Error al crear el pago:", data.error);
            }
        })
        .catch(error => console.error('Error al crear el pago:', error));
    }
});

// En la función execute_payment, después de enviar el recibo
function executePayment() {
    // ... tu lógica existente ...
    if (payment.execute({"payer_id": payer_id})) {
        // Aquí obtén los detalles del vuelo
        const flightDetails = {
            flight_id: flight_details.flight_id,
            departure: flight_details.departure,
            arrival: flight_details.arrival,
            price: flight_details.price,
            date: flight_details.date,
            confirmation_number: flight_details.confirmation_number
        };
        openModal(flightDetails);  // Abre el modal con los detalles del recibo
    } else {
        console.error("Error al ejecutar el pago:", payment.error);
    }
}