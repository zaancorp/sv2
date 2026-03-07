## Changelog

Improvements applied so far, in reverse chronological order.

---

### ✅ SV2-031 — Directory and module rename: `librerias/` → `components/` *(2026-03)*

**Files changed:** all source files

The `librerias/` package was renamed to `components/` and several module files were given English names: `pantalla.py` → `screen.py`, `cajatexto.py` → `textbox.py`, `personaje.py` → `character.py`, `limite.py` → `boundary.py`, `marcador.py` → `marker.py`, `contador.py` → `counter.py`, `palabra.py` → `words.py`. All internal imports updated. No functional change.

---

### ✅ SV2-030 — `self.text = str` assigns the type object, not an empty string *(2026-03)*

**Files changed:** `components/textbox.py`

`TextBox.__init__` set `self.text = str`, assigning the built-in `str` class itself to the attribute rather than an empty string. Any call to `self.text.lower()` or `return self.text` on a fresh instance would operate on the type object. Fixed to `self.text = ""`.

---

### ✅ SV2-029 — `canal.get_busy` missing call parentheses *(2026-03)*

**Files changed:** `components/button.py`

`Button.play_sound` tested `canal.get_busy` as a boolean condition. A bound method is always truthy, so the channel-busy check never worked and hover sounds never played. Fixed to `canal.get_busy()`.

---

### ✅ SV2-027 — Dead circular import in `speechserver.py` *(2026-03)*

**Files changed:** `components/speechserver.py`

`speechserver.py` had a module-level `from manejador import Manager as parent`. The name `parent` was only referenced in code that was entirely commented out, making the import purposeless. More critically it created the circular chain `screen.py → speechserver.py → manejador.py → screen.py`, which would cause an `ImportError` under certain import orders. The line was deleted.

---

### ✅ SV2-026 — `has_visited_screen("p2")` condition inverted in `pantalla2.py` *(2026-03)*

**Files changed:** `paginas/pantalla2.py`

The `if/else` branches were swapped: the TTS announcement `"Menú del Recurso"` was firing on every *revisit* (when `has_visited_screen` returned `True`) and was silent on the *first* visit. The `mark_screen_visited` call in the `if` branch was also redundant since the screen was already marked. Fixed to `if not has_visited_screen(…)` with `mark_screen_visited` and TTS in the same (now correct) branch.

---

### ✅ SV2-025 — Dead config key `"texto_cambio"` always returned `True` *(2026-03)*

**Files changed:** `paginas/pantalla2.py`

`pantalla2.resume()` called `get_preference("texto_cambio", True)` and `set_preference("texto_cambio", False)`. The key `texto_cambio` was removed from `user_config.json` in SV2-011; `get_preference` therefore always returned the hardcoded default `True`, permanently disabling the font-reload optimisation. Replaced with the live API: `is_text_change_enabled()` / `set_text_change_enabled(False)`.

---

### ✅ SV2-024 — Bare `except:` in `Manejador._launch_interpreter` *(2026-03)*

**Files changed:** `manejador.py`

The `subprocess.Popen` call for Blenderplayer was wrapped in a bare `except:`, which silently swallowed `KeyboardInterrupt`, `SystemExit`, and any other exception. Changed to `except OSError:` so only file/process errors are caught and all other exceptions propagate normally.

---

### ✅ SV2-022 — `get_preference("definicion", "")[0]` crashes on fresh install *(2026-03)*

**Files changed:** `paginas/pantalla10.py`

On first launch the `"definicion"` key is absent and `get_preference` returns the default `""`. Indexing an empty string with `[0]` raised `IndexError`, crashing the glossary screen before it could render. Added an explicit empty-string guard: `inicial = _def[0].upper() if _def else ""`.

---

### ✅ SV2-021 — `TextButton` used the renamed attribute `txt.final_width` *(2026-03)*

**Files changed:** `components/button.py`

