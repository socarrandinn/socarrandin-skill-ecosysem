#!/usr/bin/env python3
"""Verifica wordcount por capítulo contra los objetivos del outline.

Uso: python check_manuscrito.py <state.json>

Fuente de objetivos: state.json -> capitulos[] (n, titulo, palabras).
Cuenta palabras de cada archivo en <dir>/capitulos/*.md y las compara.
Si no hay carpeta capitulos/, cuenta el total de manuscrito.md.
Salida por capítulo: CHAP <n> <titulo>: esperado X, real Y [WARN_SHORT].
"""
import json
import pathlib
import re
import sys

MSG = {
    "es": {
        "no_state": "ERROR: falta ruta a state.json. Uso: python check_manuscrito.py <state.json>",
        "bad_json": "ERROR: state.json inválido: {e}",
        "no_dir": "ERROR: state.json no tiene clave 'dir' (carpeta del libro)",
        "no_objs": "WARN: state.json no tiene capitulos[] con objetivos; solo conteo total",
        "short": "WARN_SHORT: capítulo {n} ({titulo}) a {pct}% del objetivo ({real}/{objetivo})",
        "ok": "CHECK_OK: {totales}",
        "total": "TOTAL: {n} capítulos, {palabras} palabras",
    },
    "en": {
        "no_state": "ERROR: missing state.json path. Usage: python check_manuscrito.py <state.json>",
        "bad_json": "ERROR: invalid state.json: {e}",
        "no_dir": "ERROR: state.json missing 'dir' key (book folder)",
        "no_objs": "WARN: state.json has no capitulos[] targets; total count only",
        "short": "WARN_SHORT: chapter {n} ({titulo}) at {pct}% of target ({real}/{objetivo})",
        "ok": "CHECK_OK: {totales}",
        "total": "TOTAL: {n} chapters, {palabras} words",
    },
}

THRESHOLD = 0.8  # un capítulo bajo 80% del objetivo emite WARN_SHORT


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


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
    d = pathlib.Path(d)
    objetivos = {c.get("n"): c for c in (state.get("capitulos") or [])}
    totales = []
    cap_dir = d / "capitulos"
    if cap_dir.is_dir():
        for f in sorted(cap_dir.glob("*.md")):
            m = re.match(r"capitulo-(\d+)", f.stem)
            palabras = count_words(f.read_text(encoding="utf-8", errors="replace"))
            linea = f"CHAP {f.stem}: {palabras} palabras"
            if m and int(m.group(1)) in objetivos:
                obj = objetivos[int(m.group(1))]
                objetivo = int(obj.get("palabras") or 0)
                if objetivo:
                    pct = int(100 * palabras / objetivo)
                    linea = f"CHAP {obj.get('n')} ({obj.get('titulo', f.stem)}): esperado {objetivo}, real {palabras}"
                    if palabras < THRESHOLD * objetivo:
                        print(msg["short"].format(n=obj.get("n"), titulo=obj.get("titulo", f.stem),
                                                  pct=pct, real=palabras, objetivo=objetivo),
                              file=sys.stderr)
            totales.append((linea, palabras))
            print(linea)
    else:
        md = d / "manuscrito.md"
        if not md.exists():
            print(f"ERROR: no existe {md}", file=sys.stderr)
            return 4
        totales.append(("manuscrito.md", count_words(md.read_text(encoding="utf-8", errors="replace"))))
        print(f"CHAP manuscrito: {totales[-1][1]} palabras")
    if not objetivos:
        print(msg["no_objs"], file=sys.stderr)
    print(msg["total"].format(n=len(totales), palabras=sum(p for _, p in totales)))
    print(msg["ok"].format(totales=sum(p for _, p in totales)))
    return 0


if __name__ == "__main__":
    sys.exit(main())