#!/usr/bin/env python3
"""Phase 5 (final): Remaining Spanish identifier renames."""

import re, ast
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"

def apply_renames(text, renames):
    for old, new in renames:
        pattern = r'\b' + re.escape(old) + r'\b'
        text = re.sub(pattern, new, text)
    return text

# ─────────────────────────────────────────────────────────────────────────────
# Global renames — applied to every .py file
# Order: longest/most-specific first to avoid partial matches
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_RENAMES = [
    # class names
    ('ManejadorEventos',        'EventHandler'),
    ('cajatexto',               'TextBox'),
    # compound method names (must precede their component words)
    ('cambiar_imagen',          'set_image'),
    ('calcular_rectangulos',    'compute_rects'),
    ('actualizar_rects',        'update_rects'),
    ('actualizar_pj',           'update_character'),
    ('actualizar_marcadores',   'update_markers'),
    ('actualizar_servidor',     'update_server'),
    ('redibujar_boton',         'redraw_button'),
    ('agregar_grupo',           'add_to_group'),
    ('eliminar_grupo',          'remove_from_group'),
    ('evaluar_click',           'get_click_result'),
    ('manejador_eventos',       'handle_events'),
    ('evaluar_respuesta',       'evaluate_answer'),
    ('leer_respuestas',         'speak_answers'),
    ('dibujar_rectangulos',     'draw_debug_rects'),
    ('manejador_popups',        'handle_popup'),
    ('manejador_preguntas',     'handle_key_input'),
    ('cargar_textos',           'load_texts'),
    ('cargar_img_intrucciones', 'load_instruction_images'),
    ('cambiar_rect',            'set_frame'),
    ('cambiar_status',          'set_hover_state'),
    ('chequear_limites',        'check_collisions'),
    ('comparador_longitud',     'has_min_length'),   # before comparador
    ('comparador',              'check_answer'),
    ('caja_vacia',              'is_empty'),
    ('get_palabra',             'get_text'),
    ('get_imagen',              'add_to_group'),
    # simple methods
    ('actualizar',              'advance_frame'),
    ('por_defecto',             'reset'),
    ('reiniciar',               'reset'),
    ('generador',               'process_key'),
    ('renderizado',             'render'),
    ('titilar',                 'blink_cursor'),
    ('iniciar',                 'process'),
    # attributes / fields
    ('fila_pos',                'frame_row'),
    ('texto_visible',           'text_visible'),
    ('imagen_aplaudiendo',      'img_clapping'),
    ('imagen_pensando',         'img_thinking'),
    ('imagen_vacio',            'img_empty'),
    ('tipo_mensaje',            'message_type'),
    ('separacion',              'spacing'),
    ('dic_imagenes',            'image_paths'),
    ('lista_respuestas',        'expected_answer'),
    ('letras_caja',             'text_sprite'),
    ('ocupado',                 'busy'),
    ('chocando',                'colliding'),
    ('indicador',               'cursor_char'),
    ('teclado',                 'keyboard_active'),
    ('salir',                   'active'),
    # button ID (string key + derived attribute)
    ('volver',                  'back'),
]