`TextButton.__init__` (the `background=1` path) constructed a `Text` object and read `txt.final_width` to size the button surface. The attribute was renamed `total_height` during an earlier refactor; `txt.final_width` raised `AttributeError` on every `TextButton(background=1)` construction. Fixed to `txt.total_height`.

---

### ✅ SV2-020 — Missing `.config.` on `set_text_change_enabled` calls *(2026-03)*

**Files changed:** `paginas/menuauditivo.py`, `paginas/menuvisual.py`

Three call sites called `self.parent.set_text_change_enabled(True)`. `set_text_change_enabled` is a method on `Configuration`, not on `Manager`. All three raised `AttributeError` the moment the user saved a preference that triggered the font-change flag. Fixed to `self.parent.config.set_text_change_enabled(True)`.

---

### ✅ SV2-019 — Empty `Text("")` crashed `_layout_words` *(2026-03)*

**Files changed:** `components/texto.py`

`_layout_words` iterated `self.words` and ended with `return max_width, total_height + word.rect.height`. When the input string was empty, `self.words` was `[]`, the loop body never ran, `word` was never bound, and the `return` raised `UnboundLocalError`. `_estimate_total_height` similarly raised `IndexError` on `self.words[0]`. Added early-return guards: `_layout_words` returns `(0, 0)` and `_estimate_total_height` returns `0` for empty word lists.

---

### ✅ SV2-018 — `TextType` enum rejected all string `text_type` values *(2026-03)*

**Files changed:** `components/words.py`

`Word.__init__` converted its `text_type` argument with `TextType(text_type)`. `TextType` is an `Enum` with integer values 1–8. Every caller in the codebase passed a string (`"definicion"`, `"indice"`, `"concepto"`, `"active_text"`, etc.); `TextType("definicion")` raised `ValueError`, making it impossible to create any `Word` sprite from string-typed `Text` objects.

Added a `_TEXT_TYPE_NAMES` module-level dict mapping every string name to its `TextType` member. `Word.__init__` now accepts strings (looked up in the dict), `TextType` members (passed through), or integers (converted via `TextType(int)`).

---

### ✅ SV2-017 — `popups.py` stale `ancho_final` attribute *(2026-03)*

**Files changed:** `components/popups.py`

`PopUp.__init__` referenced `self.texto.ancho_final` (renamed `total_height` in the `texto.py` refactor) in the `tipo == 0` and `tipo == 1` branches — any screen loading a popup would crash at construction. The four affected call sites were updated to `self.texto.total_height`.

The `tipo == 2` branch (which uses a `texto2` instance, not a `Text` instance) was intentionally left unchanged: `texto2` still exposes `ancho_final` under its own API.

---

### ✅ SV2-016 — Glossary screen updated to current `Word` API *(2026-03)*

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

---

### ✅ SV2-015 — Accessibility config screens updated to current Configuration API *(2026-03)*

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

### ✅ SV2-014 — `interpretar()` split into focused methods *(2026-03)*

**Files changed:** `manejador.py`

`Manejador.interpretar(codigo)` was a single method that did two unrelated things depending on `config.disc_audi`. It is now a three-method group:

- `show_concept(codigo)` — thin dispatcher; reads `get_preference("disc_audi", False)`.
- `_launch_interpreter(codigo)` — launches the Blenderplayer sign-language interpreter subprocess. Reads `color`, `genero`, and `velocidad` via `get_preference()`. Dead Python 3.2 bytecode cache cleanup (`os.path.isdir("__pycache__")` block) removed. `import os` removed.
- `_show_glossary(codigo)` — writes `definicion` via `set_preference()`, then calls the current screen's `go_to_glossary()`.

---

### ✅ SV2-013 — Named layout constants in `texto.py` *(2026-02)*

**Files changed:** `components/texto.py`

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

### ✅ SV2-012 — Glossary vocabulary moved to JSON *(2026-03)*

**Files changed:** `components/words.py`, `paginas/text/content.json`, `manejador.py`

`Word.ENTRIES`, `DEFINITIONS`, `INDICES`, and `INTERCALATED` were 36-line hardcoded class-level dicts. They now live in `content.json` under a `"glossary"` key:

