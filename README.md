# LegalMove — Agente Autónomo de Comparación de Contratos

Sistema multi-agente que procesa imágenes escaneadas de contratos usando GPT-4o Vision y
dos agentes especializados con LangChain para identificar, clasificar y resumir cambios legales.
El resultado es un JSON validado por Pydantic con trazabilidad completa en Langfuse.

---

## Arquitectura

```
python -m src.main --original <img> --amendment <img>
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  contract-analysis  (span raíz @observe)                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  parse_contract_image  (span @observe)          │    │
│  │  GPT-4o Vision + codificación base64            │    │
│  │  Input: original.png  → Output: texto completo  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  parse_contract_image  (span @observe)          │    │
│  │  GPT-4o Vision + codificación base64            │    │
│  │  Input: amendment.png → Output: texto completo  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  contextualization_agent  (span @observe)       │    │
│  │  LangChain LCEL: PromptTemplate | ChatOpenAI    │    │
│  │  Rol: "Analista Senior de Contratos"            │    │
│  │  Input: ambos textos → Output: mapa contextual  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  extraction_agent  (span @observe)              │    │
│  │  LangChain + with_structured_output(Pydantic)   │    │
│  │  Rol: "Auditor Legal de Cambios"                │    │
│  │  Input: mapa + ambos textos                     │    │
│  │  Output: ContractChangeOutput (JSON validado)   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
          │
          ▼
{
  "sections_changed": ["..."],
  "topics_touched": ["..."],
  "summary_of_the_change": "..."
}
```

---

## Estructura del proyecto

```
M4-Final/
├── src/
│   ├── main.py                          # Entry point + pipeline raíz (@observe)
│   ├── image_parser.py                  # parse_contract_image() — GPT-4o Vision
│   ├── models.py                        # ContractChangeOutput (Pydantic)
│   ├── config.py                        # Validación de variables de entorno
│   └── agents/
│       ├── contextualization_agent.py   # Agente 1: mapeo estructural
│       └── extraction_agent.py          # Agente 2: extracción de cambios + validación
├── data/
│   └── test_contracts/
│       ├── pair_1_simple/               # Contrato SaaS (3 cambios simples)
│       ├── pair_2_complex/              # Licencia de Software (4 modificaciones + 1 adición)
│       ├── pair_3_consulting/           # Contrato de Consultoría (par bonus)
│       └── README.md                    # Descripción de cada par de prueba
├── scripts/
│   └── prepare_test_images.py           # Conversor PDF → PNG (configuración inicial)
├── additional-resources/                # PDFs originales provistos con el proyecto
├── requirements.txt
└── .env.example
```

---

## Instalación

