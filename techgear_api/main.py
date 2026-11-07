
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Response
from datetime import datetime, timezone

from auth import verificar_admin, obtener_usuario_actual
from bson import ObjectId, Binary

from database import (
    client,
    productos_collection,
    pedidos_collection,
    usuarios_collection,
)
from models.producto import Producto
from models.pedido import Pedido
from models.usuario import Usuario, Credenciales

from security import obtener_hash, verificar_contrasena, crear_token

app = FastAPI(title="TechGear API")

# =========================
# REGISTRO DE USUARIOS
# =========================

@app.post("/usuarios/registro", status_code=201, tags=["Usuarios"])
def registrar_usuario(usuario: Usuario):

    # Comprobar si el correo ya está registrado
    usuario_existente = usuarios_collection.find_one(
        {"correo": usuario.correo}
    )

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    # Convertir los datos del usuario en un diccionario
    datos_usuario = usuario.model_dump()


    # Asignar el rol predeterminado
    datos_usuario["rol"] = "usuario"

    # Proteger la contraseña
    datos_usuario["contrasena"] = obtener_hash(
        usuario.contrasena
    )

    # Guardar el usuario en MongoDB
    resultado = usuarios_collection.insert_one(datos_usuario)

    # Consultar el usuario recién creado
    nuevo_usuario = usuarios_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    # No devolver la contraseña ni su hash
    nuevo_usuario.pop("contrasena")

    return convertir_documento(nuevo_usuario)

# =========================
# INICIO DE SESIÓN
# =========================

@app.post("/usuarios/login", tags=["Usuarios"])

def iniciar_sesion(credenciales: Credenciales):
    correo = credenciales.correo
    contrasena = credenciales.contrasena

    # Buscar el usuario por correo
    usuario = usuarios_collection.find_one(
        {"correo": correo}
    )

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Verificar la contraseña
    contrasena_correcta = verificar_contrasena(
        contrasena,
        usuario["contrasena"]
    )

    if not contrasena_correcta:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Crear el token JWT
    token = crear_token({
        "sub": str(usuario["_id"]),
        "correo": usuario["correo"],
        "rol": usuario.get("rol", "usuario")
    })

    return {
        "mensaje": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.get("rol", "usuario")
    }

# Convierte el ObjectId de MongoDB en texto
def convertir_documento(documento):
    documento["id"] = str(documento.pop("_id"))
    return documento


@app.get("/")
def inicio():
    return {"mensaje": "TechGear API funcionando"}


@app.get("/probar-conexion")
def probar_conexion():
    resultado = client.admin.command("ping")
    return {
        "mensaje": "Conexión con MongoDB exitosa",
        "resultado": resultado,
    }


# =========================
# CRUD DE PRODUCTOS
# =========================

@app.post("/productos", status_code=201, tags=["Productos"])
def crear_producto(
    producto: Producto,
    usuario: dict = Depends(verificar_admin)
    ):
    resultado = productos_collection.insert_one(
        producto.model_dump()
    )

    nuevo_producto = productos_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    return convertir_documento(nuevo_producto)


@app.get("/productos", tags=["Productos"])
def listar_productos():
    productos = productos_collection.find({}, {"imagen": 0})
    return [convertir_documento(p) for p in productos]


@app.get("/productos/{producto_id}", tags=["Productos"])
def obtener_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    producto = productos_collection.find_one(
        {"_id": ObjectId(producto_id)},
        {"imagen": 0}
    )

    if producto is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return convertir_documento(producto)


@app.put("/productos/{producto_id}", tags=["Productos"])
def actualizar_producto(
    producto_id: str,
    producto: Producto,
    usuario: dict = Depends(verificar_admin)
    ):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    resultado = productos_collection.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": producto.model_dump()},
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    producto_actualizado = productos_collection.find_one(
        {"_id": ObjectId(producto_id)},
        {"imagen": 0}
    )

    return convertir_documento(producto_actualizado)


