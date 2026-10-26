from pydantic import BaseModel, Field


class Pedido(BaseModel):
    productos: list[str]
    total: float = Field(gt=0)
    estado: str = "pendiente"