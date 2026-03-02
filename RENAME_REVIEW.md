# Rename Review

These identifiers were deferred during the Spanish→English rename pass because their meaning
was ambiguous, the rename requires coordinated changes across many files, or the identifier
lives in a special execution environment. Please review each item and provide a preferred name
(or confirm the suggestion) so the rename can be applied.

---

## 1. `tipo_objeto` — type-discriminator attribute

**Files affected:** 15+ files
**Current value strings:** `"boton"`, `"palabra"`, `"mapa"`, `"animation"`

`tipo_objeto` ("type of object") is a string tag set on every interactive sprite so that
keyboard-navigation code can dispatch on sprite kind without an `isinstance()` check.

| Location | Class | Current value |
|---|---|---|
| `src/librerias/button.py:62` | `Button` | `"boton"` |
| `src/librerias/palabra.py:82` | `Word` | `"palabra"` |
| `src/librerias/objmask.py:26` | `ObjMask` | `"mapa"` |
| `src/librerias/animations.py:47` | `Animation` | `"animation"` |

Checked against in `src/paginas/pantalla2–11.py`, `menucfg.py`, `playground.py`, and
`actividad2.py` (e.g. `if self.x.tipo_objeto == "boton":`).

**Suggested rename:**
- attribute: `tipo_objeto` → `obj_type`
- string `"boton"` → `"button"`
- string `"palabra"` → `"word"`
- string `"mapa"` → `"map"`
- string `"animation"` already English — keep as-is

This is a coordinated change (attribute + all comparison strings across 15 files). Confirm
before applying.

---

## 2. `"texto_act"` / `"caja_texto"` — text-rendering mode tags

**Files affected:** `button.py`, `texto.py`, `popups.py`, `textoci.py`, `cajatexto.py`

These strings are passed as the `text_type` argument to the `Text` / `TextOCI` constructor
and control whether `"Reproducción"` is treated specially (glossary-link suppression).

| String | Where set | Meaning |
|---|---|---|
| `"texto_act"` | `button.py:226`, `popups.py:80,159` | active/button text — suppress glossary links |
| `"caja_texto"` | `cajatexto.py:136` | text-box entry — suppress glossary links |

**Suggested rename:**
- `"texto_act"` → `"active_text"`
- `"caja_texto"` → `"textbox"`

Confirm before applying (requires touching `texto.py` and `textoci.py` conditionals).

---

## 3. `self.pantalla = 0` — unused attribute in `Manager`

**File:** `src/manejador.py:47`

```python
self.pantalla = 0   # "pantalla" = screen
```

This attribute is written once in `__init__` and never read anywhere in the codebase
(confirmed by grep). It appears to be dead code from an earlier version.

**Options:**
- **Delete** the line (recommended if truly unused).


---

## 4. `handle_magnifier(self, evento)` — parameter reuse in `Pantalla`

**File:** `src/librerias/pantalla.py:254`

The parameter `evento` (the events list) is reused inside the `for` loop as a local boolean:

```python
def handle_magnifier(self, evento):          # evento = list of events
    for event in evento:
        ...
        if event.type == pygame.MOUSEBUTTONDOWN:
            evento = True                    # ← shadows the parameter!
        else:
            evento = False
        if (self.magnifier.rect.collidepoint(...) and ...):
            self.enable = True
            if evento == False:              # ← reads the bool, not the list
                ...
```

**Suggested fix:**
- Rename parameter `evento` → `events`
- Rename the internal bool `evento` → `mouse_down`
- Change `for event in evento:` → `for event in events:`
- Change `if evento == False:` → `if not mouse_down:`

This is a small refactor in addition to a rename — confirm before applying.

---

## 5. `self.active` Button in `actividad1.py`

**File:** `src/paginas/actividad1.py:129`

```python
self.active = Button(830, 60, "active", "Salir", ...)
```

The attribute name `self.active` is the Python attribute for the exit Button widget.
The button's internal ID string is also `"active"` (used in event handling:
`if sprite[0].id == "active": self.parent.popState()`).

The name conflicts with the Python convention of `active` meaning "is active" (boolean).

**Suggested rename:** `self.active` → `self.exit_button`

The button ID string `"active"` in `assets_data.py` does **not** need to change — only the
Python attribute name and the two `self.button_group.add(self.active)` call sites.

Confirm before applying.

---

## 6. `src/interprete/interprete.py` — Blenderplayer module

