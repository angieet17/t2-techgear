from database import client

try:
    resultado = client.admin.command("ping")
    print("¡Conexión exitosa con MongoDB Atlas!")
    print(resultado)
except Exception as error:
    print("Error de conexión:", error)
finally:
    client.close()