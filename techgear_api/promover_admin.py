from database import usuarios_collection

# Solicitar el correo de la cuenta que será administradora
correo = input("Correo del usuario: ").strip()

# Buscar el usuario y asignarle el rol de administrador
resultado = usuarios_collection.update_one(
    {"correo": correo},
    {"$set": {"rol": "admin"}}
)

if resultado.matched_count == 0:
    print("No se encontró ningún usuario con ese correo.")
else:
    print("Rol de administrador asignado correctamente.")
