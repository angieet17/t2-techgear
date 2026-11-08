# TechGear

Tienda de tecnología en línea desarrollada como proyecto académico. Permite consultar un catálogo de productos con imágenes, registrarse, iniciar sesión, agregar productos a los pedidos del usuario y administrar el inventario desde un panel de administración.

- **Aplicación web:** https://TU-PROYECTO.vercel.app
- **API (documentación Swagger):** https://t2-techgear.onrender.com/docs

> La API está en el plan gratuito de Render: si lleva un rato sin uso, la primera petición puede tardar entre 30 y 60 segundos en responder.

## Funcionalidades

### Para visitantes y usuarios

- Catálogo de productos con imagen, descripción, precio y stock disponible.
- Registro de cuenta con validación de datos (la contraseña debe tener mínimo 8 caracteres) y aviso de registro exitoso.
- Inicio y cierre de sesión con autenticación JWT.
- Botón **Agregar producto** en el catálogo: crea el pedido y descuenta 1 unidad del stock.
- Productos sin stock marcados como **Agotado**.
- Sección **Mis pedidos** con el historial de productos agregados por el usuario.

### Para administradores

- Panel de administración con el total de productos registrados.
- Crear, editar y eliminar productos.
- Subir o reemplazar la imagen de cada producto (JPG, PNG o WEBP, máximo 1 MB).

## Arquitectura

```text
┌──────────────┐   HTTP + JWT   ┌──────────────┐   PyMongo   ┌───────────────┐
│    Django    │ ─────────────► │   FastAPI    │ ──────────► │ MongoDB Atlas │
│  (frontend)  │ ◄───────────── │  (API REST)  │ ◄────────── │ (base datos)  │
│   Vercel     │      JSON      │   Render     │             │               │
└──────────────┘                └──────────────┘             └───────────────┘
```

- **Django** solo se encarga de la interfaz. No tiene modelos propios: obtiene y guarda todos los datos a través de la API.
- **FastAPI** contiene la lógica de negocio, la autenticación y el acceso a la base de datos.
- **MongoDB Atlas** almacena usuarios, productos, imágenes y pedidos.
- El token JWT se guarda en la sesión de Django, que usa **cookies firmadas**, por lo que Django no necesita una base de datos para funcionar.

## Tecnologías

| Capa | Tecnologías |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn, Pydantic, Pydantic Settings |
| Base de datos | MongoDB Atlas, PyMongo |
| Seguridad | PyJWT, pwdlib (hash de contraseñas) |
| Frontend | Django, Bootstrap 5, Requests |
| Despliegue | Render (API), Vercel (web) |

## Estructura del repositorio

```text
t2-techgear/
├── README.md
├── .gitignore
├── techgear_api/
│   ├── main.py              # Endpoints de la API
│   ├── auth.py              # Usuario actual y verificación de administrador
│   ├── security.py          # Hash de contraseñas y creación de tokens JWT
│   ├── database.py          # Conexión a MongoDB y configuración
│   ├── probar_conexion.py   # Script para probar la conexión con Atlas
│   ├── promover_admin.py    # Script para convertir un usuario en administrador
│   ├── requirements.txt
│   └── models/
│       ├── producto.py
│       ├── pedido.py
│       └── usuario.py
└── techgear_web/
    ├── manage.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    ├── asgi.py
    ├── requirements.txt
    └── store/
        ├── views.py
        ├── urls.py
        └── templates/store/
            ├── base.html
            ├── catalogo.html
            ├── login.html
            ├── registro.html
            ├── mis_pedidos.html
            ├── dashboard.html
            └── editar_producto.html
```

## Instalación en local

### Requisitos previos

- Python 3.12
- Git
- Un cluster de MongoDB Atlas con su cadena de conexión

### 1. Clonar e instalar

```bash
git clone https://github.com/angieet17/t2-techgear.git
cd t2-techgear

python3 -m venv .venv
source .venv/bin/activate

pip install -r techgear_api/requirements.txt
pip install -r techgear_web/requirements.txt
```

### 2. Variables de entorno

Crear `techgear_api/.env`:

```env
MONGODB_URI=tu_cadena_de_conexion_de_mongodb
JWT_SECRET_KEY=una_clave_larga_y_secreta
```

Crear `techgear_web/.env`:

```env
DJANGO_SECRET_KEY=otra_clave_larga_y_secreta
DEBUG=True
TECHGEAR_API_URL=http://127.0.0.1:8001
```

### 3. Ejecutar la API

```bash
cd techgear_api
uvicorn main:app --reload --port 8001
```

- API: http://127.0.0.1:8001/
- Swagger: http://127.0.0.1:8001/docs
- Prueba de conexión: http://127.0.0.1:8001/probar-conexion

### 4. Ejecutar Django

En otra terminal, con el entorno virtual activado:

```bash
cd techgear_web
python3 manage.py runserver 8000
```

