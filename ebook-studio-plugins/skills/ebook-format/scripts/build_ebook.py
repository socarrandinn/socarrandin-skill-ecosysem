#!/usr/bin/env python3
"""Convierte manuscrito.md a EPUB + HTML + PDF (pandoc + motor headless).

Uso: python build_ebook.py <state.json>

Requisitos externos:
  - pandoc (auto-instala con winget/brew/apt si falta; fallback: instrucción manual)
  - motor PDF: Edge/Chrome headless, wkhtmltopdf o weasyprint (opcional)
  - epubcheck en PATH (opcional, para validación completa del EPUB)
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

MSG = {
    "es": {
        "no_state": "ERROR: falta ruta a state.json. Uso: python build_ebook.py <state.json>",
        "bad_json": "ERROR: state.json inválido: {e}",
        "no_dir": "ERROR: state.json no tiene clave 'dir' (carpeta del libro)",
        "no_idioma": "ERROR: state.json no tiene clave 'idioma'",
        "no_md": "ERROR: no existe manuscrito.md en {d}",
        "no_pandoc": "ERROR: no se pudo instalar pandoc automáticamente. Instalar a mano y reintentar: {hint}",
        "epub_ok": "EPUB_OK: {p}",
        "epub_warn": "EPUB_WARN: {p} ({reason})",
        "epubcheck_ok": "EPUBCHECK_OK: {p}",
        "epubcheck_warn": "EPUBCHECK_WARN: {p} ({err})",
        "no_engine": "NO_ENGINE: sin motor PDF (Edge/Chrome/wkhtmltopdf/weasyprint); entrega EPUB + HTML",
        "pdf_warn": "PDF_WARN: PDF falló; EPUB + HTML OK",
        "ok": "OK: {d}",
    },
    "en": {
        "no_state": "ERROR: missing state.json path. Usage: python build_ebook.py <state.json>",
        "bad_json": "ERROR: invalid state.json: {e}",
        "no_dir": "ERROR: state.json missing 'dir' key (book folder)",
        "no_idioma": "ERROR: state.json missing 'idioma' key",
        "no_md": "ERROR: manuscrito.md not found in {d}",
        "no_pandoc": "ERROR: could not install pandoc automatically. Install manually and retry: {hint}",
        "epub_ok": "EPUB_OK: {p}",
        "epub_warn": "EPUB_WARN: {p} ({reason})",
        "epubcheck_ok": "EPUBCHECK_OK: {p}",
        "epubcheck_warn": "EPUBCHECK_WARN: {p} ({err})",
        "no_engine": "NO_ENGINE: no PDF engine (Edge/Chrome/wkhtmltopdf/weasyprint); delivering EPUB + HTML",
        "pdf_warn": "PDF_WARN: PDF failed; EPUB + HTML OK",
        "ok": "OK: {d}",
    },
}

PANDOC_HINT = {
    "win32": "winget install JohnMacFarlane.Pandoc",
    "darwin": "brew install pandoc",
    "linux": "sudo apt-get install -y pandoc",
}


def ensure_pandoc():
    if shutil.which("pandoc"):
        return True
    hint = PANDOC_HINT.get(sys.platform, "instalar pandoc (https://pandoc.org/installing.html)")
    try:
        if sys.platform == "win32":
            cmd = ["winget", "install", "--id", "JohnMacFarlane.Pandoc",
                   "--accept-source-agreements", "--accept-package-agreements"]
        elif sys.platform == "darwin":
            cmd = ["brew", "install", "pandoc"]
        else:
            cmd = ["apt-get", "install", "-y", "pandoc"]
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0 and shutil.which("pandoc"):
            return True
    except (FileNotFoundError, OSError):
        pass
    return hint


CHROME_FLAGS = ["--headless", "--disable-gpu", "--no-sandbox", "--print-to-pdf-no-header"]


def find_engine():
    """Devuelve (nombre_exe, ruta, clase) donde clase determina los args."""
    candidates = []
    if sys.platform == "win32":
        candidates = [
            pathlib.Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
            / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            pathlib.Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
            / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
    elif sys.platform == "darwin":
        candidates = [
            pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            pathlib.Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
    for exe in ("msedge", "microsoft-edge", "google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(exe)
        if p:
            return exe, p, "chrome"
    for c in candidates:
        if c.exists():
            return c.name, str(c), "chrome"
    for exe in ("wkhtmltopdf", "weasyprint"):
        p = shutil.which(exe)
        if p:
            return exe, p, exe
    return None


def render_pdf(engine, out_pdf: pathlib.Path, html: pathlib.Path):
    name, exe, kind = engine
    if kind == "chrome":
        profile = pathlib.Path(tempfile.gettempdir()) / f"edge-pdf-{os.getpid()}"
        cmd = [exe, *CHROME_FLAGS,
               f"--user-data-dir={profile}",
               f"--print-to-pdf={out_pdf}",
               html.as_uri()]
        try:
            r = subprocess.run(cmd, capture_output=True)
        finally:
            shutil.rmtree(profile, ignore_errors=True)
        return r.returncode == 0 and out_pdf.exists()
    if kind == "wkhtmltopdf":
        cmd = [exe, "--enable-local-file-access", str(html), str(out_pdf)]
    else:  # weasyprint
        cmd = [exe, str(html), str(out_pdf)]
    return subprocess.run(cmd, capture_output=True).returncode == 0 and out_pdf.exists()


def validate_epub(path: pathlib.Path):
    """Chequeo estructural mínimo del EPUB con stdlib. Devuelve (ok, razon)."""
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
            if not names:
                return False, "EPUB vacío"
            if "mimetype" in names:
                if not z.read("mimetype").startswith(b"application/epub"):
                    return False, "mimetype incorrecto"
            else:
                return False, "falta mimetype"
            if "META-INF/container.xml" not in names:
                return False, "falta META-INF/container.xml"
            rootfile = None
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(z.read("META-INF/container.xml"))
                for rf in root.iter():
                    if rf.tag.endswith("rootfile"):
                        rootfile = rf.get("full-path")
                        break
            except Exception:
                return False, "container.xml inválido"
            if not rootfile or rootfile not in names:
                return False, f"OPF no encontrado ({rootfile})"
            try:
                opf = ET.fromstring(z.read(rootfile))
            except Exception:
                return False, "OPF malformado"
            ns = {"o": "http://www.idpf.org/2007/opf"}
            missing = []
            base = pathlib.Path(rootfile).parent
            for item in opf.iter("{%s}item" % ns["o"]):
                href = item.get("href", "")
                if href:
                    full = (base / href).as_posix()
                    if full not in names:
                        missing.append(href)
            if missing:
                return False, f"faltan {len(missing)} archivos del manifest (ej: {missing[0]})"
            return True, "estructura OK"
    except (zipfile.BadZipFile, OSError) as e:
        return False, f"no es ZIP válido ({e})"


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
    if not state.get("idioma"):
        print(msg["no_idioma"], file=sys.stderr)
        return 3
    d = pathlib.Path(d)
    md = d / "manuscrito.md"
    if not md.exists():
        print(msg["no_md"].format(d=d), file=sys.stderr)
        return 4
    pandoc_ok = ensure_pandoc()
    if pandoc_ok is not True:
        print(msg["no_pandoc"].format(hint=pandoc_ok), file=sys.stderr)
        return 5
    out = d / "out"
    out.mkdir(parents=True, exist_ok=True)
    meta = ["--metadata", f"title={state.get('titulo', 'Libro')}",
            "--metadata", f"lang={state['idioma']}", "--toc", "--toc-depth=2"]
    try:
        epub = out / "libro.epub"
        subprocess.run(["pandoc", str(md), "-o", str(epub), *meta], check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"ERROR: pandoc EPUB falló: {e}", file=sys.stderr)
        return 6
    ok, reason = validate_epub(epub)
    print(msg["epub_ok" if ok else "epub_warn"].format(p=epub, reason=reason))
    html = out / "libro.html"
    try:
        subprocess.run(["pandoc", str(md), "-o", str(html), "--standalone", *meta],
                       check=True, capture_output=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"ERROR: pandoc HTML falló: {e}", file=sys.stderr)
        return 6
    if shutil.which("epubcheck"):
        r = subprocess.run(["epubcheck", str(epub)], capture_output=True, text=True)
        if r.returncode == 0:
            print(msg["epubcheck_ok"].format(p=epub))
        else:
            print(msg["epubcheck_warn"].format(p=epub, err=(r.stdout or r.stderr)[:200]))
    engine = find_engine()
    if engine:
        if render_pdf(engine, out / "libro.pdf", html):
            print(msg["ok"].format(d=out))
        else:
            print(msg["pdf_warn"], file=sys.stderr)
    else:
        print(msg["no_engine"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())