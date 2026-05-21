# LegalMove — Autonomous Contract Amendment Comparison Agent

A multi-agent system that processes scanned contract images using GPT-4o Vision and
two specialized LangChain agents to identify, classify, and summarize legal changes.
Output is a Pydantic-validated JSON with full Langfuse traceability.

---

## Architecture

```
python -m src.main --original <img> --amendment <img>
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  contract-analysis  (@observe root span)                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  parse_contract_image  (@observe span)          │    │
│  │  GPT-4o Vision + base64 encoding                │    │
│  │  Input: original.png  → Output: full text       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  parse_contract_image  (@observe span)          │    │
│  │  GPT-4o Vision + base64 encoding                │    │
│  │  Input: amendment.png → Output: full text       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  contextualization_agent  (@observe span)       │    │
│  │  LangChain LCEL: PromptTemplate | ChatOpenAI    │    │
│  │  Role: "Senior Legal Contract Analyst"          │    │
│  │  Input: both texts → Output: context map (md)  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  extraction_agent  (@observe span)              │    │
│  │  LangChain + with_structured_output(Pydantic)   │    │
│  │  Role: "Legal Change Auditor"                   │    │
│  │  Input: context + both texts                    │    │
│  │  Output: ContractChangeOutput (validated JSON)  │    │
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

## Project Structure

```
M4-Final/
├── src/
│   ├── main.py                          # Entry point + root @observe pipeline
│   ├── image_parser.py                  # parse_contract_image() — GPT-4o Vision
│   ├── models.py                        # ContractChangeOutput (Pydantic)
│   ├── config.py                        # Env var validation
│   └── agents/
│       ├── contextualization_agent.py   # Agent 1: structural mapping
│       └── extraction_agent.py          # Agent 2: change extraction + validation
├── data/
│   └── test_contracts/
│       ├── pair_1_simple/               # SaaS contract (3 simple changes)
│       ├── pair_2_complex/              # Software license (4 modifications + 1 addition)
│       ├── pair_3_consulting/           # Consulting contract (bonus pair)
│       └── README.md                    # Description of each test pair
├── scripts/
│   └── prepare_test_images.py           # PDF → PNG converter (one-off setup)
├── additional-resources/                # Original PDFs provided with the project
├── requirements.txt
└── .env.example
```

---

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key with GPT-4o access
- [Langfuse](https://cloud.langfuse.com) account (free tier works)

### 1. Clone the repository

```bash
git clone <repository-url>
cd M4-Final
```

### 2. Create and activate the virtual environment

```bash
uv venv .venv --python 3.12
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your keys:
#   OPENAI_API_KEY=sk-...
#   LANGFUSE_PUBLIC_KEY=pk-lf-...
#   LANGFUSE_SECRET_KEY=sk-lf-...
#   LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Usage

```bash
# Pair 1 — Simple changes (SaaS contract)
python -m src.main \
  --original  data/test_contracts/pair_1_simple/original.png \
  --amendment data/test_contracts/pair_1_simple/amendment.png

# Pair 2 — Complex changes (Software License)
python -m src.main \
  --original  data/test_contracts/pair_2_complex/original.png \
  --amendment data/test_contracts/pair_2_complex/amendment.png

# Save output to a file
python -m src.main \
  --original  data/test_contracts/pair_2_complex/original.png \
  --amendment data/test_contracts/pair_2_complex/amendment.png \
  --output    results/pair2_output.json
```

### Expected output

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

## Technical Decisions

### Why GPT-4o for Vision?

GPT-4o natively understands document layout, hierarchical numbering, and legal
formatting from a raw image — no OCR pre-processing required. The `detail: "high"`
parameter instructs the model to analyze the full image resolution, preserving
clause numbers and sub-clause structure that cheaper OCR tools would flatten.

### Why two agents instead of one?

A monolithic agent that does both contextualization and extraction produces
significantly more hallucinations, because it conflates two cognitively distinct
tasks. The two-agent design mirrors how legal review actually works:

1. **ContextualizationAgent** (Analista Senior) builds a structural map of both
   documents — which sections exist, how they correspond, and the general purpose
   of each block. It does *not* extract changes. This map acts as a shared
   "scratchpad" that grounds the second agent.

2. **ExtractionAgent** (Auditor Legal) receives both texts *plus* the context map.
   With the structure already resolved, it can focus exclusively on identifying,
   classifying (ADDITION / DELETION / MODIFICATION), and describing each change
   with legal precision.

This separation also makes debugging easier: if the output is wrong, you can
inspect the context map in Langfuse to determine whether the error is structural
(Agent 1) or analytical (Agent 2).

### Why `with_structured_output` for validation?

`ChatOpenAI.with_structured_output(ContractChangeOutput)` uses OpenAI's native
function-calling / JSON schema enforcement, which means the model is constrained
at the *generation* level to produce output that matches the Pydantic schema.
This is more reliable than parsing a free-form string with a regex or asking the
model to "return JSON" — the latter produces invalid JSON ~15% of the time in
practice on long documents.

### Langfuse `@observe` decorator pattern

Each function in the pipeline is decorated with `@observe(name=...)`. When
`run_pipeline()` calls the child functions, Langfuse automatically builds the
parent-child span hierarchy without any manual span management. This keeps the
business logic clean while still capturing inputs, outputs, latency, and metadata
at every stage.

---

## Langfuse Trace Structure

The dashboard shows one trace per pipeline execution:

```
contract-analysis  (root trace)
├── parse_contract_image   [original]  → char count, latency, tokens
├── parse_contract_image   [amendment] → char count, latency, tokens
├── contextualization_agent            → context map preview, latency
└── extraction_agent                   → sections/topics count, output JSON
```

To view traces: log in to [cloud.langfuse.com](https://cloud.langfuse.com),
open your project, and navigate to **Traces**.

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `langchain-openai` | ≥0.3.0 | LangChain + OpenAI integration |
| `langchain-core` | ≥0.3.0 | LCEL chains, prompt templates |
| `openai` | ≥1.50.0 | OpenAI SDK (Vision, structured outputs) |
| `pydantic` | ≥2.7.0 | Output schema validation |
| `langfuse` | ≥2.60.0 | Observability and tracing |
| `python-dotenv` | ≥1.0.0 | Secure env var management |
| `pdf2image` | ≥1.17.0 | PDF → PNG conversion (setup only) |
| `Pillow` | ≥10.0.0 | Image handling |
| `tenacity` | ≥8.3.0 | Retry logic for API errors |