**File:** `src/interprete/interprete.py`

This module runs inside Blenderplayer (BGE), a separate Python environment with different
imports (`bge`, `mathutils`). It contains several Spanish identifiers:

| Identifier | Location | Meaning | Suggested name |
|---|---|---|---|
| `class Vocabulario` | line 10 | vocabulary lookup | `VocabTable` |
| `def Consultar(self, palabra)` | line 40 | look up a word | `lookup(self, word)` |
| `def consultarcolor(self, color)` | line 53 | look up shirt colour | `lookup_color(self, color)` |
| `class Interprete` | line 67 | sign-language interpreter | `Interpreter` |
| `self.genero` | line 70 | gender (M/F camera) | `self.gender` |
| `self.palabra` | line 71 | the vocabulary word | `self.word` |
| `self.velocidad` | line 73 | animation speed | `self.speed` |
| `self.scena` | line 87 | Blender scene object | `self.scene` |
| `self.controlador` | line 88 | BGE controller | `self.controller` |
| `def Interpretar(self)` | line 107 | play animation + set camera | `def play_sign(self)` |
| `def Repetir(self)` | line 116 | replay animation | `def replay(self)` |
| `def mover_palabra(self)` | line 120 | position word object | `def position_word(self)` |
| `actuador` (local) | line 112 | BGE actuator | `actuator` |

Additionally, `Vocabulario.dic` and `Vocabulario.diccolor` could become `clips` and
`shirt_colors`.

**Note:** `palabra` (local variable inside `mover_palabra`) refers to a Blender scene object
and should stay as-is since it's used as a scene-object key: `self.scena.objects[self.palabra]`.

Please confirm before applying (low-risk file; not imported by any Python screen module).

---

---

## 7. `"inicio"` / `"sig"` / `"active"` button ID strings

**Files affected:** `assets_data.py`, `menucfg.py`, `playground.py`, `pantalla3–6.py`, `pantalla8.py`, `actividad1.py`

Button IDs serve double duty: they are the key in `assets_data.py` AND the Python
attribute name created by `load_buttons()` via `setattr(self, button_id, button)`.
Renaming requires changing both the asset key and all attribute accesses + `sprite.id`
comparisons in event handlers.

| Button ID | Spanish meaning | Used in (attribute) | Used in (id comparison) | Suggested rename |
|---|---|---|---|---|
| `"inicio"` | home/start | `self.inicio` in `menucfg.py`, `playground.py` | `sprite.id == "inicio"` | `"home"` |
| `"sig"` | next (siguiente) | `self.sig` in `pantalla3–6,8.py` | `sprite.id == "sig"` | `"next"` |
| `"active"` | exit (actividad1) | `self.active` in `actividad1.py` | `sprite.id == "active"` | `"exit"` |

Scope of change per button:
- `assets_data.py` — rename the top-level dict key
- `buttons = [...]` list in each screen module
- `self.<id>` attribute references
- `self.x.id == "<id>"` and `sprite[0].id == "<id>"` comparisons

---

## 8. `self.finished` (formerly `self.final`) — possibly dead code

**Files:** `pantalla3.py:72`, `pantalla4.py:89`, `pantalla5.py:112`, `pantalla6.py:86`, `pantalla8.py:86`

`self.finished = False` is set in `resume()` in each of these screens but is never read.
It was likely used in an older version and is now dead code.

**Options:**
- **Delete** the line from all five files (recommended if it truly serves no purpose).

---

## Summary checklist

| # | Item | Suggested action | Status |
|---|---|---|---|
| 1 | `tipo_objeto` + string values | Rename + update all comparisons | Awaiting confirmation |
| 2 | `"texto_act"` / `"caja_texto"` | Rename string literals | Awaiting confirmation |
| 3 | `self.pantalla = 0` | Delete or rename | Awaiting confirmation |
| 4 | `handle_magnifier(evento)` | Rename + extract local bool | Awaiting confirmation |
| 5 | `self.active` Button in actividad1 | See item 7 (`"active"` → `"exit"`) | Awaiting confirmation |
| 6 | `interprete.py` identifiers | Rename (isolated module) | Awaiting confirmation |
| 7 | `"inicio"` / `"sig"` / `"active"` button IDs | Coordinated rename across asset + screen files | Awaiting confirmation |
| 8 | `self.finished` in pantalla3–8 | Delete (possibly dead code) | Awaiting confirmation |
