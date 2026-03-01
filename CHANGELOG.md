## Changelog

Improvements applied so far, in chronological order.

---

### ✅ B — Singleton metaclass fixed to Python 3 syntax *(2026-02)*

**Files changed:** `manejador.py`

`class Manejador(object)` with the dead `__metaclass__ = Singleton` (Python 2 syntax, silently ignored in Python 3) was replaced with `class Manejador(metaclass=Singleton)`. The Singleton metaclass in `singleton.py` was already correct; only the class declaration was wrong.

Two additional bugs fixed in the same pass:
- The `icon = pygame.image.load(...)` and `pygame.display.set_icon(icon)` lines were sitting loose in the class body, executing at import time before `pygame.init()`. Moved into `__init__` immediately after `pygame.init()`.
- `manejador.draw()` called `self.states[-1].reloj.tick(30)`, but `reloj` was the dead class attribute removed in fix A. Updated to `reloj_anim`, the per-screen clock already initialised in `Pantalla.__init__`.

---

### ✅ C — `Button` no longer imports `Manejador` as its parent *(2026-02)*

**Files changed:** `librerias/button.py`, `librerias/pantalla.py`

`Button.__init__` used `from manejador import Manejador as parent` and `self.parent = parent` (the *class*, not an instance) solely to read `self.parent.config.get_font_size()` for the tooltip font. The import and the `self.parent` assignment are gone. A `font_size` parameter was added to `Button.__init__`, and `Pantalla.load_buttons()` now reads `self.parent.config.get_font_size()` once and forwards it to every `Button` it constructs. Data now flows explicitly instead of through a hidden class-level back-channel.

---

### ✅ A — Class-level mutable state moved into `__init__` *(2026-02)*

**Files changed:** `librerias/pantalla.py`

All mutable sprite groups (`grupo_anim`, `grupo_botones`, `grupo_banner`, `grupo_palabras`, etc.), navigation lists (`lista_final`, `lista_botones`, `lista_palabra`), and per-screen flags (`x`, `elemento_actual`, `enable`, `entrada_primera_vez`, `deteccion_movimiento`) were moved from class attributes into `Pantalla.__init__`. Each screen instance now gets its own fresh groups, eliminating the silent state-sharing bug that would corrupt `pushState` scenarios.

Three intentionally shared resources remain as class attributes with an explanatory comment: `spserver` (TTS server process), `raton` (cursor sprite), and `obj_magno` (magnifier — preserving zoom level across screen transitions). The dead `reloj = pygame.time.Clock()` class attribute was also removed.

`debug_groups` is now built in `__init__` from the instance groups, so debug overlays correctly reflect the current screen's own sprite groups.

---

### ✅ E + F — Standardised text loading across all screens *(2026-02)*

**Files changed:** `librerias/pantalla.py`, `paginas/pantalla3–6,8–11.py`

Two problems were solved together:

- **E (two text-access styles):** All raw `self.parent.text_content["content"][self.name]["key"]` lookups were replaced with `self.screen_text("key")`, a thin wrapper around `text_loader.get()` added to `Pantalla`. Every screen now goes through `TextLoader` consistently.

- **F (cargar_textos boilerplate):** `Pantalla` gained a `load_screen_texts(keys, x, y, text_type, right_limit, custom)` helper that builds a `{key → Text}` dict in one call. Screens that had uniform `Text(...)` constructors (pantalla3, 4, 5, 6, 8) now use it. Screens with chained-y layout (pantalla9, 11) keep their explicit `Text(...)` calls but still benefit from `screen_text()` for all their string lookups.

---

### ✅ K — Dead config keys removed *(2026-02)*

**Files changed:** `librerias/configuration.py`

`texto_cambio` and `visit` removed from `Configuration.get_default_config()`. A `_migrate()` method was added and called from `__init__` so that any existing saved file has these keys stripped on first load, and the cleaned file is written back immediately.

---

### ✅ M — Named layout constants in `texto.py` *(2026-02)*

**Files changed:** `librerias/texto.py`

Six module-level constants replaced all magic pixel numbers:

```python
_MEASURE_LEFT      = 128        # left edge used when estimating line count
_MEASURE_RIGHT     = 896        # right edge used when estimating line count
_LAYOUT_1LINE      = (256, 768) # (left, right) margins for single-line text
_LAYOUT_2LINE      = (192, 832) # margins for two-line text
_LAYOUT_3PLUS      = (32,  992) # margins for three-or-more lines
_TEXT_AREA_VCENTER = 382        # vertical midpoint of the on-screen text area
```

---

### ✅ D — Configuration no longer auto-saves on every key write *(2026-02)*

**Files changed:** `librerias/configuration.py`