```json
"glossary": {
  "entries":       { "absorbe": "absorber", "célula": "celula", ... },
  "definitions":   { "Absorber": "absorber", "Célula": "celula", ... },
  "indices":       ["A", "C", "F", "G", "M", "N", "O", "R", "T"],
  "intercalated":  ["RATON", "DIR", "ENTER"]
}
```

`words.py` now declares the four attributes as empty-default class attributes. `Manejador.load_text_content()` injects the live values via a local import (to avoid a circular-import chain).

---

### ✅ SV2-011 — Dead config keys removed *(2026-02)*

**Files changed:** `components/configuration.py`

`texto_cambio` and `visit` removed from `Configuration.get_default_config()`. A `_migrate()` method was added and called from `__init__` so that any existing saved file has these keys stripped on first load, and the cleaned file is written back immediately.

---

### ✅ SV2-010 — `assets_data.py` imported explicitly *(2026-03)*

**Files changed:** `components/screen.py`

The `from assets_data import *` wildcard was replaced with five explicit named imports using private-prefixed aliases:

```python
from components.assets_data import (
    backgrounds as _backgrounds,
    banners     as _banners,
    images      as _images,
    animations  as _animations,
    buttons     as _buttons,
)
```

The `popups` dict (also exported by `assets_data`) is not used by any `Screen` load method and was not imported. All five load methods (`load_animations`, `load_background`, `load_buttons`, `load_banners`, `load_images`) were updated to reference the new names.

---

### ✅ SV2-009 — `obj_type` string dispatch deduplicated *(2026-02)*

**Files changed:** `components/screen.py`, `components/words.py`, `components/button.py`, `components/object.py`, `components/texto.py`

`nav_right` and `nav_left` each contained an identical three-branch `if/elif obj_type` block that called `define_rect` then `speech_server.processtext` with a different attribute depending on the object type. Three problems in one: duplicated logic, stale attribute names (`.palabra` instead of `.text`, `.tt` instead of `.tooltip`), and `obj_type` was not even set on `Button` or `Word` objects so the check would `AttributeError` at runtime.

**Changes:**
- `Word.__init__` now sets `self.obj_type = "word"` and gains `get_reader_text()` returning `"explain word:" + self.text`.
- `Button.__init__` now sets `self.obj_type = "button"` and gains `get_reader_text()` returning `self.tooltip`.
- `PropObject` gains `get_reader_text()` returning `self.id` (already had `obj_type = "map"`).
- `Screen` gains a private `_announce_current()` helper that calls `self.x.get_reader_text()` — the entire `if/elif` dispatch is gone.
- Both `nav_right` and `nav_left` now end with a single `self._announce_current()` call.
- `texto.py`'s `indexar()` was updated to use the current `Word` attribute names (`word.text`, `word.selected`, `word.highlight()`, `word.restore()`).

---

### ✅ SV2-008 — Duplicate `SpriteSheet` classes consolidated *(2026-02)*

**Files changed:** `components/spritesheet.py` (new), `components/animations.py`, `components/button.py`

`animations.py` had a `spritesheet` class and `button.py` had a `SpriteSheet` class — both loading sprite-sheet images and extracting frames, with nearly identical `image_at` and `images_at` implementations but different `load_strip` signatures.

A single `SpriteSheet` class was created in `components/spritesheet.py` with a unified `load_strip(rect, image_count, rows=1, row=0, colorkey=None)` signature. The `rows`/`row` parameters default to single-row behaviour, preserving backward compatibility for Button's call site. Both `animations.py` and `button.py` now import from the shared module.

---

### ✅ SV2-007 — `resume()` no longer called from `__init__` *(2026-03)*

**Files changed:** `paginas/pantalla2–6,8–9.py`, `paginas/menucfg.py`, `paginas/playground.py`

Every screen's `__init__` used to end with `self.resume()`, causing init logic to span two methods with no clear ownership boundary. Screen construction now ends cleanly; `start()` (which `Manejador.changeState` already calls on every new state) is the single entry point into `resume()`:

