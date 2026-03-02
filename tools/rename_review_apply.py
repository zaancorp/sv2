#!/usr/bin/env python3
"""Apply all items from RENAME_REVIEW.md."""
import re
import ast
from pathlib import Path

SRC = Path(".")

def check(path):
    try:
        ast.parse(path.read_text())
    except SyntaxError as e:
        print(f"  SYNTAX ERROR: {path}: {e}")
        raise

def repl_inplace(path, pairs):
    """Apply list of (old_str, new_str) literal replacements."""
    text = path.read_text()
    orig = text
    for old, new in pairs:
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            print(f"    {repr(old)[:50]:50s} -> {repr(new)} ({count}x)")
    if text != orig:
        path.write_text(text)
        check(path)
    return text

def repl_regex(path, pairs, flags=0):
    """Apply list of (pattern, replacement) regex replacements."""
    text = path.read_text()
    orig = text
    for old, new in pairs:
        count = len(re.findall(old, text, flags=flags))
        if count:
            text = re.sub(old, new, text, flags=flags)
            print(f"    {repr(old)[:50]:50s} -> {repr(new)} ({count}x)")
    if text != orig:
        path.write_text(text)
        check(path)
    return text


# ══════════════════════════════════════════════════════════════
# ITEM 1: tipo_objeto → obj_type + string values
# ══════════════════════════════════════════════════════════════
print("\n=== Item 1: tipo_objeto → obj_type ===")

# Step A: rename the attribute name globally across all files
for f in SRC.rglob("*.py"):
    text = f.read_text()
    if "tipo_objeto" in text:
        f.write_text(text.replace("tipo_objeto", "obj_type"))
        print(f"  tipo_objeto → obj_type  in {f}")
        check(f)

# Step B: rename the Spanish string values, but ONLY in obj_type context
#  This avoids renaming "boton" in TextButton("boton", ...) which is a button ID, not a type tag
for f in SRC.rglob("*.py"):
    text = f.read_text()
    if "obj_type" not in text:
        continue
    orig = text
    # setter side: self.obj_type = "boton"
    text = re.sub(r'(obj_type\s*=\s*)"boton"',   r'\1"button"', text)
    text = re.sub(r'(obj_type\s*=\s*)"palabra"',  r'\1"word"',   text)
    text = re.sub(r'(obj_type\s*=\s*)"mapa"',     r'\1"map"',    text)
    # comparison side: .obj_type == "boton"
    text = re.sub(r'(obj_type\s*==\s*)"boton"',   r'\1"button"', text)
    text = re.sub(r'(obj_type\s*==\s*)"palabra"',  r'\1"word"',   text)
    text = re.sub(r'(obj_type\s*==\s*)"mapa"',     r'\1"map"',    text)
    if text != orig:
        f.write_text(text)
        print(f"  string values updated in {f}")
        check(f)


# ══════════════════════════════════════════════════════════════
# ITEM 2: text-type string literals
# ══════════════════════════════════════════════════════════════
print("\n=== Item 2: text type strings ===")
for f in SRC.rglob("*.py"):
    text = f.read_text()
    if '"texto_act"' in text or '"caja_texto"' in text:
        orig = text
        text = text.replace('"texto_act"', '"active_text"')
        text = text.replace('"caja_texto"', '"textbox"')
        if text != orig:
            f.write_text(text)
            print(f"  text type strings in {f}")
            check(f)


# ══════════════════════════════════════════════════════════════
# ITEM 3: delete self.pantalla = 0 (dead code)
# ══════════════════════════════════════════════════════════════
print("\n=== Item 3: delete self.pantalla ===")
p = SRC / "manejador.py"
text = p.read_text()
new = re.sub(r'^\s*self\.pantalla\s*=\s*0\s*\n', '', text, flags=re.MULTILINE)
if new != text:
    p.write_text(new)
    print(f"  Removed self.pantalla = 0 from manejador.py")
    check(p)


# ══════════════════════════════════════════════════════════════
# ITEM 4: handle_magnifier parameter rename (pantalla.py)
# ══════════════════════════════════════════════════════════════
print("\n=== Item 4: handle_magnifier(evento) ===")
p = SRC / "librerias/pantalla.py"
repl_inplace(p, [
    ("def handle_magnifier(self, evento):", "def handle_magnifier(self, events):"),
    ("@param evento: Event list from the current frame.", "@param events: Event list from the current frame."),
    ("@type evento: list", "@type events: list"),
    ("for event in evento:", "for event in events:"),
    ("                    evento = True", "                    mouse_down = True"),
    ("                else:\n                    evento = False", "                else:\n                    mouse_down = False"),
    ("                if evento == False:", "                if not mouse_down:"),
])


