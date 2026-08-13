#!/usr/bin/env python3
"""Extrae texto de PDFs fuente a markdown (pdfplumber) para reescribir contenido.

Uso: python extract_pdf.py <state.json>

Dependencias: pdfplumber (auto-instala desde requirements.txt si falta).
"""
import json
import pathlib
import subprocess
import sys

MSG = {
    "es": {
        "no_state": "ERROR: falta ruta a state.json. Uso: python extract_pdf.py <state.json>",
        "bad_json": "ERROR: state.json inválido: {e}",
        "no_dir": "ERROR: state.json no tiene clave 'dir' (carpeta del libro)",
        "no_pdfplumber": "ERROR: no se pudo instalar pdfplumber. Ejecutar: pip install -r requirements.txt",
        "corrupt": "ERROR: PDF ilegible o corrupto: {p} ({e})",
        "scanned": "WARN_SCANNED: {p} parece PDF escaneado (0 páginas con texto). Se omite: no hay texto que extraer.",
        "extracted": "EXTRACTED: {p}",
        "missing": "FALTA: {p}",
    },
    "en": {
        "no_state": "ERROR: missing state.json path. Usage: python extract_pdf.py <state.json>",
        "bad_json": "ERROR: invalid state.json: {e}",
        "no_dir": "ERROR: state.json missing 'dir' key (book folder)",
        "no_pdfplumber": "ERROR: could not install pdfplumber. Run: pip install -r requirements.txt",
        "corrupt": "ERROR: unreadable or corrupt PDF: {p} ({e})",
        "scanned": "WARN_SCANNED: {p} looks like a scanned PDF (0 pages with text). Skipped: no text to extract.",
        "extracted": "EXTRACTED: {p}",
        "missing": "MISSING: {p}",
    },
}


def ensure_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber
    except ImportError:
        req = pathlib.Path(__file__).resolve().parent / "requirements.txt"
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(req)],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass
        try:
            import pdfplumber
            return pdfplumber
        except ImportError:
            return None


def extract(pdfplumber, path: pathlib.Path, out_dir: pathlib.Path) -> tuple:
    """Extrae texto de un PDF. Devuelve (estado, ruta_md)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    md_path = out_dir / (stem + ".md")
    n = 1
    while md_path.exists():
        n += 1
        md_path = out_dir / f"{stem}_{n}.md"
    lines = []
    total = 0
    with_text = 0
    with pdfplumber.open(path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text() or ""
            if txt.strip():
                with_text += 1
                lines.append(f"<!-- pagina {i+1} -->\n{txt}")
    if total and not with_text:
        return "scanned", None
    md_path.write_text("\n\n".join(lines), encoding="utf-8")
    return "extracted", md_path


def main():
    if len(sys.argv) < 2:
        print(MSG["es"]["no_state"], file=sys.stderr)
        return 1
    try:
        state = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(MSG["es"]["bad_json"].format(e=e), file=sys.stderr)
        return 2
    idioma = state.get("idioma", "es")
    msg = MSG.get(idioma, MSG["es"])
    d = state.get("dir")
    if not d:
        print(msg["no_dir"], file=sys.stderr)
        return 3
    pdfplumber = ensure_pdfplumber()
    if pdfplumber is None:
        print(msg["no_pdfplumber"], file=sys.stderr)
        return 4
    out = pathlib.Path(d) / "extraido"
    fuentes = state.get("fuentes", []) or []
    if not fuentes:
        print("SIN_FUENTES: no hay fuentes en state; saltar a write", file=sys.stderr)
        return 0
    for src in fuentes:
        p = pathlib.Path(src)
        if not p.is_absolute():
            p = pathlib.Path(d) / src
        if not p.exists():
            print(msg["missing"].format(p=src), file=sys.stderr)
            continue
        try:
            estado, ruta = extract(pdfplumber, p, out)
        except Exception as e:
            print(msg["corrupt"].format(p=src, e=e), file=sys.stderr)
            continue
        if estado == "scanned":
            print(msg["scanned"].format(p=src), file=sys.stderr)
        else:
            print(msg["extracted"].format(p=ruta))
    return 0


if __name__ == "__main__":
    sys.exit(main())