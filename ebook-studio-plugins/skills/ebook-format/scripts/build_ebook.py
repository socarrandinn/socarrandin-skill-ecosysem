import json, os, pathlib, subprocess, shutil, sys, tempfile

def ensure_pandoc():
    if shutil.which("pandoc"):
        return
    try:
        r = subprocess.run(["winget", "install", "--id", "JohnMacFarlane.Pandoc", "--accept-source-agreements", "--accept-package-agreements"])
    except FileNotFoundError:
        print("PANDOC_MANUAL: instala con: winget install JohnMacFarlane.Pandoc", file=sys.stderr)
        raise SystemExit(1)
    if r.returncode != 0:
        print("PANDOC_MANUAL: instala con: winget install JohnMacFarlane.Pandoc", file=sys.stderr)
        raise SystemExit(1)

def find_engine():
    for exe in ("msedge", "chrome"):
        p = shutil.which(exe)
        if p: return p
    edge = pathlib.Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    chrome = pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    for c in (edge, chrome):
        if c.exists(): return str(c)
    return None

def main():
    state = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    d = pathlib.Path(state["dir"]); out = d / "out"; out.mkdir(exist_ok=True)
    md = d / "manuscrito.md"; ensure_pandoc()
    meta = ["--metadata", f"title={state.get('titulo','Libro')}", "--metadata", f"lang={state['idioma']}", "--toc", "--toc-depth=2"]
    subprocess.run(["pandoc", str(md), "-o", str(out/"libro.epub"), *meta], check=True)
    html = out / "libro.html"
    subprocess.run(["pandoc", str(md), "-o", str(html), "--standalone", *meta], check=True)
    engine = find_engine()
    if engine:
        profile_dir = pathlib.Path(tempfile.gettempdir()) / f"edge-pdf-{os.getpid()}"
        r = subprocess.run([engine, "--headless", "--disable-gpu", "--print-to-pdf-no-header", f"--user-data-dir={profile_dir}", f"--print-to-pdf={out/'libro.pdf'}", str(html.as_uri())])
        shutil.rmtree(profile_dir, ignore_errors=True)
        if r.returncode != 0:
            print("PDF_WARN: PDF falló, EPUB + HTML OK", file=sys.stderr)
    else:
        print("NO_ENGINE: sin Edge/Chrome; entrega EPUB + HTML", file=sys.stderr)
    print("OK:", out)

if __name__ == "__main__":
    main()