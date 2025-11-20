from typing import Dict
from click import File
from pydantic import BaseModel


class AI(BaseModel):
    file: bytes = File(...)

class AIResponse(BaseModel):
    result:dict