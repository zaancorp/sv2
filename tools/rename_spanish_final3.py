#!/usr/bin/env python3
"""Third-pass rename: self.tiempo in pantalla files, actividad2 levels, contador.py."""
import re
import ast
from pathlib import Path

SRC = Path("src")

def replace(path, pairs):
    """pairs: list of (old, new) or (old, new, flags)"""
    text = path.read_text()
    original = text
    for entry in pairs:
        if len(entry) == 2:
            old, new = entry
            flags = 0
        else:
            old, new, flags = entry
        count = len(re.findall(old, text, flags=flags))
        if count:
            text = re.sub(old, new, text, flags=flags)
            print(f"    {old!r:45s} -> {new!r} ({count}x)")
    if text != original:
        path.write_text(text)
    return text

def check_syntax(path):
    try:
        ast.parse(path.read_text())
        print(f"  OK: {path}")
    except SyntaxError as e:
        print(f"  SYNTAX ERROR: {path}: {e}")

# 1. pantalla3,4,5,6,8: self.tiempo -> self.elapsed_ms
for name in ["pantalla3.py", "pantalla4.py", "pantalla5.py", "pantalla6.py", "pantalla8.py"]:
    p = SRC / "paginas" / name
    print(f"\n--- {p} ---")
    replace(p, [(r'\bself\.tiempo\b', 'self.elapsed_ms')])
    check_syntax(p)

# 2. actividad2.py
p = SRC / "paginas/actividad2.py"
print(f"\n--- {p} ---")
replace(p, [
    (r'\bself\.instruccion1\b', 'self.instruction1'),
    (r'\bself\.nivel_cargado\b', 'self.loaded_level'),
    (r'\bnivel_cargado\b', 'loaded_level'),
    (r'\bdef nivel1\b', 'def start_level1'),
    (r'\bdef nivel2\b', 'def start_level2'),
    (r'\bdef nivel3\b', 'def start_level3'),
    (r'\bself\.nivel1\(\)', 'self.start_level1()'),
    (r'\bself\.nivel2\(\)', 'self.start_level2()'),
    (r'\bself\.nivel3\(\)', 'self.start_level3()'),
])
check_syntax(p)

# 3. contador.py
p = SRC / "librerias/contador.py"
print(f"\n--- {p} ---")
replace(p, [
    (r'\bdef contar\b', 'def tick'),
    (r'\bself\.inicio\b', 'self.started'),
    (r'\bself\.final\b', 'self.done'),
    (r'^(\s*)inicio\s*=', r'\1started =', re.MULTILINE),
    (r'^(\s*)final\s*=',  r'\1done =', re.MULTILINE),
])
check_syntax(p)

print("\n\nFinal full syntax check:")
errors = []
for f in (SRC).rglob("*.py"):
    try:
        ast.parse(f.read_text())
    except SyntaxError as e:
        errors.append(f"{f}: {e}")
if errors:
    print("ERRORS:")
    for e in errors: print(e)
else:
    print(f"All {len(list(SRC.rglob('*.py')))} files OK")
