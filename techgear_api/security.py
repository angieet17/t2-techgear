from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from database import settings

# Configuración para proteger contraseñas
password_hash = PasswordHash.recommended()

# Clave secreta para firmar los JWT
SECRET_KEY = settings.jwt_secret_key

if not SECRET_KEY:
    raise ValueError("No se encontró JWT_SECRET_KEY en el archivo .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Generar el hash de una contraseña
def obtener_hash(contrasena):
    return password_hash.hash(contrasena)


# Verificar una contraseña
def verificar_contrasena(contrasena, hash_guardado):
    return password_hash.verify(contrasena, hash_guardado)


# Crear un token JWT
def crear_token(datos):
    datos_token = datos.copy()

    fecha_expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos_token.update({"exp": fecha_expiracion})

    token = jwt.encode(
        datos_token,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token