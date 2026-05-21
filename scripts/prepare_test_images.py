"""Convert PDF test contracts to PNG images for the pipeline.

Usage:
    python scripts/prepare_test_images.py

Requires:
    pip install pdf2image
    sudo apt-get install poppler-utils  (Linux)
    brew install poppler                (macOS)
"""

import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    print("ERROR: pdf2image is not installed.")
    print("Run: pip install pdf2image")
    print("Also ensure poppler is installed: sudo apt-get install poppler-utils")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / "additional-resources"
OUTPUT_BASE = BASE_DIR / "data" / "test_contracts"


def convert_pdf_to_images(pdf_path: Path, output_dir: Path, prefix: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nConverting: {pdf_path.name} → {output_dir.relative_to(BASE_DIR)}/")

    try:
        pages = convert_from_path(str(pdf_path), dpi=200)
    except Exception as e:
        print(f"  ERROR: Could not convert {pdf_path.name}: {e}")
        return []

    saved = []
    for i, page in enumerate(pages):
        out_path = output_dir / f"{prefix}_page_{i + 1:02d}.png"
        page.save(str(out_path), "PNG")
        saved.append(out_path)
        print(f"  Saved page {i + 1}: {out_path.name}")

    return saved


def main():
    pdfs = sorted(RESOURCES_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in: {RESOURCES_DIR}")
        sys.exit(1)

    print(f"Found {len(pdfs)} PDF(s) in {RESOURCES_DIR.relative_to(BASE_DIR)}/")

    all_images: dict[str, list[Path]] = {}
    for pdf in pdfs:
        out_dir = OUTPUT_BASE / "source_pages" / pdf.stem.replace(" ", "_")
        images = convert_pdf_to_images(pdf, out_dir, prefix="page")
        all_images[pdf.stem] = images

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("Review the generated images and copy them to:")
    print()
    print("  data/test_contracts/pair_1_simple/")
    print("    original.png   ← contrato de servicios original")
    print("    amendment.png  ← enmienda con cambio de monto y fecha")
    print()
    print("  data/test_contracts/pair_2_complex/")
    print("    original.png   ← contrato de confidencialidad (NDA) original")
    print("    amendment.png  ← enmienda con múltiples cambios")
    print()
    print("Images generated:")
    for name, imgs in all_images.items():
        print(f"  [{name}]")
        for img in imgs:
            print(f"    {img.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