# ══════════════════════════════════════════════════════════════
# ITEM 5 (item 6 in file): interprete.py
# ══════════════════════════════════════════════════════════════
print("\n=== Item 5: interprete.py ===")
p = SRC / "interprete/interprete.py"
# Use ordered literal replacements (order matters to avoid double-replacing)
repl_inplace(p, [
    # dict contents on VocabTable
    ("self.dic = {",           "self.clips = {"),
    ("self.diccolor = {",      "self.shirt_colors = {"),
    # lookup method internals (before renaming class name)
    ("tupla = self.dic[palabra]", "clip_info = self.clips[word]"),
    ("return tupla",           "return clip_info"),
    # lookup_color method
    ("tupla = self.diccolor[color]", "clip_info = self.shirt_colors[color]"),
    # class and method names
    ("class Vocabulario:",     "class VocabTable:"),
    ("class Interprete:",      "class Interpreter:"),
    ("def Consultar(self, palabra):", "def lookup(self, word):"),
    ("def consultarcolor(self, color):", "def lookup_color(self, color):"),
    ("def Interpretar(self):", "def play_sign(self):"),
    ("def Repetir(self):",     "def replay(self):"),
    # mover_palabra: class method AND module-level function
    ("    def mover_palabra(self):", "    def position_word(self):"),
    ("def mover_palabra(self):", "def position_word_handler(self):"),
    # module-level repetir
    ("def repetir(self):",     "def replay_handler(self):"),
    # instance attributes
    ("self.genero",            "self.gender"),
    ("self.palabra",           "self.word"),
    ("self.velocidad",         "self.speed"),
    ("self.scena",             "self.scene"),
    ("self.controlador",       "self.controller"),
    ("self.voc = Vocabulario()", "self.vocab = VocabTable()"),
    # method calls
    ("self.voc.Consultar(",    "self.vocab.lookup("),
    ("self.voc.consultarcolor(", "self.vocab.lookup_color("),
    ("self.Interpretar()",     "self.play_sign()"),
    ("self.Repetir()",         "self.replay()"),
    ("self.mover_palabra()",   "self.position_word()"),
    # local variables in play() / Interpretar()
    ("cotas = self.vocab.lookup(self.word)", "clip_info = self.vocab.lookup(self.word)"),
    ("cotas[0]",               "clip_info[0]"),
    ("cotas[1]",               "clip_info[1]"),
    ("actuador = ",            "actuator = "),
    ("actuador.",              "actuator."),
    # module-level functions locals
    ("    interprete = Interpreter()", "    interpreter = Interpreter()"),
    ("    interprete.",        "    interpreter."),
    ("scena = logic.getCurrentScene()", "scene = logic.getCurrentScene()"),
    ("        scena.objects",  "        scene.objects"),
    ("    scena = ",           "    scene = "),
    ("    scena.objects",      "    scene.objects"),
    ("cont = logic.getCurrentController()", "controller = logic.getCurrentController()"),
    ("cont.sensors",           "controller.sensors"),
    ("cont.owner",             "controller.owner"),
    ("cont.actuators",         "controller.actuators"),
])


# ══════════════════════════════════════════════════════════════
# ITEM 6a (item 7): button ID "sig" → "next"
# ══════════════════════════════════════════════════════════════
print("\n=== Item 6a: button ID sig → next ===")
# assets_data.py: rename the dict key
p = SRC / "librerias/assets_data.py"
text = p.read_text()
# Replace only the top-level dict key (not inside the value)
text = re.sub(r'^(\s*)"sig":', r'\1"next":', text, count=1, flags=re.MULTILINE)
p.write_text(text)
check(p)
print(f"  sig key → next in assets_data.py")

# All screen files: rename attribute accesses and ID comparisons
for f in SRC.rglob("*.py"):
    text = f.read_text()
    if "self.sig" not in text and '"sig"' not in text:
        continue
    orig = text
    text = re.sub(r'\bself\.sig\b', 'self.next', text)
    text = text.replace('"sig"', '"next"')
    if text != orig:
        f.write_text(text)
        print(f"  sig → next in {f}")
        check(f)


# ══════════════════════════════════════════════════════════════
# ITEM 6b (item 7): button ID "inicio" → "intro"
# ══════════════════════════════════════════════════════════════
print("\n=== Item 6b: button ID inicio → intro ===")
# assets_data.py
p = SRC / "librerias/assets_data.py"
text = p.read_text()
text = re.sub(r'^(\s*)"inicio":', r'\1"intro":', text, count=1, flags=re.MULTILINE)
p.write_text(text)
check(p)
print(f"  inicio key → intro in assets_data.py")

# All screen files
for f in SRC.rglob("*.py"):
    text = f.read_text()
    if "self.inicio" not in text and '"inicio"' not in text:
        continue
    orig = text
    text = re.sub(r'\bself\.inicio\b', 'self.intro', text)
    text = text.replace('"inicio"', '"intro"')
    if text != orig:
        f.write_text(text)
        print(f"  inicio → intro in {f}")
        check(f)


# ══════════════════════════════════════════════════════════════
# ITEM 6c (item 7): button ID "active" → "exit" (actividad1.py only)
# ══════════════════════════════════════════════════════════════
print("\n=== Item 6c: button ID active → exit (actividad1) ===")
p = SRC / "paginas/actividad1.py"
repl_inplace(p, [
    ('"active"', '"exit"'),
])
repl_regex(p, [(r'\bself\.active\b', 'self.exit_btn')])


# ══════════════════════════════════════════════════════════════
# ITEM 7 (item 8): delete self.finished dead code
# ══════════════════════════════════════════════════════════════
print("\n=== Item 7: remove self.finished dead code ===")
for name in ["pantalla3.py", "pantalla4.py", "pantalla5.py", "pantalla6.py", "pantalla8.py"]:
    f = SRC / "paginas" / name
    text = f.read_text()
    new = re.sub(r'^\s*self\.finished\s*=\s*False\s*\n', '', text, flags=re.MULTILINE)
    if new != text:
        f.write_text(new)
        print(f"  Removed self.finished from {name}")
        check(f)


# ══════════════════════════════════════════════════════════════
# FINAL SYNTAX CHECK
# ══════════════════════════════════════════════════════════════
print("\n=== Final syntax check ===")
errors = []
files = list(SRC.rglob("*.py"))
for f in files:
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        errors.append(f"{f}: {e}")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  {e}")
else:
    print(f"All {len(files)} files OK")
