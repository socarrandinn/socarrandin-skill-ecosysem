import sys, json, pathlib
try:
    import pdfplumber
except ImportError:
    import subprocess; subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber"], check=True)
    import pdfplumber

def extract(path: pathlib.Path, out_dir: pathlib.Path) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    md_path = out_dir / (stem + ".md")
    n = 1
    while md_path.exists():
        n += 1
        md_path = out_dir / f"{stem}_{n}.md"
    lines = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            txt = page.extract_text() or ""
            if txt.strip():
                lines.append(f"<!-- pagina {i+1} -->\n{txt}")
    md_path.write_text("\n\n".join(lines), encoding="utf-8")
    return str(md_path)

if __name__ == "__main__":
    state = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(state["dir"]) / "extraido"
    for src in state.get("fuentes", []):
        p = pathlib.Path(src)
        if not p.is_absolute():
            p = pathlib.Path(state["dir"]) / src
        if p.exists():
            print(extract(p, out))
        else:
            print(f"FALTA: {src}", file=sys.stderr)
