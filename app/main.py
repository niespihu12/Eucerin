from fastapi import FastAPI
from app.routers.camera_router import camera_router
from app.routers.ai_router import ai_router
from app.utils.http_error_handler import HTTPErrorHandler
from app.utils.cors import add_cors_middleware


app = FastAPI()

# Cors Middleware
app.add_middleware(HTTPErrorHandler)
add_cors_middleware(app)

app.include_router(prefix="/api/camara", router=camera_router)
app.include_router(prefix="/api/ai", router=ai_router)
