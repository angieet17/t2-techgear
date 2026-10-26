from pydantic import BaseModel, Field


class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)