@app.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(
    producto_id: str,
    usuario: dict = Depends(verificar_admin)
    ):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    resultado = productos_collection.delete_one(
        {"_id": ObjectId(producto_id)}
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return {"mensaje": "Producto eliminado correctamente"}


# =========================
# REGISTRO Y CONSULTA DE PEDIDOS
# =========================
# =========================
# IMAGEN DE LOS PRODUCTOS
# =========================

TIPOS_IMAGEN = ["image/jpeg", "image/png", "image/webp"]
MAX_IMAGEN_BYTES = 1024 * 1024  # 1 MB


@app.post("/productos/{producto_id}/imagen", tags=["Productos"])
async def subir_imagen_producto(
    producto_id: str,
    imagen: UploadFile = File(...),
    usuario: dict = Depends(verificar_admin)
    ):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    if imagen.content_type not in TIPOS_IMAGEN:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Usa JPG, PNG o WEBP",
        )

    # Leemos un byte de más para detectar si se pasa del límite
    contenido = await imagen.read(MAX_IMAGEN_BYTES + 1)

    if len(contenido) > MAX_IMAGEN_BYTES:
        raise HTTPException(
            status_code=400,
            detail="La imagen pesa más de 1 MB",
        )

    resultado = productos_collection.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": {
            "imagen": Binary(contenido),
            "imagen_tipo": imagen.content_type,
            "tiene_imagen": True,
        }},
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return {"mensaje": "Imagen guardada correctamente"}


@app.get("/productos/{producto_id}/imagen", tags=["Productos"])
def obtener_imagen_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    producto = productos_collection.find_one(
        {"_id": ObjectId(producto_id)},
        {"imagen": 1, "imagen_tipo": 1}
    )

    if producto is None or "imagen" not in producto:
        raise HTTPException(
            status_code=404,
            detail="El producto no tiene imagen",
        )

    return Response(
        content=bytes(producto["imagen"]),
        media_type=producto.get("imagen_tipo", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=3600"},
    )
# =========================
# PEDIDOS DEL USUARIO
# =========================
@app.post("/pedidos/agregar/{producto_id}", status_code=201, tags=["Pedidos"])
def agregar_producto_a_pedidos(
    producto_id: str,
    usuario: dict = Depends(obtener_usuario_actual)
    ):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    # Descuenta 1 de stock SOLO si todavía hay stock.
    # La operación es atómica: dos personas no pueden comprar la última unidad.
    producto = productos_collection.find_one_and_update(
        {"_id": ObjectId(producto_id), "stock": {"$gt": 0}},
        {"$inc": {"stock": -1}},
    )

    if producto is None:
        existe = productos_collection.find_one({"_id": ObjectId(producto_id)})
        if existe is None:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado",
            )
        raise HTTPException(
            status_code=400,
            detail="Producto agotado",
        )

    pedido = {
        "usuario_id": str(usuario["_id"]),
        "correo": usuario["correo"],
        "producto_id": producto_id,
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": 1,
        "productos": [producto["nombre"]],
        "total": producto["precio"],
        "estado": "pendiente",
        "fecha": datetime.now(timezone.utc).isoformat(),
    }

    try:
        resultado = pedidos_collection.insert_one(pedido)
    except Exception:
        # Si no se pudo guardar el pedido, devolvemos el stock
        productos_collection.update_one(
            {"_id": ObjectId(producto_id)},
            {"$inc": {"stock": 1}},
        )
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el pedido",
        )

    pedido["_id"] = resultado.inserted_id
    return convertir_documento(pedido)


@app.get("/pedidos/mis-pedidos", tags=["Pedidos"])
def listar_mis_pedidos(usuario: dict = Depends(obtener_usuario_actual)):
    pedidos = pedidos_collection.find(
        {"usuario_id": str(usuario["_id"])}
    ).sort("_id", -1)
    return [convertir_documento(p) for p in pedidos]

@app.post("/pedidos", status_code=201, tags=["Pedidos"])
def crear_pedido(pedido: Pedido):
    resultado = pedidos_collection.insert_one(
        pedido.model_dump()
    )

    nuevo_pedido = pedidos_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    return convertir_documento(nuevo_pedido)


@app.get("/pedidos", tags=["Pedidos"])
def listar_pedidos():
    pedidos = pedidos_collection.find()
    return [convertir_documento(p) for p in pedidos]


@app.get("/pedidos/{pedido_id}", tags=["Pedidos"])
def obtener_pedido(pedido_id: str):
    if not ObjectId.is_valid(pedido_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del pedido no es válido",
        )

    pedido = pedidos_collection.find_one(
        {"_id": ObjectId(pedido_id)}
    )

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido no encontrado",
        )

    return convertir_documento(pedido)