`set_preference()` previously called `save_config()` after every single key update, triggering a synchronous full-file JSON write for each individual setting change. The save call was removed; `set_preference` now only updates the in-memory dict and sets `self.changed = True`. `save_config()` now resets the dirty flag when it writes.

A `flush()` convenience method was added as an explicit save shorthand. The two call sites that should still save immediately are unchanged: `mark_screen_visited()` (screen visits are always persisted right away) and `update_preferences()` (its explicit purpose is a batch in-memory update followed by a single disk write).

---

### ✅ H — Duplicate `SpriteSheet` classes consolidated *(2026-02)*

**Files changed:** `librerias/spritesheet.py` (new), `librerias/animations.py`, `librerias/button.py`

`librerias/animations.py` had a `spritesheet` class and `librerias/button.py` had a `SpriteSheet` class — both loading sprite-sheet images and extracting frames, with nearly identical `image_at` and `images_at` implementations but different `load_strip` signatures (animations supported multi-row sheets; buttons only needed single-row).

A single `SpriteSheet` class was created in `librerias/spritesheet.py` with a unified `load_strip(rect, image_count, rows=1, row=0, colorkey=None)` signature. The `rows`/`row` parameters default to single-row behaviour, preserving backward compatibility for Button's call site (which now passes `colorkey` as a keyword argument). Both `animations.py` and `button.py` now import from the shared module and their local class definitions are gone.

A regression was also fixed: `button.py`'s import cleanup had accidentally dropped `from pygame.image import load`, which is still used by `TextButton`. The import was restored.

---

### ✅ I — `tipo_objeto` string dispatch deduplicated *(2026-02)*

**Files changed:** `librerias/pantalla.py`, `librerias/palabra.py`, `librerias/button.py`, `librerias/objmask.py`, `librerias/texto.py`

`controlador_lector_evento_K_RIGHT` and `controlador_lector_evento_K_LEFT` each contained an identical three-branch `if/elif tipo_objeto` block that called `definir_rect` then `spserver.processtext` with a different attribute depending on the object type. Three problems in one: duplicated logic, stale attribute names (`.palabra` instead of `.text`, `.tt` instead of `.tooltip`), and `tipo_objeto` was not even set on `Button` or `palabra` objects so the check would `AttributeError` at runtime.

**Changes:**
- `palabra.__init__` now sets `self.tipo_objeto = "palabra"` and gains `get_reader_text()` returning `"explicar la palabra:" + self.text`.
- `Button.__init__` now sets `self.tipo_objeto = "boton"` and gains `get_reader_text()` returning `self.tooltip`.
- `object_mask` gains `get_reader_text()` returning `self.id` (already had `tipo_objeto = "mapa"`).
- `Pantalla` gains a private `_announce_current()` helper that calls `self.x.get_reader_text()` — the entire `if/elif` dispatch is gone.
- Both `controlador_lector_evento_K_RIGHT` and `controlador_lector_evento_K_LEFT` now end with a single `self._announce_current()` call.
- `texto.py`'s `indexar()` was updated to use the current `palabra` attribute names (`word.text`, `word.selected`, `word.highlight()`, `word.restore()`) replacing the stale `word.palabra`, `word.selec`, `word.destacar()`, `word.restaurar()`.

---

### ✅ G — `resume()` no longer called from `__init__` *(2026-03)*

**Files changed:** `paginas/pantalla2–6,8–9.py`, `paginas/menucfg.py`, `paginas/playground.py`

Every screen's `__init__` used to end with `self.resume()`, causing init logic to span two methods with no clear ownership boundary. Screen construction now ends cleanly; `start()` (which `Manejador.changeState` already calls on every new state) is the single entry point into `resume()`:

```python
def start(self):
    self.resume()
```

`playground.py` already had a `def start(self): pass` stub; its body was replaced with `self.resume()`.

---

### ✅ J — `assets_data.py` imported explicitly *(2026-03)*

**Files changed:** `librerias/pantalla.py`

The `from librerias.assets_data import *` wildcard was replaced with five explicit named imports using private-prefixed aliases:

```python
from librerias.assets_data import (
    backgrounds as _backgrounds,
    banners     as _banners,
    images      as _images,
    animations  as _animations,
    buttons     as _buttons,
)
```

The `popups` dict (also exported by `assets_data`) is not used by any `Pantalla` load method and was not imported. All five load methods (`load_animations`, `load_background`, `load_buttons`, `load_banners`, `load_images`) were updated to reference the new names.

---

### ✅ L — Glossary vocabulary moved to JSON *(2026-03)*

**Files changed:** `librerias/palabra.py`, `paginas/text/content.json`, `manejador.py`

`palabra.ENTRIES`, `DEFINITIONS`, `INDICES`, and `INTERCALATED` were 36-line hardcoded class-level dicts. They now live in `content.json` under a `"glossary"` key:

