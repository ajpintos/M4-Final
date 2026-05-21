from typing import List
from pydantic import BaseModel, Field


class ContractChangeOutput(BaseModel):
    sections_changed: List[str] = Field(
        ...,
        description=(
            "Identificadores exactos de las secciones modificadas por la enmienda "
            "(ej: ['Cláusula 3.2 - Monto Mensual', 'Artículo 7 - Vigencia'])."
        ),
    )
    topics_touched: List[str] = Field(
        ...,
        description=(
            "Categorías legales o comerciales afectadas por los cambios "
            "(ej: ['Pagos y Montos', 'Plazos', 'Territorio', 'Confidencialidad'])."
        ),
    )
    summary_of_the_change: str = Field(
        ...,
        description=(
            "Descripción detallada y precisa de cada cambio introducido por la enmienda: "
            "adiciones (nuevo texto), eliminaciones (texto removido) y modificaciones "
            "(texto anterior → texto nuevo). Apta para revisión de compliance legal."
        ),
    )
