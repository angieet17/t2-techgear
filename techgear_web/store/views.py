import requests

from django.shortcuts import render, redirect

API_URL = "http://127.0.0.1:8001"

# Create your views here.
def catalogo(request):
    try:
        respuesta = requests.get(
            f"{API_URL}/productos",
            timeout=10
        )

        respuesta.raise_for_status()
        productos = respuesta.json()

        error = None

    except requests.RequestException:
        productos = []
        error = "No se pudo conectar con el servidor de productos"

    return render(
        request,
        'store/catalogo.html',
        {
            'productos': productos,
            'error': error
        }
    )


def login(request):
    if request.method == 'POST':

        # Obtener los datos del formulario
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        # Preparar los datos para FastAPI
        datos = {
            "correo": correo,
            "contrasena": contrasena
        }

        try:
            respuesta = requests.post(
                f"{API_URL}/usuarios/login",
                json=datos,
                timeout=10
            )

            if respuesta.status_code == 200:

                # Obtener el JWT que devuelve FastAPI
                resultado = respuesta.json()
                token = resultado['access_token']

                # Guardar el token en la sesión de Django
                request.session['access_token'] = token
                request.session['correo'] = correo

                # La sesión tendrá la misma duración que el JWT
                request.session.set_expiry(1800)

                return redirect('catalogo')

            mensaje = respuesta.json().get(
                'detail',
                'Correo o contraseña incorrectos'
            )

        except requests.RequestException:
            mensaje = 'No se pudo conectar con el servidor'

        return render(
            request,
            'store/login.html',
            {'error': mensaje}
        )
    return render(request, 'store/login.html')


def registro(request):
    if request.method == 'POST':

        # Obtener los datos enviados desde el formulario
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')

        # Preparar los datos para FastAPI
        datos = {
            "nombre": nombre,
            "correo": correo,
            "contrasena": contrasena
        }

        try:
            respuesta = requests.post(
                f"{API_URL}/usuarios/registro",
                json=datos,
                timeout=10
            )

            if respuesta.status_code == 201:
                return redirect('login')

            mensaje = respuesta.json().get(
                'detail',
                'No fue posible registrar el usuario'
            )

        except requests.RequestException:
            mensaje = 'No se pudo conectar con el servidor'

        return render(
            request,
            'store/registro.html',
            {'error': mensaje}
        )
    return render(request, 'store/registro.html')

def cerrar_sesion(request):
    request.session.flush()
    return redirect('catalogo')
