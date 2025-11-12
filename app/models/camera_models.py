from pydantic import BaseModel


class Camara(BaseModel):
    camera: bool

class CamaraResponse(BaseModel):
    camera:bool