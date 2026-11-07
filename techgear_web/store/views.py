import os
import requests

from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

API_URL = os.getenv(
    "TECHGEAR_API_URL",
    "https://t2-techgear.onrender.com"
).rstrip("/")
TIMEOUT = 40
MAX_IMAGEN = 1024 * 1024  # 1 MB

def subir_imagen(producto_id, archivo, headers):
    """Envía la imagen a la API. Devuelve None si salió bien,
    o un texto con el error si algo falló."""
    if archivo.size > MAX_IMAGEN:
        return 'La imagen pesa más de 1 MB'

    try:
        respuesta = requests.post(
            f"{API_URL}/productos/{producto_id}/imagen",
            files={'imagen': (archivo.name, archivo.read(), archivo.content_type)},
            headers=headers,
            timeout=TIMEOUT
        )
        if respuesta.status_code == 200:
            return None
        return respuesta.json().get('detail', 'No se pudo subir la imagen')

    except (requests.RequestException, ValueError):
        return 'No se pudo subir la imagen'

def traducir_errores(detalle):
    """Convierte la respuesta de error de la API en mensajes por campo.
    Devuelve (errores_por_campo, mensaje_general)."""
    errores = {}
    general = None

    # Errores de validación (pydantic): llegan como una lista
    if isinstance(detalle, list):
        for e in detalle:
            loc = e.get('loc') or []
            campo = loc[-1] if loc else None
            tipo = e.get('type', '')

            if campo == 'contrasena' and tipo == 'string_too_short':
                errores['contrasena'] = 'La contraseña debe tener mínimo 8 caracteres.'
            elif campo in ('nombre', 'correo') and tipo == 'string_too_short':
                errores[campo] = 'Este campo es obligatorio.'
            elif campo in ('nombre', 'correo', 'contrasena'):
                errores[campo] = 'Revisa este campo.'

        if not errores:
            general = 'Revisa los datos e inténtalo de nuevo.'

    # Errores de texto (por ejemplo, "El correo ya está registrado")
    elif isinstance(detalle, str):
        if 'correo' in detalle.lower():
            errores['correo'] = detalle
        else:
            general = detalle

    return errores, general

# Create your views here.
def catalogo(request):
    try:
        respuesta = requests.get(
            f"{API_URL}/productos",
            timeout=30
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
            'error': error,
            'api_url': API_URL
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
                timeout=TIMEOUT
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
                timeout=TIMEOUT
            )

            if respuesta.status_code == 201:
                messages.success(
                    request,
                    '¡Registro exitoso! Ya puedes iniciar sesión.'
                )
                return redirect('login')

            try:
                detalle = respuesta.json().get('detail')
            except ValueError:
                detalle = None

            errores, mensaje = traducir_errores(detalle)

            if not errores and not mensaje:
                mensaje = 'No fue posible registrar el usuario'

        except requests.RequestException:
            errores = {}
            mensaje = 'No se pudo conectar con el servidor'

        return render(
            request,
            'store/registro.html',
            {
                'error': mensaje,
                'errores': errores,
                # Se conservan nombre y correo; la contraseña nunca
                'valores': {'nombre': nombre, 'correo': correo}
            }
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
                timeout=TIMEOUT
            )

            respuesta.raise_for_status()
            # Si el admin eligió una imagen, subirla al producto nuevo
            archivo = request.FILES.get('imagen')
            if archivo:
                fallo = subir_imagen(respuesta.json()['id'], archivo, headers)
                if fallo:
                    messages.error(
                        request,
                        f'Producto creado, pero la imagen falló: {fallo}'
                    )

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
            timeout=TIMEOUT
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
            'error': error,
            'api_url': API_URL
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
                timeout=TIMEOUT
            )

            respuesta.raise_for_status()
            
            # Si el admin eligió una imagen nueva, reemplazar la anterior
            archivo = request.FILES.get('imagen')
            if archivo:
                fallo = subir_imagen(producto_id, archivo, headers)
                if fallo:
                    messages.error(
                        request,
                        f'Producto actualizado, pero la imagen falló: {fallo}'
                    )

            return redirect('dashboard')

        except requests.RequestException:
            error = 'No se pudo actualizar el producto'

            return render(
                request,
                'store/editar_producto.html',
                {
                    'producto': datos,
                    'error': error,
                    'api_url': API_URL
                }
            )

    # Consultar los datos actuales del producto
    try:
        respuesta = requests.get(
            f"{API_URL}/productos/{producto_id}",
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()
        producto = respuesta.json()

    except requests.RequestException:
        return redirect('dashboard')

    return render(
        request,
        'store/editar_producto.html',
        {
            'producto': producto,
            'api_url': API_URL
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
            timeout=TIMEOUT
        )

        if respuesta.status_code == 200:
            return redirect('dashboard')

        return redirect('dashboard')

    except requests.RequestException:
        return redirect('dashboard')
    
@require_POST
def agregar_producto(request, producto_id):

    # Verificar que haya una sesión iniciada
    if 'access_token' not in request.session:
        return redirect('login')

    # Los administradores no hacen pedidos
    if request.session.get('rol') == 'admin':
        return redirect('catalogo')

    headers = {
        'Authorization': f'Bearer {request.session["access_token"]}'
    }

    try:
        respuesta = requests.post(
            f"{API_URL}/pedidos/agregar/{producto_id}",
            headers=headers,
            timeout=TIMEOUT
        )

        if respuesta.status_code == 201:
            nombre = respuesta.json().get('nombre', 'Producto')
            messages.success(request, f'"{nombre}" se agregó a tus pedidos.')

        elif respuesta.status_code == 401:
            # El token expiró: cerrar sesión y pedir login de nuevo
            request.session.flush()
            return redirect('login')

        else:
            messages.error(
                request,
                respuesta.json().get('detail', 'No se pudo agregar el producto')
            )

    except (requests.RequestException, ValueError):
        messages.error(request, 'No se pudo conectar con el servidor')

    return redirect('catalogo')


def mis_pedidos(request):

    # Verificar que haya una sesión iniciada
    if 'access_token' not in request.session:
        return redirect('login')

    headers = {
        'Authorization': f'Bearer {request.session["access_token"]}'
    }

    pedidos = []
    error = None

    try:
        respuesta = requests.get(
            f"{API_URL}/pedidos/mis-pedidos",
            headers=headers,
            timeout=TIMEOUT
        )

        if respuesta.status_code == 401:
            request.session.flush()
            return redirect('login')

        respuesta.raise_for_status()
        pedidos = respuesta.json()

    except requests.RequestException:
        error = 'No se pudieron cargar tus pedidos'

    return render(
        request,
        'store/mis_pedidos.html',
        {
            'pedidos': pedidos,
            'error': error
        }
    )