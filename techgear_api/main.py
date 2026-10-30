
from fastapi import FastAPI, HTTPException
from bson import ObjectId

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
        "correo": usuario["correo"]
    })

    return {
        "mensaje": "Inicio de sesión exitoso",
        "access_token": token,
        "token_type": "bearer"
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
def crear_producto(producto: Producto):
    resultado = productos_collection.insert_one(
        producto.model_dump()
    )

    nuevo_producto = productos_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    return convertir_documento(nuevo_producto)


@app.get("/productos", tags=["Productos"])
def listar_productos():
    productos = productos_collection.find()
    return [convertir_documento(p) for p in productos]


@app.get("/productos/{producto_id}", tags=["Productos"])
def obtener_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(
            status_code=400,
            detail="El identificador del producto no es válido",
        )

    producto = productos_collection.find_one(
        {"_id": ObjectId(producto_id)}
    )

    if producto is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado",
        )

    return convertir_documento(producto)


@app.put("/productos/{producto_id}", tags=["Productos"])
def actualizar_producto(producto_id: str, producto: Producto):
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
        {"_id": ObjectId(producto_id)}
    )

    return convertir_documento(producto_actualizado)


@app.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(producto_id: str):
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