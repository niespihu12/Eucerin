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
                    {"type": "input_text", "text": "Analiza esta imagen y proporciona una descripción detallada de lo que ves."},
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