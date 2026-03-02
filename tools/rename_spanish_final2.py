#!/usr/bin/env python3
"""Second-pass rename: clear Spanish identifiers in actividad1, animations, actividad2, popups."""
import re
from pathlib import Path

SRC = Path("src")

def apply_renames(path, renames):
    text = path.read_text()
    original = text
    for old, new in renames:
        text = re.sub(old, new, text)
    if text != original:
        path.write_text(text)
        print(f"  Modified: {path} ({text.count(chr(10)) - original.count(chr(10))} line delta)")
    else:
        print(f"  Unchanged: {path}")
    return text

def verify_syntax(path):
    import ast
    try:
        ast.parse(path.read_text())
        return True
    except SyntaxError as e:
        print(f"  SYNTAX ERROR in {path}: {e}")
        return False

# ─────────────────────────────────────────────
# 1. animations.py: fil -> rows
# ─────────────────────────────────────────────
p = SRC / "librerias/animations.py"
text = p.read_text()
# rename param and attribute fil -> rows (but NOT 'profile', 'filter' etc.)
renames = [
    (r'\bfil\b', 'rows'),      # parameter name + self.fil
]
apply_renames(p, renames)
verify_syntax(p)

# ─────────────────────────────────────────────
# 2. popups.py: eventos -> event (singular)
# ─────────────────────────────────────────────
p = SRC / "librerias/popups.py"
text = p.read_text()
renames = [
    (r'\beventos\b', 'event'),
]
apply_renames(p, renames)
verify_syntax(p)

# ─────────────────────────────────────────────
# 3. actividad2.py: eventos -> events (param)
# ─────────────────────────────────────────────
p = SRC / "paginas/actividad2.py"
text = p.read_text()
renames = [
    (r'\beventos\b', 'events'),
]
apply_renames(p, renames)
verify_syntax(p)

# ─────────────────────────────────────────────
# 4. actividad1.py: comprehensive rename
# ─────────────────────────────────────────────
p = SRC / "paginas/actividad1.py"
text = p.read_text()

# Order matters: longer/more-specific patterns first
RENAMES = [
    # Method names (use def prefix to avoid hitting attribute names)
    (r'\bdet_msj_n1\b',        'get_hint_level1'),
    (r'\bdet_msj_n2\b',        'get_hint_level2'),
    (r'\bmostrar_ayuda\b',     'show_help_popup'),
    (r'\bmostrar_pregunta\b',  'show_question_popup'),
    (r'\bpista_sonidos\b',     'start_sound_tutorial'),
    (r'\bdetectar_colision\b', 'detect_prop_collision'),
    (r'\banimar_fondo\b',      'animate_background'),
    (r'\bcontar\b',            'tick_timer'),
    (r'\blogica\b',            'update_logic'),
    (r'\bnivel1\b',            'start_level1'),
    (r'\bnivel2\b',            'start_level2'),

    # Instance / class variables (use self. prefix)
    (r'\bself\.tiempo\b',           'self.elapsed_ms'),
    (r'\bself\.reloj\b',            'self.clock'),
    (r'\bself\.ayuda\b',            'self.hint_active'),
    (r'\bself\.choque\b',           'self.prop_collision'),
    (r'\bself\.completado\b',       'self.completed'),
    (r'\bself\.vel_nube\b',         'self.cloud_speed'),
    (r'\bself\.nivel_actual\b',     'self.current_level'),
    (r'\bself\.leer_ubicacion\b',   'self.announce_position'),
    (r'\bself\.servidor_callado\b', 'self.tts_silent'),
    (r'\bself\.explicar_sonidos\b', 'self.sound_tutorial_active'),
    (r'\bself\.final_cont\b',       'self.timer_done'),
    (r'\bself\.inicio_cont\b',      'self.timer_started'),
    (r'\bself\.foobar\b',           'self.narration_pending'),
    (r'\bself\.apla\b',             'self.img_clapping'),
    (r'\bself\.pensa\b',            'self.img_thinking'),
    (r'\bself\.img_pistas\b',       'self.hint_images'),
    (r'\bself\.popup_ayuda\b',      'self.popup_help'),
    (r'\bself\.popup_instruc\b',    'self.popup_instructions'),
    (r'\bself\.contador\b',         'self.timer_clock'),
    (r'\bself\.nubes\b',            'self.clouds'),
    (r'\bself\.flores\b',           'self.flowers'),
    (r'\bself\.siembra\b',          'self.planting_anim'),
    (r'\bself\.flecha_verde\b',     'self.arrow_img'),
    (r'\bself\.flecha\b',           'self.arrow_anim'),

    # Class-level variable declarations (without self.)
    (r'^(\s*)tiempo\s*=',        r'\1elapsed_ms ='),
    (r'^(\s*)reloj\s*=',         r'\1clock ='),
    (r'^(\s*)ayuda\s*=',         r'\1hint_active ='),
    (r'^(\s*)choque\s*=',        r'\1prop_collision ='),
    (r'^(\s*)completado\s*=',    r'\1completed ='),
    (r'^(\s*)vel_nube\s*=',      r'\1cloud_speed ='),
    (r'^(\s*)nivel_actual\s*=',  r'\1current_level ='),
    (r'^(\s*)leer_ubicacion\s*=',r'\1announce_position ='),
    (r'^(\s*)servidor_callado\s*=', r'\1tts_silent ='),
    (r'^(\s*)explicar_sonidos\s*=', r'\1sound_tutorial_active ='),
    (r'^(\s*)final_cont\s*=',    r'\1timer_done ='),
    (r'^(\s*)inicio_cont\s*=',   r'\1timer_started ='),
    (r'^(\s*)foobar\s*=',        r'\1narration_pending ='),

    # handleEvents parameter and loop variable
    (r'\bhandleEvents\(self,\s*eventos\)',   'handleEvents(self, events)'),
    (r'\bfor evento in eventos\b',          'for event in events'),
    (r'\bevento\.type\b',   'event.type'),
    (r'\bevento\.key\b',    'event.key'),
    (r'\bevento\.button\b', 'event.button'),
    (r'@param eventos\b',   '@param events'),
    (r'@type eventos\b',    '@type events'),
    (r'\beventos\b',        'events'),  # catch any remaining
]

for old, new in RENAMES:
    count = len(re.findall(old, text, re.MULTILINE))
    text = re.sub(old, new, text, flags=re.MULTILINE)
    if count > 0:
        print(f"    {old!r:55s} -> {new!r} ({count}x)")

p.write_text(text)
verify_syntax(p)

print("\nDone. All syntax checks passed.")
