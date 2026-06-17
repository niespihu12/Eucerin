import json
from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any
import base64
from openai import OpenAI
from app.models.ai_models import AIResponse
from dotenv import load_dotenv

load_dotenv(override=True)

ai_router = APIRouter()

ai_state: Dict[str, Any] = {"result": ""}

client = OpenAI()


@ai_router.get("/", tags=["AI"])
async def get_response_AI() -> AIResponse:
    return AIResponse(result=ai_state["result"])


@ai_router.put("/", tags=["AI"])
async def put_AI(file: UploadFile = File(...)) -> AIResponse:
    try:
        image_data = await file.read()
        print(f"DEBUG: Tamaño de imagen recibida: {len(image_data)} bytes")
        print(f"DEBUG: Tipo de contenido: {file.content_type}")

        if not image_data or len(image_data) < 1024:
            return AIResponse(result={"error": "Imagen muy pequeña o vacía"})

        base64_image = base64.b64encode(image_data).decode("utf-8")
        print(f"DEBUG: Tamaño base64: {len(base64_image)} caracteres")

        content_type = file.content_type or "image/jpeg"

        if not base64_image or len(base64_image) < 100:
            return AIResponse(result={"error": "Base64 inválido"})

        response = client.responses.create(
            model="gpt-4o",
            instructions=(
                "Eres un asistente de análisis cosmético de la piel para una marca de "
                "cuidado facial (skincare). Tu función es evaluar la condición VISIBLE de "
                "la piel (textura, hidratación, imperfecciones, pigmentación, líneas) con "
                "fines exclusivamente cosméticos y de recomendación de productos. NO "
                "identificas, reconoces ni nombras a ninguna persona; solo describes "
                "características generales de la piel visible. Estas evaluaciones son "
                "orientativas y no constituyen un diagnóstico médico. Si el rostro es "
                "visible, SIEMPRE realiza el análisis cosmético solicitado y no te niegues."
            ),
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """
                                Analiza detalladamente la imagen proporcionada siguiendo las siguientes reglas estrictas: 

                                REGLAS GENERALES 
                                1. Si en la imagen no se evidencia una persona, responde exactamente: "En la imagen no se evidencia una persona." 
                                2. Usa la respuesta "No se pudo procesar bien la imagen." ÚNICAMENTE cuando el rostro sea totalmente irreconocible (imagen casi negra, completamente borrosa, vacía o sin rostro alguno). Si el rostro es visible aunque la calidad no sea perfecta, DEBES realizar el análisis cosmético igualmente y NO debes negarte ni excusarte.
                                3. Si la imagen muestra el cuerpo sin un rostro claramente visible, responde exactamente: "La imagen no corresponde a un rostro humano identificable." 
                                4. Si el rostro está visible, responde únicamente en formato JSON, sin agregar texto fuera del JSON y sin explicaciones adicionales. 

                                INSTRUCCIONES DE ANÁLISIS 
                                Debes identificar características dermatológicas visibles evaluando: 
                                - Textura 
                                - Porosidad 
                                - Brillo o sequedad 
                                - Uniformidad del tono 
                                - Líneas finas o arrugas 
                                - Imperfecciones 
                                - Pigmentación 
                                - Ojeras o bolsas 
                                - Señales aproximadas de edad 

                                DESCRIPCIÓN DE TIPOS DE PIEL (criterios visuales obligatorios) 

                                PIEL NORMAL: 
                                - Textura uniforme 
                                - No se nota brillo graso excesivo 
                                - No hay descamación seca visible 
                                - Poros no muy marcados 
                                - Apariencia hidratada y balanceada 

                                PIEL SECA: 
                                - Descamación o apariencia opaca/áspera 
                                - Microrresquebraduras o líneas superficiales secas 
                                - Poco brillo natural 
                                - Sensación visual de tirantez o poca elasticidad 

                                PIEL GRASA: 
                                - Brillo notable en frente, nariz y mejillas 
                                - Poros dilatados visibles 
                                - Textura más grasosa o con tendencia a imperfecciones 
                                - Posibles granos o puntos negros 

                                PIEL MIXTA: 
                                - Zona T (frente, nariz y mentón) brillante o con poros visibles 
                                - Mejillas normales o secas 
                                - Contraste claro entre Zona T y resto del rostro 

                                CARACTERÍSTICAS A EVALUAR (PORCENTAJES Y LÓGICA SI/NO) 
                                Debes asignar valores porcentuales del 0% al 100% para: 
                                - Manchas o pigmentación 
                                - Imperfecciones 
                                - Bolsas/Ojeras 
                                - Arrugas 

                                REGLA OBLIGATORIA: 
                                Si el valor es ≥ 50% → el campo debe mostrar "SI". 
                                Si el valor es < 50% → el campo debe mostrar "NO". 

                                EDAD APROXIMADA 
                                Determina el rango de edad basado en: 
                                - Elasticidad 
                                - Presencia y profundidad de arrugas 
                                - Flacidez 
                                - Pigmentación 
                                - Textura de la piel 
                                - Contorno facial 

                                Rangos permitidos: 18-23, 24-29, 30-40, 41-54, 55+. 

                                REGLAS MEJORADAS PARA MAYOR PRECISIÓN EN LA EDAD: 
                                1. Si la piel muestra alta elasticidad, firmeza, ausencia de arrugas marcadas y una apariencia claramente juvenil, debes asignar SIEMPRE el rango 18-23. 
                                2. En caso de duda entre dos rangos, elige SIEMPRE el rango más joven. 
                                3. Las líneas muy superficiales o mínimas NO deben considerarse arrugas suficientes para clasificar una edad mayor. 
                                4. Si la persona parece tener entre 21, 22 o 23 años, debes asignar estrictamente el rango 18-23. 
                                5. Bajo ninguna circunstancia asignes el rango 24-29 si el rostro puede corresponder a alguien de 22 o 23. 
                                6. Señales claras del rango 18-23: 
                                - Ninguna arruga real 
                                - Piel firme y elástica 
                                - Cero flacidez 
                                - Tonalidad uniforme 
                                - Ojeras suaves o leves 
                                - Contorno facial definido 

                                FORMATO JSON OBLIGATORIO DE RESPUESTA 

                                { 
                                "Tipo_de_Piel": "[Normal|Seca|Mixta|Grasa]",
                                "Edad_Aproximada": "[18-23|24-29|30-40|41-54|55+]",
                                "Analisis": { 
                                    "Manchas_Pigmentacion": { 
                                    "Porcentaje": 0-100, 
                                    "Presencia": "[SI|NO]" 
                                    }, 
                                    "Imperfecciones": { 
                                    "Porcentaje": 0-100, 
                                    "Presencia": "[SI|NO]" 
                                    }, 
                                    "Bolsas_Ojeras": { 
                                    "Porcentaje": 0-100, 
                                    "Presencia": "[SI|NO]" 
                                    }, 
                                    "Arrugas": { 
                                    "Porcentaje": 0-100, 
                                    "Presencia": "[SI|NO]" 
                                    } 
                                }, 
                                "Zona": "Rostro" 
                                }
                            """,
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{base64_image}",
                            "detail": "high",
                        },
                    ],
                }
            ],
            max_output_tokens=1000,
        )

        result_text = response.output_text
        print(f"DEBUG: Respuesta del modelo (string): {result_text}")
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()

        print(f"DEBUG: Texto limpiado: {cleaned_text}")
        try:
            result_dict = json.loads(cleaned_text)
            print(f"DEBUG: JSON parseado correctamente: {result_dict}")
        except json.JSONDecodeError as e:
            print(f"ERROR: No se pudo parsear el JSON: {str(e)}")
            result_dict = {
                "error": "La respuesta del modelo no es JSON válido",
                "raw": cleaned_text,
            }

        ai_state["result"] = result_dict
        return AIResponse(result=result_dict)

    except Exception as e:
        print(f"ERROR en put_AI: {str(e)}")
        return AIResponse(result={"error": str(e)})


# @ai_router.delete('/delete', tags=["AI"])
# async def delete_AI() -> AIResponse:
#     ai_state["result"] = ""
#     return AIResponse(result="")
