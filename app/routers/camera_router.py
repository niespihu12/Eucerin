from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.models.camera_models import Camara, CamaraResponse

camera_router = APIRouter()

camera_state: Dict[str, Any] = {
    "camera": False  
}

@camera_router.get("/", tags=["Camara"])
async def get_camera() -> CamaraResponse:
    return CamaraResponse(camera=camera_state["camera"])


@camera_router.put("/", tags=["Camara"])
async def put_camera(data: Camara) -> CamaraResponse:
    camera_state["camera"] =  data
    return CamaraResponse(camera=camera_state["camera"])