# ─────────────────────────────────────────────────────────────────────────────
# Per-file renames  (applied AFTER globals for that file)
# key = relative path from src/
# ─────────────────────────────────────────────────────────────────────────────
PER_FILE_RENAMES = {
    'librerias/animations.py': [
        ('cambiar_vel', 'set_speed'),
        # param names inside the file
        ('\\bvel\\b',   'speed'),    # param in cambiar_vel/set_speed
        ('\\bfila\\b',  'row'),      # param in cambiar_rect/set_frame
    ],
    'librerias/personaje.py': [
        ('cambiar_vel',  'reduce_speed'),
        ('\\bimagen\\b', 'image'),   # param in __init__, por_defecto, cambiar_imagen
        ('\\bizq\\b',    'facing_left'),
        ('limites',      'boundaries'),
        ('vel_anim',     'move_speed'),
        ('codigo',       'marker_code'),
        ('chdir',        'set_direction'),
        ('\\bmover\\b',  'move'),
        ('\\bdire\\b',   'reverse_dir'),
    ],
    'librerias/cajatexto.py': [
        ('palabras',     'chars_str'),   # local var  (before palabra)
        ('palabra_f',    'text'),        # self.palabra_f  (before palabra)
        ('\\bpalabra\\b','chars'),       # self.palabra list — NOT the import
        ('\\brespuestas\\b', 'expected_answer'),  # self.respuestas
        ('\\btamano\\b', 'size'),
        ('\\bletra\\b',  'key_input'),   # param in process_key
    ],
    'paginas/menuvisual.py': [
        ('\\btecla\\b',  'key'),         # param name only in this file
    ],
    'paginas/actividad1.py': [
        ('\\bpregunta\\b',   'question'),
        ('\\brespuesta\\b',  'answer'),
        ('\\brespuestas\\b', 'answers'),
        ('\\bvalor\\b',      'value'),
        ('\\brepetir\\b',    'repeat'),
        ('vel_anim',         'move_speed'),   # farmer.vel_anim
        ('codigo',           'marker_code'),  # farmer.codigo
    ],
    'paginas/actividad2.py': [
        ('\\bpregunta\\b',   'question'),
        ('\\btipo\\b',       'layout_type'),  # popup tipo param (local)
        ('\\btam\\b',        'extra_width'),  # popup tam (local)
        ('popupbien',        'popup_correct'),
        ('popupnobien',      'popup_wrong'),
        ('popupvacio',       'popup_empty'),
        ('popupayuda',       'popup_help'),
        ('popupinstruccion', 'popup_instruction'),
        ('popup_instruccion_fija', 'popup_instruction_fixed'),
        ('germinador',       'img_sprouter'),
        ('\\btexto\\b',      'narration'),   # self.texto in activity context
    ],
    'librerias/popups.py': [
        ('\\btipo\\b',   'layout_type'),
        ('\\btam\\b',    'extra_width'),
        ('spacing',      'spacing'),   # already English — no-op placeholder
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Files to skip entirely
# ─────────────────────────────────────────────────────────────────────────────
SKIP_FILES = {
    'librerias/assets_data.py',  # handle separately below
}

# ─────────────────────────────────────────────────────────────────────────────
# Special one-off exact replacements (string, not regex)
# Applied after everything else, to specific files
# ─────────────────────────────────────────────────────────────────────────────
EXACT_REPLACEMENTS = {
    'inicio.py': [
        ('game = Manejador(', 'game = Manager('),
    ],
    'librerias/animations.py': [
        # fix the tipo_objeto string value that was incorrectly renamed
        ('"animation_index"', '"animation"'),
    ],
    'librerias/cajatexto.py': [
        # fix the import: keep module name, rename class
        ('from .palabra import palabra', 'from .palabra import Word'),
        # rename the constructor call (word boundary won't catch 'palabra(' after self.chars rename)
        ('= chars(chars_str', '= Word(chars_str'),  # in case the pattern above over-renames
        ('x = chars(', 'x = Word('),
    ],
    'librerias/assets_data.py': [
        # rename the "volver" key in the dict
        ('"volver": {', '"back": {'),
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# Main processing
# ─────────────────────────────────────────────────────────────────────────────
total_replacements = 0
files_changed = []

for py_file in sorted(SRC.rglob("*.py")):
    rel = py_file.relative_to(SRC).as_posix()
    if rel in SKIP_FILES:
        # Still apply exact replacements for skipped files
        original = py_file.read_text(encoding='utf-8')
        text = original
        for old_str, new_str in EXACT_REPLACEMENTS.get(rel, []):
            count = text.count(old_str)
            if count:
                text = text.replace(old_str, new_str)
                total_replacements += count
        if text != original:
            py_file.write_text(text, encoding='utf-8')
            files_changed.append(rel)
        continue

    original = py_file.read_text(encoding='utf-8')
    text = original

    # 1. Apply global renames
    for old, new in GLOBAL_RENAMES:
        pattern = r'\b' + re.escape(old) + r'\b'
        new_text = re.sub(pattern, new, text)
        count = len(re.findall(pattern, text))
        if count:
            total_replacements += count
        text = new_text

    # 2. Apply per-file renames
    for old, new in PER_FILE_RENAMES.get(rel, []):
        # If old starts with \b it's already a regex; otherwise wrap with \b
        if old.startswith('\\b') or old.startswith('('):
            pattern = old
        else:
            pattern = r'\b' + re.escape(old) + r'\b'
        new_text = re.sub(pattern, new, text)
        count = len(re.findall(pattern, text))
        if count:
            total_replacements += count
        text = new_text

    # 3. Apply exact (string) replacements
    for old_str, new_str in EXACT_REPLACEMENTS.get(rel, []):
        count = text.count(old_str)
        if count:
            text = text.replace(old_str, new_str)
            total_replacements += count

    if text != original:
        py_file.write_text(text, encoding='utf-8')
        files_changed.append(rel)

print(f"\nTotal replacements: {total_replacements}")
print(f"Files changed: {len(files_changed)}")
for f in files_changed:
    print(f"  {f}")

# Syntax check all changed files
print("\nSyntax check:")
errors = []
for f in files_changed:
    path = SRC / f
    try:
        ast.parse(path.read_text(encoding='utf-8'))
        print(f"  OK: {f}")
    except SyntaxError as e:
        print(f"  ERROR: {f}: {e}")
        errors.append((f, e))

if errors:
    print(f"\n{len(errors)} syntax error(s) found!")
    import sys; sys.exit(1)
else:
    print("\nAll files pass syntax check.")
