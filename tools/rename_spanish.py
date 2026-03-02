#!/usr/bin/env python3
"""
Rename Spanish identifiers to English across the sv2 codebase.

Usage:
    python tools/rename_spanish.py [--dry-run]
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# RENAME MAPPINGS
# Each entry is (old_name, new_name).  They are applied in ORDER — put longer
# or more specific names first to avoid partial-match collisions.
# All matches use \b word boundaries, so they only touch whole identifiers.
# ---------------------------------------------------------------------------

RENAMES = [
    # -----------------------------------------------------------------------
    # pantalla.py — sprite groups (referenced as self.X in every screen file)
    # -----------------------------------------------------------------------
    ("grupo_magnificador", "magnifier_group"),
    ("grupo_cuadro_texto", "text_box_group"),
    ("grupo_fondotexto",   "text_bg_group"),
    ("grupo_palabras",     "word_group"),
    ("grupo_botones",      "button_group"),
    ("grupo_banner",       "banner_group"),
    ("grupo_tooltip",      "tooltip_group"),
    ("grupo_update",       "update_group"),
    ("grupo_imagen",       "image_group"),
    ("grupo_popup",        "popup_group"),
    ("grupo_anim",         "anim_group"),
    ("grupo_mapa",         "map_group"),

    # -----------------------------------------------------------------------
    # pantalla.py — class-level singletons
    # -----------------------------------------------------------------------
    ("obj_magno",  "magnifier"),
    ("spserver",   "speech_server"),

    # -----------------------------------------------------------------------
    # pantalla.py — navigation / per-screen state attributes
    # -----------------------------------------------------------------------
    ("lista_mascaras",      "mask_list"),
    ("lista_botones",       "button_list"),
    ("lista_palabra",       "word_list"),
    ("lista_final",         "nav_list"),
    ("elemento_actual",     "focus_index"),
    ("numero_elementos",    "element_count"),
    ("entrada_primera_vez", "first_entry"),
    ("deteccion_movimiento","keyboard_nav_active"),
    ("anim_actual",         "current_anim"),
    ("reloj_anim",          "frame_clock"),
    ("canal_audio",         "audio_channel"),

    # -----------------------------------------------------------------------
    # pantalla.py — path constants
    # -----------------------------------------------------------------------
    ("varios", "misc_path"),

    # -----------------------------------------------------------------------
    # pantalla.py — methods
    # -----------------------------------------------------------------------
    ("limpiar_grupos",                   "clear_groups"),
    ("chequeo_mascaras",                 "collect_masks"),
    ("chequeo_botones",                  "collect_buttons"),
    ("chequeo_palabra",                  "collect_words"),
    ("controlador_lector_evento_K_RIGHT","nav_right"),
    ("controlador_lector_evento_K_LEFT", "nav_left"),
    ("definir_rect",                     "set_focus_rect"),
    ("dibujar_rect",                     "draw_focus_rect"),
    ("sonido_on",                        "init_audio"),
    ("minimag",                          "handle_magnifier"),

    # -----------------------------------------------------------------------
    # pantalla.py — previa (is_overlay): constructor param + instance attr
    # -----------------------------------------------------------------------
    ("previa", "is_overlay"),

    # -----------------------------------------------------------------------
    # manejador.py — Manejador class attrs / methods
    # -----------------------------------------------------------------------
    ("VOLVER_PANTALLA_PREVIA", "RETURN_TO_PREV_SCREEN"),
    ("rutas_int",              "interpreter_paths"),
    ("primera_vez",            "first_run"),
    ("habilitar",              "magnifier_active"),
    ("interpretar",            "show_concept"),
    ("animacion",              "animation_index"),   # instance attr = 0 on Manejador

    # -----------------------------------------------------------------------
    # paginas/ — common per-screen Spanish names
    # -----------------------------------------------------------------------
    ("cargar_preferencias", "load_preferences"),
    ("portada_glosario",    "at_glossary_cover"),
    ("ir_glosario",         "go_to_glossary"),
    ("camisas_mujer",       "female_shirts"),
    ("camisas_hombre",      "male_shirts"),

    # -----------------------------------------------------------------------
    # librerias/ — compound names containing Spanish fragments
    # (must come BEFORE the bare fragments below)
    # -----------------------------------------------------------------------
    ("ancho_final",  "final_width"),   # Text/TextOCI computed-width attribute
    ("img_fondo2",   "img_bg2"),       # Button/Popup background surface (hover)
    ("img_fondo",    "img_bg"),        # Button/Popup background surface (normal)

    # -----------------------------------------------------------------------
    # librerias/ — imgfondo.py: local parameter / variable names
    # NOTE: 'largo'/'ancho' in imgfondo.py are handled in PER_FILE_RENAMES
    #        because both would map to 'width' here, causing a collision
    #        (ancho is used as HEIGHT in that file).
    # -----------------------------------------------------------------------
    ("borde",  "border"),
    ("grosor", "corner_radius"),

    # -----------------------------------------------------------------------
    # librerias/ — magnificador.py
    # -----------------------------------------------------------------------
    ("aumentar",  "zoom_in"),
    ("disminuir", "zoom_out"),
    ("ventana",   "surface"),  # parameter name in magnificar(), not a widget

    # -----------------------------------------------------------------------
    # librerias/ — personaje.py character sprite attributes / methods
    # -----------------------------------------------------------------------
    ("velocidad_caida", "fall_speed"),
    ("velocidad_salto", "jump_speed"),
    ("en_suelo",        "on_ground"),
    ("num_saltos",      "jump_count"),
    ("direccion",       "direction"),
    ("gravedad",        "gravity"),
    ("saltar",          "jump"),
    ("caer",            "fall"),
    ("caminar",         "walk"),
    ("voltear",         "flip"),
    ("parar",           "stop"),
    ("lado",            "side"),

    # -----------------------------------------------------------------------
    # librerias/ — cajatexto.py / button.py / textoci.py / imgfondo.py
    # Generic dimension names — placed AFTER compound names above
    # -----------------------------------------------------------------------
    ("margen", "margin"),
    ("ancho",  "width"),
    ("alto",   "height"),

    # -----------------------------------------------------------------------
    # librerias/ — popups.py / button.py
    # 'fondo' as a Python identifier (class name OR parameter name).
    # NOTE: assets_data.py is EXCLUDED below — it only uses 'fondo' in string
    # values (filenames like "fondo-inicio.png"), not as a Python identifier.
    # -----------------------------------------------------------------------
    ("boton_cerrar", "close_button"),
    ("fondo", "background"),   # class fondo in imgfondo; param fondo=0 in button

    # -----------------------------------------------------------------------
    # actividad1/2 — game level counter (only as an identifier, not in strings)
    # Handled via PRECISE_RENAMES below to avoid touching TTS string literals.
    # -----------------------------------------------------------------------
    # 'nivel' is intentionally omitted here; handled precisely below.
]

# ---------------------------------------------------------------------------
# PER-FILE RENAMES — applied only to the specified file.
# Maps file path → list of (old_name, new_name) to apply BEFORE global renames.
# ---------------------------------------------------------------------------

IMGFONDO = Path("/Users/jose/Projects/sv2/src/librerias/imgfondo.py")

PER_FILE_RENAMES: dict[Path, list] = {
    # In imgfondo.py, 'largo' is the width and 'ancho' is the HEIGHT
    # (the original Spanish naming is inconsistent: ancho = "wide" but used as height).
    IMGFONDO: [
        ("largo", "width"),
        ("ancho", "height"),
    ],
}

# Files that should skip the GLOBAL rename for certain names.
# Key: Path, Value: set of old_names to skip for that file.
PER_FILE_SKIP: dict[Path, set] = {
    # imgfondo.py already handles 'largo' and 'ancho' via PER_FILE_RENAMES above.
    IMGFONDO: {"largo", "ancho"},
}

# ---------------------------------------------------------------------------
# PRECISE RENAMES — applied as literal regex patterns, not word boundaries
# ---------------------------------------------------------------------------

PRECISE_RENAMES = [
    # 'pops' → 'popups_path' (only as a self.pops attribute)
    (r'\bself\.pops\b',            "self.popups_path"),
    # 'raton' → 'mouse'
    (r'\braton\b',                 "mouse"),
    # 'nivel' → 'level' — only as a bare identifier (self.nivel, nivel =, etc.)
    # Deliberately NOT matching the word inside Spanish string literals.
    (r'\bself\.nivel\b',           "self.level"),
    (r'\bnivel\s*=',               "level ="),
    (r'==\s*nivel\b',              "== level"),
    (r'self\.nivel\b',             "self.level"),
]

# ---------------------------------------------------------------------------
# FILES TO EXCLUDE from specific renames
# ---------------------------------------------------------------------------

# assets_data.py only has 'fondo' inside filename strings like "fondo-inicio.png"
# — no Python identifiers — so renaming would corrupt the filenames.
EXCLUDE_FROM_ALL = {
    Path("/Users/jose/Projects/sv2/src/librerias/assets_data.py"),
}

# ---------------------------------------------------------------------------
# SOURCE ROOT
# ---------------------------------------------------------------------------

SRC = Path("/Users/jose/Projects/sv2/src")
PYTHON_FILES = sorted(SRC.rglob("*.py"))

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def make_word_pattern(name: str) -> re.Pattern:
    """Return a regex that matches 'name' as a complete identifier token."""
    return re.compile(r'\b' + re.escape(name) + r'\b')


def rename_in_text(text: str, renames: list, skip: set = None) -> tuple[str, list]:
    """Apply word-boundary renames; return (new_text, list_of_(old,new,count))."""
    changes = []
    for old, new in renames:
        if skip and old in skip:
            continue
        pattern = make_word_pattern(old)
        hits = pattern.findall(text)
        if hits:
            text = pattern.sub(new, text)
            changes.append((old, new, len(hits)))
    return text, changes


def apply_precise_renames(text: str) -> tuple[str, list]:
    """Apply precise (hand-written) regex renames."""
    changes = []
    for pat_str, replacement in PRECISE_RENAMES:
        pattern = re.compile(pat_str)
        hits = pattern.findall(text)
        if hits:
            text = pattern.sub(replacement, text)
            changes.append((pat_str, replacement, len(hits)))
    return text, changes


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    total_files = 0
    total_replacements = 0

    for filepath in PYTHON_FILES:
        if filepath in EXCLUDE_FROM_ALL:
            continue

        original = filepath.read_text(encoding="utf-8")

        # 1. Apply per-file renames first (take precedence over globals).
        per_file = PER_FILE_RENAMES.get(filepath, [])
        modified, pf_changes = rename_in_text(original, per_file)

        # 2. Apply global renames, skipping names handled per-file.
        skip = PER_FILE_SKIP.get(filepath, set())
        modified, changes = rename_in_text(modified, RENAMES, skip=skip)

        # 3. Apply precise regex renames.
        modified, precise = apply_precise_renames(modified)
        all_changes = pf_changes + changes + precise

        if modified != original:
            total_files += 1
            total_replacements += sum(c[2] for c in all_changes)
            tag = "[DRY RUN] " if dry_run else ""
            print(f"\n{tag}Modified: {filepath.relative_to(SRC.parent)}")
            for old, new, count in all_changes:
                print(f"  {old!r:50s} → {new!r}  ({count}x)")
            if not dry_run:
                filepath.write_text(modified, encoding="utf-8")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total: {total_files} files, {total_replacements} replacements")


if __name__ == "__main__":
    main()