```json
"glossary": {
  "entries":       { "absorbe": "absorber", "célula": "celula", ... },
  "definitions":   { "Absorber": "absorber", "Célula": "celula", ... },
  "indices":       ["A", "C", "F", "G", "M", "N", "O", "R", "T"],
  "intercalated":  ["RATON", "DIR", "ENTER"]
}
```

`palabra.py` now declares the four attributes as empty-default class attributes with a comment. `Manejador.load_text_content()` injects the live values via a local import (to avoid a circular-import chain):

```python
from librerias.palabra import palabra as Palabra
Palabra.ENTRIES      = glossary.get("entries", {})
Palabra.DEFINITIONS  = glossary.get("definitions", {})
Palabra.INDICES      = glossary.get("indices", [])
Palabra.INTERCALATED = glossary.get("intercalated", [])
```

---

### ✅ N — `interpretar()` split into focused methods *(2026-03)*

**Files changed:** `manejador.py`

`Manejador.interpretar(codigo)` was a single method that did two unrelated things depending on `config.disc_audi`. It is now a three-method group:

- `interpretar(codigo)` — thin dispatcher; reads `get_preference("disc_audi", False)`.
- `_launch_interpreter(codigo)` — launches the Blenderplayer sign-language interpreter subprocess. Reads `color`, `genero`, and `velocidad` via `get_preference()`. Dead Python 3.2 bytecode cache cleanup (`os.path.isdir("__pycache__")` block) removed. `import os` removed.
- `_show_glossary(codigo)` — writes `definicion` via `set_preference()`, then calls the current screen's `ir_glosario()`.

---

### ✅ Q — `popups.py` stale `ancho_final` attribute fixed *(2026-03)*

**Files changed:** `librerias/popups.py`

`PopUp.__init__` referenced `self.texto.ancho_final` (renamed `total_height` in the `texto.py` refactor) in the `tipo == 0` and `tipo == 1` branches — any screen loading a popup would crash at construction. The four affected call sites were updated to `self.texto.total_height`.

The `tipo == 2` branch (which uses a `texto2` instance, not a `Text` instance) was intentionally left unchanged: `texto2` still exposes `ancho_final` under its own API.

---

### ✅ O — Accessibility config screens updated to current Configuration API *(2026-03)*

**Files changed:** `paginas/menuauditivo.py`, `paginas/menuvisual.py`

Both screens pre-dated the `Configuration` refactor and used removed methods and direct attribute access. Without this fix they crashed at runtime as soon as a user entered either config screen.

**`menuauditivo.py`** (~25 sites):
- Removed `consultar()` (×2) and `cargar_default()` (×1)
- Replaced `.cache`, `.disc_audi`, `.genero`, `.color`, `.velocidad`, `.ubx` reads with `get_preference(key, default)`
- Replaced the same attribute writes with `set_preference(key, value)`
- Replaced `.preferencias["t_fuente"]` with `get_preference("t_fuente", 18)`
- Replaced `guardar_preferencias()` with `flush()`

**`menuvisual.py`** (~17 sites):
- Removed `consultar()` (×3)
- Fixed `if config.set_screen_reader_enabled(True):` (setter used as condition) → `if config.is_screen_reader_enabled():`
- Replaced `.synvel` reads (×5) with `get_preference("synvel", "baja") == "..."`
- Replaced `.synvel` writes (×6) with `set_preference("synvel", "...")`
- Replaced bare `config.enable_magnifier` / `config.disable_magnifier` property no-ops with `set_preference("magnificador", True/False)`
- Removed stale `synvel` rollback block in the `oflector` handler (replaced with a comment)
- Replaced `.preferencias["t_fuente"]` (×2) with `get_preference("t_fuente", 18)`
- Replaced `guardar_preferencias()` (×2) with `flush()`

---

### ✅ P — Glossary screen updated to current `palabra` API *(2026-03)*

**Files changed:** `paginas/pantalla10.py`

`pantalla10.py` is the in-app glossary. It used the old `palabra` attribute and method names from before the `palabra` refactor. Without this fix, clicking any glossary entry crashed the screen.

Changes made:
- `config.definicion` (×3) → `config.get_preference("definicion", "")`
- `self.concepto.ancho_final` (×2) → `self.concepto.total_height`
- `.definible` → `.definable`
- `.definicion ==` → `.definition ==`
- `.selec = True/False` (×3) → `.selected = True/False`
- `.destacar()` → `.highlight()`
- `.negrita()` (×2) → deleted (bold-on-selection is now automatic via the `selected` flag in the new render path)
- `sprite[0].palabra` / `i.words[0].palabra` → `.text`
- `sprite[0].codigo` / `i.words[0].codigo` → `.code`
