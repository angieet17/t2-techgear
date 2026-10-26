from fastapi import FastAPI

app = FastAPI(title="TechGear API")


@app.get("/")
def inicio():
    return {"mensaje": "TechGear API funcionando"}

from database import client


@app.get("/probar-conexion")
def probar_conexion():
    try:
        resultado = client.admin.command("ping")
        return {
            "mensaje": "Conexión con MongoDB exitosa",
            "resultado": resultado
        }
    except Exception as error:
        return {
            "mensaje": "Error de conexión con MongoDB",
            "detalle": str(error)
        }