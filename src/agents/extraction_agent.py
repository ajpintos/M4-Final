from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe, langfuse_context

from src.models import ContractChangeOutput

SYSTEM_PROMPT = """\
Eres un Auditor Legal especializado en análisis de enmiendas y modificaciones contractuales \
para el equipo de Compliance de LegalMove.

Tu responsabilidad exclusiva es identificar, aislar y describir con precisión quirúrgica \
TODOS los cambios introducidos por la enmienda sobre el contrato original.

**Reglas estrictas:**
1. Usa el mapa contextual proporcionado como guía de estructura antes de comparar el texto.
2. Compara párrafo a párrafo, cláusula a cláusula, para no omitir ningún cambio.
3. Clasifica cada cambio con uno de estos tipos:
   - ADICIÓN: texto completamente nuevo en la enmienda, ausente en el original.
   - ELIMINACIÓN: texto presente en el original que fue removido.
   - MODIFICACIÓN: texto que existía y fue alterado (indica texto anterior → texto nuevo).
4. Para cada MODIFICACIÓN, transcribe el fragmento anterior y el nuevo.
5. Identifica el identificador exacto de cada sección afectada (ej: "Cláusula 3.2", \
"Artículo 7 - Pago").
6. Agrupa los temas legales/comerciales afectados (ej: "Pagos y Montos", "Plazos", \
"Territorio", "Confidencialidad", "Penalidades").
7. El campo summary_of_the_change debe ser exhaustivo y apto para revisión de compliance \
legal, describiendo cada cambio con claridad y precisión.
8. NO omitas ningún cambio, por menor que parezca.\
"""

HUMAN_TEMPLATE = """\
## MAPA CONTEXTUAL (generado por el Analista Senior):
{context_map}

---

## CONTRATO ORIGINAL (texto completo):
{original_text}

---

## ENMIENDA / ADENDA (texto completo):
{amendment_text}

---

Analiza todos los cambios y genera el reporte estructurado completo.\
"""


class ExtractionAgent:
    """Agente 2: Extrae y clasifica todos los cambios introducidos por la enmienda."""

    def __init__(self, model: str = "gpt-4o") -> None:
        llm = ChatOpenAI(model=model, temperature=0).with_structured_output(
            ContractChangeOutput
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_TEMPLATE),
        ])
        self._chain = prompt | llm

    @observe(name="extraction_agent")
    def run(
        self,
        context_map: str,
        original_text: str,
        amendment_text: str,
    ) -> ContractChangeOutput:
        """Extrae todos los cambios de la enmienda y devuelve un modelo Pydantic validado.

        Args:
            context_map: Mapa estructural producido por ContextualizationAgent.
            original_text: Texto completo del contrato original.
            amendment_text: Texto completo de la enmienda.

        Returns:
            ContractChangeOutput con sections_changed, topics_touched y summary.
        """
        langfuse_context.update_current_observation(
            input={
                "context_map_char_count": len(context_map),
                "original_char_count": len(original_text),
                "amendment_char_count": len(amendment_text),
            },
            metadata={"model": "gpt-4o", "role": "extraction", "output_format": "structured"},
        )

        result: ContractChangeOutput = self._chain.invoke({
            "context_map": context_map,
            "original_text": original_text,
            "amendment_text": amendment_text,
        })

        langfuse_context.update_current_observation(
            output={
                "sections_changed": result.sections_changed,
                "topics_touched": result.topics_touched,
                "summary_preview": result.summary_of_the_change[:300] + "..."
                if len(result.summary_of_the_change) > 300
                else result.summary_of_the_change,
            },
            metadata={
                "sections_count": len(result.sections_changed),
                "topics_count": len(result.topics_touched),
            },
        )

        return result
