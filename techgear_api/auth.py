from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
import jwt

from database import usuarios_collection
from security import SECRET_KEY, ALGORITHM


# Leer el token enviado en la solicitud
esquema_bearer = HTTPBearer()


# Obtener el usuario que inició sesión
def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(esquema_bearer)
):
    token = credenciales.credentials

    try:
        datos = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = datos.get("sub")

        if not usuario_id or not ObjectId.is_valid(usuario_id):
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    usuario = usuarios_collection.find_one(
        {"_id": ObjectId(usuario_id)}
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return usuario


# Comprobar que el usuario sea administrador
def verificar_admin(
    usuario: dict = Depends(obtener_usuario_actual)
):
    if usuario.get("rol", "usuario") != "admin":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos de administrador"
        )

    return usuario