"""LegalMove — Autonomous Contract Amendment Comparison Agent.

Entry point that accepts two image paths and runs the full pipeline:
    1. Parse original contract (GPT-4o Vision)
    2. Parse amendment (GPT-4o Vision)
    3. ContextualizationAgent — structural mapping
    4. ExtractionAgent       — change extraction + Pydantic validation

Usage:
    python -m src.main --original data/test_contracts/pair_1_simple/original.png \
                       --amendment data/test_contracts/pair_1_simple/amendment.png
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from langfuse.decorators import langfuse_context, observe

load_dotenv()

from src.config import validate_config
from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent


@observe(name="contract-analysis")
def run_pipeline(original_path: str, amendment_path: str) -> dict:
    """Full pipeline: image parsing → contextualization → change extraction.

    Args:
        original_path: Path to the original contract image (PNG/JPG).
        amendment_path: Path to the amendment image (PNG/JPG).

    Returns:
        Dictionary matching ContractChangeOutput schema.
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

    # ── Step 1: Parse original contract ─────────────────────────────────────
    print("[1/4] Parsing original contract image...", flush=True)
    original_text = parse_contract_image(original_path, document_label="original")
    print(f"      Extracted {len(original_text):,} characters.", flush=True)

    # ── Step 2: Parse amendment ──────────────────────────────────────────────
    print("[2/4] Parsing amendment image...", flush=True)
    amendment_text = parse_contract_image(amendment_path, document_label="amendment")
    print(f"      Extracted {len(amendment_text):,} characters.", flush=True)

    # ── Step 3: Contextualization ────────────────────────────────────────────
    print("[3/4] Running ContextualizationAgent...", flush=True)
    context_map = ContextualizationAgent().run(original_text, amendment_text)
    print(f"      Context map: {len(context_map):,} characters.", flush=True)

    # ── Step 4: Change extraction + Pydantic validation ─────────────────────
    print("[4/4] Running ExtractionAgent...", flush=True)
    result = ExtractionAgent().run(context_map, original_text, amendment_text)
    print(
        f"      Found {len(result.sections_changed)} section(s) changed, "
        f"{len(result.topics_touched)} topic(s) touched.",
        flush=True,
    )

    langfuse_context.flush()
    return result.model_dump()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LegalMove — Contract Amendment Comparison Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m src.main \\\n"
            "    --original data/test_contracts/pair_1_simple/original.png \\\n"
            "    --amendment data/test_contracts/pair_1_simple/amendment.png\n\n"
            "  python -m src.main \\\n"
            "    --original contracts/original.jpg \\\n"
            "    --amendment contracts/amendment.jpg \\\n"
            "    --output results/output.json"
        ),
    )
    parser.add_argument(
        "--original",
        required=True,
        metavar="PATH",
        help="Path to the original contract image (PNG or JPG).",
    )
    parser.add_argument(
        "--amendment",
        required=True,
        metavar="PATH",
        help="Path to the amendment / addendum image (PNG or JPG).",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Optional path to save the JSON output (e.g. results/output.json).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        validate_config()
    except EnvironmentError as exc:
        print(f"\n[CONFIG ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    print("\nLegalMove — Contract Amendment Comparison Agent")
    print("=" * 52)
    print(f"Original : {args.original}")
    print(f"Amendment: {args.amendment}")
    print("=" * 52)

    try:
        result = run_pipeline(args.original, args.amendment)
    except FileNotFoundError as exc:
        print(f"\n[FILE ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"\n[VALIDATION ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"\n[PIPELINE ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    print("\n" + "=" * 52)
    print("CONTRACT CHANGE ANALYSIS — RESULT")
    print("=" * 52)
    print(output_json)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_json, encoding="utf-8")
        print(f"\n[OK] Result saved to: {args.output}")


if __name__ == "__main__":
    main()
