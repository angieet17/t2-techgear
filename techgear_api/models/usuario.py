from pydantic import BaseModel, Field, ConfigDict


class Usuario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1)
    correo: str = Field(min_length=1)
    contrasena: str = Field(min_length=8)

class Credenciales(BaseModel):
    correo: str
    contrasena: str