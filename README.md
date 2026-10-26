# TeachGear

Proyecto académico para la gestión de productos y pedidos, desarrollado con Python, FastAPI, MongoDB Atlas y Django.

## Estructura del proyecto

```text
t2-techgaer/
├── techgear_api/
│   ├── models/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   └── .env
├── techgear_web/
├── .gitignore
└── README.md
```

## Tecnologías

- Python
- FastAPI
- Pydantic
- MongoDB Atlas
- PyMongo
- Django (frontend)

## Requisitos previos

- Python instalado.
- Git instalado.
- Una cuenta y un clúster de MongoDB Atlas.
- Acceso a una terminal.

## Configuración del backend

Desde la raíz del repositorio, entra en la carpeta del backend:

```bash
cd techgear_api
```

Crea y activa un entorno virtual en Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements.txt
```

### Variables de entorno

Crea un archivo `.env` dentro de `techgear_api/` con esta variable:

```env
MONGODB_URI="mongodb+srv://USUARIO:CONTRASENA@HOST/"
```

Reemplaza los valores de ejemplo por los datos de tu clúster de MongoDB Atlas. No compartas las credenciales reales ni las subas al repositorio.

### Ejecutar FastAPI

Desde `techgear_api/`, con el entorno virtual activo:

```bash
uvicorn main:app --reload
```

La API estará disponible en:

- Inicio: http://127.0.0.1:8000/
- Documentación interactiva: http://127.0.0.1:8000/docs
- Prueba de conexión: http://127.0.0.1:8000/probar-conexion

La ruta de prueba de conexión depende de la configuración de MongoDB Atlas y de que el archivo `.env` esté configurado correctamente.

## Configuración del frontend Django

El frontend se desarrollará dentro de `techgear_web/`.

Cuando el proyecto Django esté creado, sus instrucciones específicas de instalación y ejecución se documentarán en esta sección. Por el momento, el frontend está pendiente de implementación.

## Avance de la Clase 1

- Estructura inicial del backend y frontend.
- Conexión comprobada con MongoDB Atlas.
- Modelos Pydantic para productos y pedidos.
- Configuración inicial de dependencias.

## Seguridad

- No subir archivos `.env` ni contraseñas.
- No subir entornos virtuales.
- Mantener las credenciales fuera del código fuente.

## Historial de desarrollo

El desarrollo se registrará progresivamente mediante commits descriptivos en la rama `main`.