Abrir http://127.0.0.1:8000/

> No hace falta ejecutar `migrate`: Django no usa base de datos propia, ya que los datos viven en MongoDB y las sesiones se guardan en cookies firmadas. Por lo mismo, el panel `/admin/` de Django no está disponible; la administración se hace desde el panel de la aplicación.

### 5. Crear un administrador

Todos los usuarios nuevos se registran con el rol `usuario`. Para convertir una cuenta en administrador, primero regístrala desde la web y luego ejecuta, desde `techgear_api`:

```bash
python3 promover_admin.py
```

El script pide el correo de la cuenta y le asigna el rol `admin`. Después de ejecutarlo, esa persona debe cerrar sesión y volver a entrar.

## Variables de entorno

| Variable | Dónde | Descripción | Obligatoria |
|---|---|---|---|
| `MONGODB_URI` | API | Cadena de conexión de MongoDB Atlas | Sí |
| `JWT_SECRET_KEY` | API | Clave para firmar los tokens JWT | Sí |
| `DJANGO_SECRET_KEY` | Web | Clave secreta de Django (también firma las cookies de sesión) | Sí |
| `DEBUG` | Web | `True` solo en desarrollo; por defecto es `False` | No |
| `TECHGEAR_API_URL` | Web | URL de la API. Por defecto apunta a la API en Render | No |

## Endpoints de la API

| Método | Ruta | Descripción | Acceso |
|---|---|---|---|
| POST | `/usuarios/registro` | Registrar un usuario | Público |
| POST | `/usuarios/login` | Iniciar sesión y recibir el JWT | Público |
| GET | `/productos` | Listar productos | Público |
| GET | `/productos/{id}` | Ver un producto | Público |
| GET | `/productos/{id}/imagen` | Obtener la imagen de un producto | Público |
| POST | `/productos` | Crear un producto | Administrador |
| PUT | `/productos/{id}` | Actualizar un producto | Administrador |
| DELETE | `/productos/{id}` | Eliminar un producto | Administrador |
| POST | `/productos/{id}/imagen` | Subir o reemplazar la imagen | Administrador |
| POST | `/pedidos/agregar/{producto_id}` | Agregar un producto a los pedidos y descontar 1 de stock | Usuario autenticado |
| GET | `/pedidos/mis-pedidos` | Listar los pedidos del usuario autenticado | Usuario autenticado |
| GET | `/pedidos` | Listar todos los pedidos | Administrador |
| POST | `/pedidos` | Crear un pedido manualmente | Administrador |
| GET | `/pedidos/{id}` | Ver un pedido | Administrador |

Las rutas protegidas esperan el encabezado `Authorization: Bearer <token>`.

## Seguridad

- Las contraseñas se guardan con hash; nunca en texto plano.
- Los tokens JWT expiran a los 30 minutos y la sesión de Django dura lo mismo.
- Los permisos se validan en la API según el rol del token; ocultar un botón en la web no es la única protección.
- El descuento de stock es atómico: si dos personas intentan comprar la última unidad al mismo tiempo, solo una lo consigue, y el stock nunca queda en negativo.
- Si falla el guardado de un pedido, el stock descontado se devuelve.
- Las imágenes se validan por tipo (JPG, PNG, WEBP) y por tamaño (máximo 1 MB).
- Los formularios de Django usan protección CSRF.
- Los archivos `.env` están excluidos del repositorio.

**Importante:** no publicar credenciales reales ni archivos `.env` en GitHub.

## Despliegue

### API en Render

- **Root directory:** `techgear_api`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Variables:** `MONGODB_URI` y `JWT_SECRET_KEY`

### Web en Vercel

- **Root directory:** `techgear_web`
- **Variables:** `DJANGO_SECRET_KEY`, `DEBUG=False` y, opcionalmente, `TECHGEAR_API_URL`

Ambos servicios se redespliegan automáticamente con cada `git push`. Al hacer cambios que afecten a la API y a la web a la vez, conviene esperar a que Render termine antes de probar la web.

## Limitaciones conocidas

- La API en el plan gratuito de Render se suspende por inactividad, por lo que la primera petición puede tardar.
- Cada clic en **Agregar producto** agrega una unidad; todavía no se puede elegir la cantidad.
- Los pedidos quedan en estado `pendiente`; aún no existe un flujo de pago ni de cambio de estado.
- Las imágenes se guardan en MongoDB, por lo que se limitan a 1 MB para no agotar el espacio del plan gratuito.

## Posibles mejoras

- Selección de cantidad y carrito con varios productos por pedido.
- Gestión de estados de pedido desde el panel de administración.
- Almacenar las imágenes en un servicio externo (por ejemplo, Cloudinary).
- Buscador y filtros en el catálogo.

## Autoría

Proyecto académico desarrollado por [angieet17](https://github.com/angieet17) de forma incremental, con commits descriptivos que integran API REST, base de datos, autenticación y aplicación web.