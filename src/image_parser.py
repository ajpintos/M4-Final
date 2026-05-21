import base64
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langfuse.decorators import observe, langfuse_context

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_MB = 20

VISION_PROMPT = (
    "Eres un especialista en extracción de texto de documentos legales escaneados.\n\n"
    "Tu tarea es extraer el texto completo del documento que aparece en la imagen, "
    "de forma fiel y precisa.\n\n"
    "Instrucciones:\n"
    "1. Transcribe TODO el texto visible, sin omitir ninguna sección.\n"
    "2. Preserva la estructura jerárquica: títulos, numeración de cláusulas, "
    "subcláusulas y listas.\n"
    "3. Mantén el orden original del documento (de arriba hacia abajo).\n"
    "4. Si hay texto ilegible o borroso, márcalo como [ILEGIBLE].\n"
    "5. No añadas interpretaciones, comentarios ni texto propio.\n"
    "6. Mantén los números de artículos, fechas, montos y nombres exactamente "
    "como aparecen.\n\n"
    "Devuelve únicamente el texto extraído, sin preámbulos ni explicaciones."
)


def _validate_image_path(image_path: str) -> Path:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo de imagen no encontrado: {image_path}")
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Formato no soportado '{path.suffix}'. "
            f"Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"Archivo demasiado grande: {size_mb:.1f} MB (máximo permitido: {MAX_FILE_SIZE_MB} MB)"
        )
    return path


def _encode_image_base64(image_path: Path) -> tuple[str, str]:
    """Devuelve (cadena_base64, mime_type)."""
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    mime_type = mime_map[image_path.suffix.lower()]
    with open(image_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode("utf-8")
    return b64, mime_type


@observe(name="parse_contract_image")
def parse_contract_image(image_path: str, document_label: str = "document") -> str:
    """Extrae el texto completo de una imagen de contrato usando GPT-4o Vision.

    Args:
        image_path: Ruta absoluta o relativa a una imagen PNG/JPG.
        document_label: Etiqueta legible para el trazado (ej: 'original', 'amendment').

    Returns:
        Texto extraído preservando la estructura y jerarquía del documento.
    """
    path = _validate_image_path(image_path)
    b64, mime_type = _encode_image_base64(path)

    langfuse_context.update_current_observation(
        input={"image_path": str(path), "document_label": document_label},
        metadata={"file_size_kb": round(path.stat().st_size / 1024, 1)},
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    message = HumanMessage(
        content=[
            {"type": "text", "text": VISION_PROMPT},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64}",
                    "detail": "high",
                },
            },
        ]
    )

    response = llm.invoke([message])
    extracted_text: str = response.content

    langfuse_context.update_current_observation(
        output=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
        metadata={"char_count": len(extracted_text)},
    )

    return extracted_text
