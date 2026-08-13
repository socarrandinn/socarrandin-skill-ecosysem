#!/usr/bin/env python3
"""Genera portada 2560x1600 PNG para ebook.

Uso: python make_cover.py <state.json> [ruta_portada.png]

Dependencias: Pillow (auto-instala desde requirements.txt si falta).
Opciones de entorno:
  EBOOK_FONT: ruta a una fuente TTF/OTF (override de la búsqueda automática).
"""
import json
import os
import pathlib
import subprocess
import sys

WIDTH, HEIGHT = 2560, 1600
MARGIN_X = 200
TITLE_MAX_WIDTH = WIDTH - 2 * MARGIN_X
TITLE_BASE_SIZE = 110
TITLE_MIN_SIZE = 60
MAX_LINES = 3

PALETTES = {
    "salud": ("#1B5E20", "#FFFFFF", "#A5D6A7"),
    "cocina": ("#BF360C", "#FFFFFF", "#FFCCBC"),
    "dinero": ("#1A237E", "#FFFFFF", "#9FA8DA"),
    "infantil": ("#4A148C", "#FFFFFF", "#CE93D8"),
    "default": ("#263238", "#FFFFFF", "#B0BEC5"),
}

PALETTE_KEYWORDS = {
    "salud": [
        "salud", "saludable", "perder peso", "dieta", "nutricion", "nutrición",
        "fitness", "ejercicio", "bienestar", "ansiedad", "sueño", "sueño",
        "meditacion", "meditación", "yoga", "longevidad", "alimentacion",
    ],
    "cocina": [
        "cocina", "cocinar", "receta", "recetas", "comida", "gastronomia",
        "reposteria", "repostería", "hornear", "pan", "chef", "sabor",
    ],
    "dinero": [
        "dinero", "finanzas", "financiera", "inversion", "inversión",
        "ahorro", "ahorrar", "negocio", "negocios", "emprender", "emprendimiento",
        "trading", "cripto", "ingresos", "pasivo",
    ],
    "infantil": [
        "infantil", "infantiles", "ninos", "niños", "kids", "children",
        "cuento", "cuentos", "bebe", "bebé",
    ],
}

MSG = {
    "es": {
        "no_state": "ERROR: falta ruta a state.json. Uso: python make_cover.py <state.json>",
        "bad_json": "ERROR: state.json inválido: {e}",
        "no_dir": "ERROR: state.json no tiene clave 'dir' (carpeta del libro)",
        "no_pillow": "ERROR: no se pudo instalar Pillow. Ejecutar: pip install -r requirements.txt",
        "cover_ok": "COVER_OK: {path}",
        "truncated": "TITLE_TRUNCATED: título demasiado largo, se truncó a 3 líneas",
    },
    "en": {
        "no_state": "ERROR: missing state.json path. Usage: python make_cover.py <state.json>",
        "bad_json": "ERROR: invalid state.json: {e}",
        "no_dir": "ERROR: state.json missing 'dir' key (book folder)",
        "no_pillow": "ERROR: could not install Pillow. Run: pip install -r requirements.txt",
        "cover_ok": "COVER_OK: {path}",
        "truncated": "TITLE_TRUNCATED: title too long, truncated to 3 lines",
    },
}


def ensure_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
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
            from PIL import Image, ImageDraw, ImageFont
            return Image, ImageDraw, ImageFont
        except ImportError:
            return None


def candidate_font_dirs():
    dirs = []
    if sys.platform == "win32":
        dirs.append(pathlib.Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts")
    elif sys.platform == "darwin":
        dirs += [
            pathlib.Path("/System/Library/Fonts"),
            pathlib.Path("/Library/Fonts"),
            pathlib.Path.home() / "Library" / "Fonts",
        ]
    else:
        dirs += [
            pathlib.Path("/usr/share/fonts/truetype/dejavu"),
            pathlib.Path("/usr/share/fonts/truetype/liberation"),
            pathlib.Path("/usr/share/fonts"),
            pathlib.Path("/usr/local/share/fonts"),
            pathlib.Path.home() / ".local" / "share" / "fonts",
        ]
    return [d for d in dirs if d.is_dir()]


FONT_CANDIDATES = [
    "arialbd.ttf",
    "DejaVuSans-Bold.ttf",
    "LiberationSans-Bold.ttf",
    "HelveticaNeue-Bold.ttf",
    "arial.ttf",
    "DejaVuSans.ttf",
    "LiberationSans-Regular.ttf",
]


def find_font(size, ImageFont):
    override = os.environ.get("EBOOK_FONT")
    if override and pathlib.Path(override).exists():
        return ImageFont.truetype(str(override), size)
    for name in FONT_CANDIDATES:
        for d in candidate_font_dirs():
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), size)
    try:
        r = subprocess.run(
            ["fc-match", "-f", "%{file}", "sans-serif:bold"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            p = pathlib.Path(r.stdout.strip())
            if p.exists():
                return ImageFont.truetype(str(p), size)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return ImageFont.load_default()


def pick_palette(nicho):
    n = (nicho or "").strip().lower()
    if not n:
        return PALETTES["default"]
    for key, keywords in PALETTE_KEYWORDS.items():
        if any(kw in n for kw in keywords):
            return PALETTES[key]
    return PALETTES["default"]


def wrap_title(text, draw, font, max_width):
    """Wrap por ancho real en píxeles. Devuelve (lineas, truncado)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        candidate = w if not cur else f"{cur} {w}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if not cur or (bbox[2] - bbox[0]) <= max_width:
            cur = candidate
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


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
    pil = ensure_pillow()
    if pil is None:
        print(msg["no_pillow"], file=sys.stderr)
        return 4
    Image, ImageDraw, ImageFont = pil
    try:
        pal = pick_palette(state.get("nicho", ""))
        img = Image.new("RGB", (WIDTH, HEIGHT), pal[0])
        draw = ImageDraw.Draw(img)
        title = state.get("titulo", "Libro")
        size = TITLE_BASE_SIZE
        lines, truncated = [], False
        while size >= TITLE_MIN_SIZE:
            f = find_font(size, ImageFont)
            lines = wrap_title(title, draw, f, TITLE_MAX_WIDTH)
            if len(lines) <= MAX_LINES:
                break
            size -= 10
        else:
            f = find_font(size, ImageFont)
            lines = wrap_title(title, draw, f, TITLE_MAX_WIDTH)
            truncated = True
        lines = lines[:MAX_LINES]
        y = 500
        for ln in lines:
            draw.text((MARGIN_X, y), ln, font=f, fill=pal[1])
            y += size + 40
        sub = "practical guide" if idioma == "en" else "guía práctica"
        draw.text((MARGIN_X, 1050), f"{state.get('nicho', '')} - {sub}",
                  font=find_font(60, ImageFont), fill=pal[2])
        out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(d) / "portada.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        if truncated:
            print(msg["truncated"], file=sys.stderr)
        print(msg["cover_ok"].format(path=out))
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
