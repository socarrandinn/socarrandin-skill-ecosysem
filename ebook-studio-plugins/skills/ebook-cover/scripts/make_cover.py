import json, pathlib, sys
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess; subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
    from PIL import Image, ImageDraw, ImageFont

PALETTES = {
    "salud":   ("#1B5E20", "#FFFFFF", "#A5D6A7"),
    "cocina":  ("#BF360C", "#FFFFFF", "#FFCCBC"),
    "dinero":  ("#1A237E", "#FFFFFF", "#9FA8DA"),
    "infantil":("#4A148C", "#FFFFFF", "#CE93D8"),
    "default": ("#263238", "#FFFFFF", "#B0BEC5"),
}
def font(size):
    for name in ("arialbd.ttf", "arial.ttf"):
        p = pathlib.Path("C:/Windows/Fonts") / name
        if p.exists(): return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()

def main():
    state = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    n = state.get("nicho","").strip().lower()
    first = n.split()[0] if n else ""
    pal = PALETTES["default"]
    img = Image.new("RGB", (2560, 1600), pal[0])
    draw = ImageDraw.Draw(img)
    for p, c in PALETTES.items():
        if p in first: pal = c; draw.rectangle([0,0,2560,1600], fill=c[0]); break
    title = state.get("titulo", "Libro")
    lines = []
    cur = ""
    for w in title.split():
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= 30:
            cur += " " + w
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    if len(lines) > 3:
        print("TITLE_TRUNCATED: título demasiado largo", file=sys.stderr)
    y = 500
    for ln in lines[:3]:
        draw.text((200, y), ln, font=font(110), fill=PALETTES["default"][1]); y += 150
    sub = "practical guide" if state.get("idioma") == "en" else "guía práctica"
    draw.text((200, 1050), f"{state.get('nicho','')} - {sub}", font=font(60), fill=pal[2])
    img.save(pathlib.Path(state["dir"]) / "portada.png")

if __name__ == "__main__":
    main()