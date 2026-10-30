# TechGear

Proyecto académico para la gestión de productos, pedidos y usuarios de una tienda de tecnología.

El backend está desarrollado con FastAPI y MongoDB Atlas. El frontend utiliza Django y se comunica con la API para mostrar el catálogo y gestionar el registro e inicio de sesión de los usuarios.

## Estado del proyecto

- API REST desarrollada con FastAPI.
- CRUD de productos implementado.
- CRUD de pedidos implementado.
- Conexión con MongoDB Atlas mediante PyMongo y Pydantic Settings.
- Modelos Pydantic para productos, pedidos y usuarios.
- Registro de usuarios desde Django.
- Contraseñas protegidas mediante hash.
- Autenticación mediante JWT.
- Inicio y cierre de sesión.
- Almacenamiento del token JWT en la sesión de Django.
- Catálogo dinámico conectado con FastAPI.
- Plantillas HTML para catálogo, registro e inicio de sesión.

## Estructura del repositorio

```text
t2-techgaer/
├── README.md
├── .gitignore
├── .venv/
├── techgear_api/
│   ├── .env
│   ├── database.py
│   ├── main.py
│   ├── security.py
│   ├── requirements.txt
│   └── models/
│       ├── __init__.py
│       ├── producto.py
│       ├── pedido.py
│       └── usuario.py
└── techgear_web/
    ├── .env
    ├── manage.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    ├── asgi.py
    ├── requirements.txt
    └── store/
        ├── views.py
        ├── urls.py
        └── templates/
            └── store/
                ├── base.html
                ├── catalogo.html
                ├── login.html
                └── registro.html
```

## Tecnologías utilizadas

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- MongoDB Atlas
- PyMongo
- PyJWT
- pwdlib
- Django
- SQLite
- Requests
- python-dotenv

## Requisitos previos

- Python 3.12.
- Git.
- Cuenta y cluster de MongoDB Atlas.
- Terminal o consola.

## 1. Configuración del entorno

Clonar el repositorio:

```bash
git clone https://github.com/angieet17/t2-techgear.git
cd t2-techgaer
```

Crear y activar el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r techgear_api/requirements.txt
pip install -r techgear_web/requirements.txt
```

## 2. Configuración de FastAPI

Crear el archivo `techgear_api/.env`:

```env
MONGODB_URI=tu_conexion_de_mongodb
JWT_SECRET_KEY=tu_clave_secreta
```

Las variables contienen las credenciales de conexión y la clave para firmar los tokens JWT.

Ejecutar la API desde `techgear_api`:

```bash
cd techgear_api
uvicorn main:app --reload --port 8001
```

Direcciones:

- API: http://127.0.0.1:8001/
- Swagger: http://127.0.0.1:8001/docs
- Redoc: http://127.0.0.1:8001/redoc
- Prueba de conexión: http://127.0.0.1:8001/probar-conexion

## 3. Configuración de Django

Crear el archivo `techgear_web/.env`:

```env
DJANGO_SECRET_KEY=tu_clave_secreta_de_django
```

Desde otra terminal, activar el entorno virtual y entrar a `techgear_web`:

```bash
cd ~/Escritorio/t2-techgaer
source .venv/bin/activate
cd techgear_web
```

Ejecutar las migraciones:

```bash
python3 manage.py migrate
```

Iniciar Django:

```bash
python3 manage.py runserver 8000
```

Abrir la aplicación:

http://127.0.0.1:8000/

## 4. Funcionalidades de la aplicación web

### Catálogo

- Consulta los productos registrados en MongoDB Atlas mediante FastAPI.
- Muestra nombre, descripción, precio y stock.

### Registro de usuarios

- Permite registrar nuevos usuarios.
- Valida los datos mediante los modelos Pydantic.
- Protege las contraseñas mediante hash.
- Evita registros con correos duplicados.

### Inicio de sesión

- Envía las credenciales a FastAPI.
- Verifica el correo y la contraseña.
- Recibe un token JWT.
- Guarda el token en la sesión de Django.

### Cierre de sesión

- Elimina los datos de la sesión de Django.
- Devuelve al usuario al catálogo.

## 5. Endpoints principales

### Productos

- `POST /productos`
- `GET /productos`
- `GET /productos/{producto_id}`
- `PUT /productos/{producto_id}`
- `DELETE /productos/{producto_id}`

### Pedidos

- `POST /pedidos`
- `GET /pedidos`
- `GET /pedidos/{pedido_id}`

### Usuarios

- `POST /usuarios/registro`
- `POST /usuarios/login`

## 6. Seguridad

- Las contraseñas se almacenan mediante hash.
- Los tokens JWT tienen una duración de 30 minutos.
- Las claves secretas se configuran mediante variables de entorno.
- Los archivos `.env` están excluidos del control de versiones.
- Se utiliza protección CSRF en los formularios de Django.

**Importante:** no publicar credenciales reales ni archivos `.env` en GitHub.

## 7. Historial de desarrollo

Proyecto académico desarrollado de forma incremental mediante commits descriptivos, integrando API REST, base de datos, autenticación y aplicación web.