### Requisitos previos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip
- API key de OpenAI con acceso a GPT-4o
- Cuenta en [Langfuse](https://cloud.langfuse.com) (el plan gratuito funciona)

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd M4-Final
```

### 2. Crear y activar el entorno virtual

```bash
uv venv .venv --python 3.12
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Instalar dependencias

```bash
uv pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

```bash
cp .env.example .env
# Editá .env y completá tus claves:
#   OPENAI_API_KEY=sk-...
#   LANGFUSE_PUBLIC_KEY=pk-lf-...
#   LANGFUSE_SECRET_KEY=sk-lf-...
#   LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Uso

```bash
# Par 1 — Cambios simples (contrato SaaS)
python -m src.main \
  --original  data/test_contracts/pair_1_simple/original.png \
  --amendment data/test_contracts/pair_1_simple/amendment.png

# Par 2 — Cambios complejos (Licencia de Software)
python -m src.main \
  --original  data/test_contracts/pair_2_complex/original.png \
  --amendment data/test_contracts/pair_2_complex/amendment.png

# Guardar resultado en un archivo
python -m src.main \
  --original  data/test_contracts/pair_2_complex/original.png \
  --amendment data/test_contracts/pair_2_complex/amendment.png \
  --output    results/par2_resultado.json
```

### Salida esperada

```json
{
  "sections_changed": [
    "Cláusula 2 - Plazo",
    "Cláusula 3 - Pago",
    "Cláusula 4 - Soporte",
    "Cláusula 5 - Terminación",
    "Cláusula 7 - Protección de Datos"
  ],
  "topics_touched": [
    "Plazos y Vigencia",
    "Pagos y Montos",
    "Soporte Técnico",
    "Terminación del Contrato",
    "Protección de Datos"
  ],
  "summary_of_the_change": "La enmienda introduce los siguientes cambios: ..."
}
```

---

## Decisiones técnicas

### ¿Por qué GPT-4o para Vision?

GPT-4o entiende de forma nativa el layout de documentos, la numeración jerárquica y el
formato legal directamente desde una imagen, sin necesidad de pre-procesamiento con OCR.
El parámetro `detail: "high"` instruye al modelo a analizar la imagen en alta resolución,
preservando los números de cláusulas y la estructura jerárquica que las herramientas OCR
tradicionales aplanarían.

### ¿Por qué dos agentes en lugar de uno?

Un agente monolítico que hace tanto la contextualización como la extracción produce
significativamente más alucinaciones, ya que conflúa dos tareas cognitivamente distintas.
El diseño de dos agentes refleja cómo funciona la revisión legal en la práctica:

1. **ContextualizationAgent** (Analista Senior) construye un mapa estructural de ambos
   documentos — qué secciones existen, cómo se corresponden y cuál es el propósito de
   cada bloque. *No extrae cambios*. Este mapa actúa como un "scratchpad" compartido
   que ancla al segundo agente.

2. **ExtractionAgent** (Auditor Legal) recibe ambos textos *más* el mapa contextual.
   Con la estructura ya resuelta, puede enfocarse exclusivamente en identificar,
   clasificar (ADICIÓN / ELIMINACIÓN / MODIFICACIÓN) y describir cada cambio con
   precisión legal.

Esta separación también facilita el debugging: si el output es incorrecto, se puede
inspeccionar el mapa contextual en Langfuse para determinar si el error es estructural
(Agente 1) o analítico (Agente 2).

### ¿Por qué `with_structured_output` para la validación?

`ChatOpenAI.with_structured_output(ContractChangeOutput)` usa el mecanismo nativo de
function calling / JSON schema de OpenAI, lo que significa que el modelo queda
*restringido a nivel de generación* para producir un output que cumpla el esquema Pydantic.
Esto es más confiable que parsear un string libre con regex o pedirle al modelo que
"devuelva JSON" — esto último produce JSON inválido aproximadamente el 15% de las veces
en documentos largos.

### Patrón de trazabilidad con el decorador `@observe` de Langfuse

Cada función del pipeline está decorada con `@observe(name=...)`. Cuando `run_pipeline()`
llama a las funciones hijas, Langfuse construye automáticamente la jerarquía
padre-hijo de spans sin necesidad de gestión manual. Esto mantiene la lógica de negocio
limpia mientras captura inputs, outputs, latencia y metadata en cada etapa.

---

## Estructura de trazas en Langfuse

El dashboard muestra una traza por ejecución del pipeline:

```
contract-analysis  (traza raíz)
├── parse_contract_image   [original]  → cantidad de chars, latencia, tokens
├── parse_contract_image   [amendment] → cantidad de chars, latencia, tokens
├── contextualization_agent            → preview del mapa contextual, latencia
└── extraction_agent                   → cantidad de secciones/temas, JSON de salida
```

Para ver las trazas: ingresar a [cloud.langfuse.com](https://cloud.langfuse.com),
abrir el proyecto y navegar a **Traces**.

---

## Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `langchain-openai` | 0.3.35 | Integración LangChain + OpenAI |
| `langchain-core` | 0.3.86 | Chains LCEL, prompt templates |
| `openai` | 1.109.1 | SDK de OpenAI (Vision, structured outputs) |
| `pydantic` | 2.13.4 | Validación del esquema de salida |
| `langfuse` | 2.60.10 | Observabilidad y trazabilidad |
| `python-dotenv` | 1.2.2 | Gestión segura de variables de entorno |
| `pdf2image` | 1.17.0 | Conversión PDF → PNG (solo configuración inicial) |
| `Pillow` | 12.2.0 | Procesamiento de imágenes |
| `tenacity` | 9.1.4 | Lógica de reintentos para errores de API |
