
from fastapi import FastAPI, HTTPException
from bson import ObjectId

from database import (
    client,
    productos_collection,
    pedidos_collection,
)
from models.producto import Producto
from models.pedido import Pedido

app = FastAPI(title="TechGear API")


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

