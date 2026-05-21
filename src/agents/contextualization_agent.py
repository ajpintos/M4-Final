from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe, langfuse_context

SYSTEM_PROMPT = """\
Eres un Analista Senior de Contratos Legales con 20 años de experiencia en derecho corporativo \
y revisión de enmiendas contractuales.

Tu única responsabilidad en este flujo de trabajo es CONTEXTUALIZAR y MAPEAR la estructura \
comparada de dos documentos: un contrato original y su enmienda (adenda).

**NO debes extraer ni describir cambios específicos en este paso.**

Tu tarea consiste en:
1. Identificar las secciones y cláusulas principales de cada documento (título + numeración).
2. Establecer la correspondencia entre secciones del original y la enmienda (cuál modifica cuál).
3. Describir brevemente el propósito legal de cada bloque principal.
4. Señalar si la enmienda introduce secciones completamente nuevas o elimina secciones enteras.
5. Indicar el tipo de contrato (servicios, confidencialidad, compraventa, etc.) y el marco \
legal general aplicable.

El output de tu análisis será utilizado por un Auditor Legal especializado para extraer \
los cambios precisos. Por eso, tu mapa debe ser claro, estructurado y sin ambigüedades.

Responde en formato Markdown estructurado.\
"""

HUMAN_TEMPLATE = """\
A continuación tienes el texto extraído de dos documentos legales:

## CONTRATO ORIGINAL:
{original_text}

---

## ENMIENDA / ADENDA:
{amendment_text}

---

Genera el mapa contextual y estructural comparado de ambos documentos.\
"""


class ContextualizationAgent:
    """Agente 1: Mapea el contexto estructural de ambos documentos antes de extraer cambios."""

    def __init__(self, model: str = "gpt-4o") -> None:
        llm = ChatOpenAI(model=model, temperature=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_TEMPLATE),
        ])
        self._chain = prompt | llm

    @observe(name="contextualization_agent")
    def run(self, original_text: str, amendment_text: str) -> str:
        """Produce un mapa contextual estructural a partir de los textos de ambos documentos.

        Args:
            original_text: Texto completo extraído del contrato original.
            amendment_text: Texto completo extraído de la enmienda.

        Returns:
            Mapa contextual en formato Markdown con la estructura y correspondencia de secciones.
        """
        langfuse_context.update_current_observation(
            input={
                "original_char_count": len(original_text),
                "amendment_char_count": len(amendment_text),
            },
            metadata={"model": "gpt-4o", "role": "contextualization"},
        )

        response = self._chain.invoke({
            "original_text": original_text,
            "amendment_text": amendment_text,
        })

        context_map: str = response.content

        langfuse_context.update_current_observation(
            output=context_map[:800] + "..." if len(context_map) > 800 else context_map,
            metadata={"context_map_char_count": len(context_map)},
        )

        return context_map
