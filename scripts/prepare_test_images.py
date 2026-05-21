"""Convierte los PDFs de contratos de prueba a imágenes PNG para usar en el pipeline.

Uso:
    python scripts/prepare_test_images.py

Requisitos:
    pip install pdf2image
    sudo apt-get install poppler-utils  (Linux)
    brew install poppler                (macOS)
"""

import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
except ImportError:
    print("ERROR: pdf2image no está instalado.")
    print("Ejecutá: pip install pdf2image")
    print("También asegurate de tener poppler instalado: sudo apt-get install poppler-utils")
    sys.exit(1)

BASE_DIR = Path(__file__).parent.parent
RESOURCES_DIR = BASE_DIR / "additional-resources"
OUTPUT_BASE = BASE_DIR / "data" / "test_contracts"


def convert_pdf_to_images(pdf_path: Path, output_dir: Path, prefix: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nConvirtiendo: {pdf_path.name} → {output_dir.relative_to(BASE_DIR)}/")

    try:
        pages = convert_from_path(str(pdf_path), dpi=200)
    except Exception as e:
        print(f"  ERROR: No se pudo convertir {pdf_path.name}: {e}")
        return []

    saved = []
    for i, page in enumerate(pages):
        out_path = output_dir / f"{prefix}_page_{i + 1:02d}.png"
        page.save(str(out_path), "PNG")
        saved.append(out_path)
        print(f"  Página {i + 1} guardada: {out_path.name}")

    return saved


def main():
    pdfs = sorted(RESOURCES_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No se encontraron archivos PDF en: {RESOURCES_DIR}")
        sys.exit(1)

    print(f"Se encontraron {len(pdfs)} PDF(s) en {RESOURCES_DIR.relative_to(BASE_DIR)}/")

    all_images: dict[str, list[Path]] = {}
    for pdf in pdfs:
        out_dir = OUTPUT_BASE / "source_pages" / pdf.stem.replace(" ", "_")
        images = convert_pdf_to_images(pdf, out_dir, prefix="page")
        all_images[pdf.stem] = images

    print("\n" + "=" * 60)
    print("PRÓXIMOS PASOS:")
    print("=" * 60)
    print("Revisá las imágenes generadas y copialas a:")
    print()
    print("  data/test_contracts/pair_1_simple/")
    print("    original.png   ← contrato de servicios original")
    print("    amendment.png  ← enmienda con cambio de monto y fecha")
    print()
    print("  data/test_contracts/pair_2_complex/")
    print("    original.png   ← contrato de confidencialidad (NDA) original")
    print("    amendment.png  ← enmienda con múltiples cambios")
    print()
    print("Imágenes generadas:")
    for name, imgs in all_images.items():
        print(f"  [{name}]")
        for img in imgs:
            print(f"    {img.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