```python
def start(self):
    self.resume()
```

---

### ✅ SV2-006 — `cargar_textos` boilerplate consolidated *(2026-02)*

**Files changed:** `components/screen.py`, `paginas/pantalla3–6,8.py`

`Screen` gained a `load_screen_texts(keys, x, y, text_type, right_limit, custom)` helper that builds a `{key → Text}` dict in one call. Screens that had uniform `Text(...)` constructors now use it. Screens with chained-y layout (pantalla9, 11) keep their explicit `Text(...)` calls but still benefit from `screen_text()` for all their string lookups.

---

### ✅ SV2-005 — Two text-access styles unified *(2026-02)*

**Files changed:** `components/screen.py`, `paginas/pantalla3–6,8–11.py`

All raw `self.parent.text_content["content"][self.name]["key"]` lookups were replaced with `self.screen_text("key")`, a thin wrapper around `text_loader.get()` added to `Screen`. Every screen now goes through `TextLoader` consistently.

---

### ✅ SV2-004 — Configuration no longer auto-saves on every key write *(2026-02)*

**Files changed:** `components/configuration.py`

`set_preference()` previously called `save_config()` after every single key update, triggering a synchronous full-file JSON write for each individual setting change. The save call was removed; `set_preference` now only updates the in-memory dict and sets `self.changed = True`. `save_config()` now resets the dirty flag when it writes.

A `flush()` convenience method was added as an explicit save shorthand. The two call sites that should still save immediately are unchanged: `mark_screen_visited()` (screen visits are always persisted right away) and `update_preferences()` (its explicit purpose is a batch in-memory update followed by a single disk write).

---

### ✅ SV2-003 — `Button` no longer imports `Manejador` as its parent *(2026-02)*

**Files changed:** `components/button.py`, `components/screen.py`

`Button.__init__` used `from manejador import Manejador as parent` and `self.parent = parent` (the *class*, not an instance) solely to read `self.parent.config.get_font_size()` for the tooltip font. The import and the `self.parent` assignment are gone. A `font_size` parameter was added to `Button.__init__`, and `Screen.load_buttons()` now reads `self.parent.config.get_font_size()` once and forwards it to every `Button` it constructs. Data now flows explicitly instead of through a hidden class-level back-channel.

---

### ✅ SV2-002 — Singleton metaclass fixed to Python 3 syntax *(2026-02)*

**Files changed:** `manejador.py`

`class Manejador(object)` with the dead `__metaclass__ = Singleton` (Python 2 syntax, silently ignored in Python 3) was replaced with `class Manejador(metaclass=Singleton)`. The Singleton metaclass in `singleton.py` was already correct; only the class declaration was wrong.

Two additional bugs fixed in the same pass:
- The `icon = pygame.image.load(...)` and `pygame.display.set_icon(icon)` lines were sitting loose in the class body, executing at import time before `pygame.init()`. Moved into `__init__` immediately after `pygame.init()`.
- `manejador.draw()` called `self.states[-1].reloj.tick(30)`, but `reloj` was the dead class attribute removed in SV2-001. Updated to `reloj_anim`, the per-screen clock already initialised in `Screen.__init__`.

---

### ✅ SV2-001 — Class-level mutable state moved into `__init__` *(2026-02)*

**Files changed:** `components/screen.py`

All mutable sprite groups (`anim_group`, `button_group`, `banner_group`, `word_group`, etc.), navigation lists, and per-screen flags were moved from class attributes into `Screen.__init__`. Each screen instance now gets its own fresh groups, eliminating the silent state-sharing bug that would corrupt `pushState` scenarios.

Three intentionally shared resources remain as class attributes with an explanatory comment: `speech_server` (TTS server process), `mouse` (cursor sprite), and `magnifier` (magnifier — preserving zoom level across screen transitions). The dead `clock = pygame.time.Clock()` class attribute was also removed.

`debug_groups` is now built in `__init__` from the instance groups, so debug overlays correctly reflect the current screen's own sprite groups.
