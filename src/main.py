"""LegalMove — Agente Autónomo de Comparación de Contratos.

Entry point que acepta dos rutas de imágenes y ejecuta el pipeline completo:
    1. Parseo del contrato original (GPT-4o Vision)
    2. Parseo de la enmienda (GPT-4o Vision)
    3. ContextualizationAgent — mapeo estructural
    4. ExtractionAgent       — extracción de cambios + validación Pydantic

Uso:
    python -m src.main --original data/test_contracts/pair_1_simple/original.png \
                       --amendment data/test_contracts/pair_1_simple/amendment.png
"""

import argparse
import json
import sys
from pathlib import Path

from rich import print_json

from dotenv import load_dotenv
from langfuse.decorators import langfuse_context, observe

load_dotenv()

from src.config import validate_config
from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent


@observe(name="contract-analysis")
def run_pipeline(original_path: str, amendment_path: str) -> dict:
    """Pipeline completo: parseo de imágenes → contextualización → extracción de cambios.

    Args:
        original_path: Ruta a la imagen del contrato original (PNG/JPG).
        amendment_path: Ruta a la imagen de la enmienda (PNG/JPG).

    Returns:
        Diccionario que cumple el esquema ContractChangeOutput.
    """
    langfuse_context.update_current_trace(
        name="contract-analysis",
        metadata={
            "original_file": Path(original_path).name,
            "amendment_file": Path(amendment_path).name,
            "pipeline_version": "1.0.0",
        },
        tags=["legalmove", "contract-comparison", "production"],
    )

    # ── Paso 1: Parseo del contrato original ────────────────────────────────
    print("[1/4] Parseando imagen del contrato original...", flush=True)
    original_text = parse_contract_image(original_path, document_label="original")
    print(f"      {len(original_text):,} caracteres extraídos.", flush=True)

    # ── Paso 2: Parseo de la enmienda ────────────────────────────────────────
    print("[2/4] Parseando imagen de la enmienda...", flush=True)
    amendment_text = parse_contract_image(amendment_path, document_label="amendment")
    print(f"      {len(amendment_text):,} caracteres extraídos.", flush=True)

    # ── Paso 3: Contextualización ────────────────────────────────────────────
    print("[3/4] Ejecutando ContextualizationAgent...", flush=True)
    context_map = ContextualizationAgent().run(original_text, amendment_text)
    print(f"      Mapa contextual: {len(context_map):,} caracteres.", flush=True)

    # ── Paso 4: Extracción de cambios + validación Pydantic ──────────────────
    print("[4/4] Ejecutando ExtractionAgent...", flush=True)
    result = ExtractionAgent().run(context_map, original_text, amendment_text)
    print(
        f"      {len(result.sections_changed)} sección(es) modificada(s), "
        f"{len(result.topics_touched)} tema(s) afectado(s).",
        flush=True,
    )

    langfuse_context.flush()
    return result.model_dump()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LegalMove — Agente de Comparación de Enmiendas Contractuales",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python -m src.main \\\n"
            "    --original data/test_contracts/pair_1_simple/original.png \\\n"
            "    --amendment data/test_contracts/pair_1_simple/amendment.png\n\n"
            "  python -m src.main \\\n"
            "    --original contratos/original.jpg \\\n"
            "    --amendment contratos/enmienda.jpg \\\n"
            "    --output resultados/output.json"
        ),
    )
    parser.add_argument(
        "--original",
        required=True,
        metavar="RUTA",
        help="Ruta a la imagen del contrato original (PNG o JPG).",
    )
    parser.add_argument(
        "--amendment",
        required=True,
        metavar="RUTA",
        help="Ruta a la imagen de la enmienda / adenda (PNG o JPG).",
    )
    parser.add_argument(
        "--output",
        metavar="RUTA",
        help="Ruta opcional para guardar el JSON de salida (ej: resultados/output.json).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        validate_config()
    except EnvironmentError as exc:
        print(f"\n[ERROR DE CONFIGURACIÓN] {exc}", file=sys.stderr)
        sys.exit(1)

    print("\nLegalMove — Agente de Comparación de Enmiendas Contractuales")
    print("=" * 60)
    print(f"Original : {args.original}")
    print(f"Enmienda : {args.amendment}")
    print("=" * 60)

    try:
        result = run_pipeline(args.original, args.amendment)
    except FileNotFoundError as exc:
        print(f"\n[ERROR DE ARCHIVO] {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"\n[ERROR DE VALIDACIÓN] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n[ERROR DEL PIPELINE] {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("ANÁLISIS DE CAMBIOS CONTRACTUALES — RESULTADO")
    print("=" * 60)
    print_json(output_json)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_json, encoding="utf-8")
        print(f"\n[OK] Resultado guardado en: {args.output}")


if __name__ == "__main__":
    main()
