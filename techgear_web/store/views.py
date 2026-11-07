import os
import requests

from django.shortcuts import render, redirect

API_URL = os.getenv(
    "TECHGEAR_API_URL",
    "https://t2-techgear.onrender.com"
).rstrip("/")

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
                request.session['rol'] = resultado['rol']

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


def dashboard(request):

    # Verificar que haya una sesión iniciada
    if 'access_token' not in request.session:
        return redirect('login')

    # Verificar que el usuario sea administrador
    if request.session.get('rol') != 'admin':
        return redirect('catalogo')

    # Obtener el token guardado en la sesión
    token = request.session['access_token']

    # Preparar los encabezados de autenticación
    headers = {
        'Authorization': f'Bearer {token}'
    }

    error = None

    # Comprobar si se envió el formulario
    if request.method == 'POST':

        # Obtener los datos del formulario
        datos = {
            'nombre': request.POST.get('nombre'),
            'descripcion': request.POST.get('descripcion'),
            'precio': request.POST.get('precio'),
            'stock': request.POST.get('stock')
        }

        try:
            respuesta = requests.post(
                f"{API_URL}/productos",
                json=datos,
                headers=headers,
                timeout=10
            )

            respuesta.raise_for_status()

            return redirect('dashboard')

        except requests.RequestException as e:
            try:
                error = respuesta.json().get(
                    'detail',
                    'No se pudo registrar el producto'
                )
            except (ValueError, UnboundLocalError):
                error = 'No se pudo conectar con FastAPI'

    # Consultar los productos
    try:
        respuesta = requests.get(
            f"{API_URL}/productos",
            timeout=10
        )

        respuesta.raise_for_status()
        productos = respuesta.json()

    except requests.RequestException:
        productos = []
        error = error or "No se pudieron cargar los productos"

    return render(
        request,
        'store/dashboard.html',
        {
            'productos': productos,
            'error': error
        }
    )


def editar_producto(request, producto_id):

    # Verificar que haya una sesión iniciada
    if 'access_token' not in request.session:
        return redirect('login')

    # Verificar que el usuario sea administrador
    if request.session.get('rol') != 'admin':
        return redirect('catalogo')

    # Obtener el token de autenticación
    token = request.session['access_token']

    # Preparar los encabezados
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Si se envía el formulario
    if request.method == 'POST':

        # Obtener los datos modificados
        datos = {
            'nombre': request.POST.get('nombre'),
            'descripcion': request.POST.get('descripcion'),
            'precio': request.POST.get('precio'),
            'stock': request.POST.get('stock')
        }

        try:
            respuesta = requests.put(
                f"{API_URL}/productos/{producto_id}",
                json=datos,
                headers=headers,
                timeout=10
            )

            respuesta.raise_for_status()

            return redirect('dashboard')

        except requests.RequestException:
            error = 'No se pudo actualizar el producto'

            return render(
                request,
                'store/editar_producto.html',
                {
                    'producto': datos,
                    'error': error
                }
            )

    # Consultar los datos actuales del producto
    try:
        respuesta = requests.get(
            f"{API_URL}/productos/{producto_id}",
            timeout=10
        )

        respuesta.raise_for_status()
        producto = respuesta.json()

    except requests.RequestException:
        return redirect('dashboard')

    return render(
        request,
        'store/editar_producto.html',
        {
            'producto': producto
        }
    )

def eliminar_producto(request, producto_id):

    # Verificar que haya una sesión iniciada
    if 'access_token' not in request.session:
        return redirect('login')

    # Verificar que el usuario sea administrador
    if request.session.get('rol') != 'admin':
        return redirect('catalogo')

    # Obtener el token
    token = request.session['access_token']

    # Preparar los encabezados
    headers = {
        'Authorization': f'Bearer {token}'
    }

    try:
        respuesta = requests.delete(
            f"{API_URL}/productos/{producto_id}",
            headers=headers,
            timeout=10
        )

        if respuesta.status_code == 200:
            return redirect('dashboard')

        return redirect('dashboard')

    except requests.RequestException:
        return redirect('dashboard')