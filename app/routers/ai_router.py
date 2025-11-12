from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any
import base64
from openai import OpenAI
from app.models.ai_models import AIResponse
from dotenv import load_dotenv
load_dotenv(override=True)

ai_router = APIRouter()

ai_state: Dict[str, Any] = {
    "result": ""
}

client = OpenAI()


@ai_router.get("/", tags=["AI"])
async def get_response_AI() -> AIResponse:
    return AIResponse(result=ai_state["result"])


@ai_router.put("/", tags=["AI"])
async def put_AI(file: UploadFile = File(...)) -> AIResponse:
    image_data = await file.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    content_type = file.content_type or "image/jpeg"
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analiza cuidadosamente la imagen proporcionada y determina de forma precisa las características dermatológicas visibles. Si en la imagen no se evidencia una persona, responde únicamente: “En la imagen no se evidencia una persona.”. Si detectas una persona, analiza su piel y responde estrictamente en este formato, sin agregar texto adicional: Tipo_de_Piel: [Normal | Seca | Mixta | Grasa], Presencia_Manchas_o_Pigmentacion: [SI | NO], Presencia_de_Imperfecciones: [SI | NO], Zona: [Rostro | Cuerpo]. Para determinar el tipo de piel, evalúa brillo, textura, poros y uniformidad; para manchas o pigmentación, identifica zonas oscuras o tono desigual; para imperfecciones, detecta granos, poros inflamados o brotes visibles; y para la zona, define si corresponde al rostro o al cuerpo según la proporción de rasgos humanos presentes. Si no se puede realizar el análisis por baja calidad o falta de claridad, responde exactamente: “No se pudo procesar bien la imagen."},
                    {
                        "type": "input_image",
                        "image_url": f"data:{content_type};base64,{base64_image}",
                    },
                ],
            }
        ],
        max_output_tokens=1000
    )
    result = response.output_text
    ai_state["result"] = result

@ai_router.delete('/delete', tags=["AI"])
async def delete_AI() -> AIResponse:
    ai_state["result"] = ""
    return AIResponse(result="")