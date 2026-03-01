# sv2 — Architectural Analysis

This document analyses the current codebase with an eye towards simplification and maintainability. The goal is to identify what is working well, what are genuine anti-patterns, and where the most repetition lives so we can prioritise what to improve first.

---

## What works well

### 1. The game loop and state machine are clean
`inicio.py` is exactly four lines of actual logic. The `Manejador` state stack with `changeState` / `pushState` / `popState` is a solid and well-understood pattern. The lifecycle contract (`start → pause → resume → cleanUp`) is the right idea even if it's not perfectly consistent in implementation.

### 2. Asset data is centralised
`assets_data.py` holds every button, animation, and banner spec in one place. The loader methods on `Pantalla` (`load_buttons`, `load_animations`, `load_banners`) iterate over those specs and do the heavy lifting. Screen files only declare which assets they need, not how to load them. That is a good separation.

### 3. Text content is in JSON
All user-facing Spanish text lives in `content.json`. Text that changes together belongs together, and it gives a single place to make translation or copy edits without touching Python files.

### 4. `TextLoader` is a good accessor
The `get` / `require` / `screen_content` / `concept` / `ui` API is clean. `require` raising a `KeyError` with a readable path is better than a silent `None`. LRU-caching the JSON load in `text_repository.py` is correct.

### 5. `FontManager` caches fonts properly
Font creation is expensive. `FontManager` in `palabra.py` memoises by `(size, bold, underline)` tuples, which avoids creating a new `pygame.font.Font` on every render call.

### 6. Accessibility is first-class
Screen magnifier, TTS / screen reader, keyboard navigation, and configurable font size and character skin colour are all built into the base layer. For a personal project this is genuinely impressive.

### 7. Per-screen sprite groups are now instance-level *(fixed in A)*
Each screen gets its own fresh sprite groups at construction time, eliminating the silent state-sharing bug that corrupted `pushState` scenarios.

### 8. `Configuration` has a clean getter/setter API *(fixed in D, K)*
Dead keys are auto-migrated. `set_preference` only writes to memory; an explicit `flush()` / `save_config()` persists to disk. `mark_screen_visited` still saves immediately (intentional).

### 9. `SpriteSheet` is unified *(fixed in H)*
`librerias/spritesheet.py` is the single source of truth for loading sprite-sheet images. Both `Animation` (multi-row) and `Button` (single-row) import from it.

### 10. Screen-reader navigation uses a polymorphic protocol *(fixed in I)*
`Button`, `palabra`, and `object_mask` each implement `get_reader_text()`. `Pantalla._announce_current()` calls it without a `tipo_objeto` string switch.

---

## Open anti-patterns

### G. `resume()` called from `__init__` — init logic is split in two

**Files:** all `paginas/pantalla*.py`

Every screen's `__init__` ends with `self.resume()`. The `resume()` method re-adds sprites to groups and sets state flags. This means initialisation logic is split across two methods with no clear rule about what belongs where.

The intent seems to be: `resume()` resets the screen to its initial visual state so it can be called both after creation and after returning from a pushed overlay (like the config menu). That is a reasonable idea, but calling it from `__init__` makes `__init__` responsible for setup *and* for calling what is semantically a "return from pause" handler.

The base class also has an empty `start()` that is never called by anything meaningful, and an empty `cleanUp()`. The contract of `start` / `pause` / `resume` / `cleanUp` is informally documented but not enforced.

**Fix:** Distinguish what is one-time setup (belongs in `__init__`) from what is "return to ready state" (belongs in `resume`). Do not call `resume` from `__init__`; call it from `start` instead, which `Manejador.changeState` already invokes.

---

### J. `assets_data.py` exported via `import *`

**Files:** `librerias/pantalla.py`, `librerias/assets_data.py`

```python
from librerias.assets_data import *
```

This dumps `backgrounds`, `banners`, `images`, `animations`, `buttons`, `popups` into the `pantalla` module namespace. The name `buttons` in `assets_data` collides conceptually (though not technically) with the `buttons` list defined in every screen module. `animations` and `images` are generic names. There's also no schema validation — a mistyped key in a screen file fails at runtime when the screen is loaded, not at startup.

**Fix:** Import the dicts explicitly by name, or wrap them in a namespace object. Consider validating that every key referenced by screens exists in the data at startup.

---

### L. Glossary vocabulary hardcoded in Python

**Files:** `librerias/palabra.py`

```python
class palabra(pygame.sprite.Sprite):
    ENTRIES = {
        "absorbe": "absorber",
        "célula": "celula",
        ...
    }
    DEFINITIONS = {
        "Absorber": "absorber",
        ...
    }
```

These two dicts are the vocabulary index — which words in the flowing text are clickable, and which words appear in the glossary index. They belong in `content.json` alongside the concept definitions they point to. Having them in Python means adding a new concept requires editing both a Python file and the JSON.

**Fix:** Move `ENTRIES` and `DEFINITIONS` into `content.json` under a `"glossary"` key. Load them at startup through `TextLoader`.

---

### N. `Manejador.interpretar()` does two unrelated things

**Files:** `manejador.py`

Half of `interpretar()` launches `blenderplayer` (a legacy 3D application from a discontinued Blender game engine). The other half navigates to the in-app glossary screen. These are completely different code paths that should be separate methods.

The Blenderplayer branch also contains a check for a Python 3.2 bytecode cache file (`cpython-32.pyc`), which is a historical artefact from when the project ran on Python 2/3.2.

**Fix:** Split into `launch_interpreter(codigo)` and `show_glossary(codigo)`. Remove the Python 3.2 cache check.

---

### O. Accessibility config screens use a defunct `Configuration` API

**Files:** `paginas/menuauditivo.py`, `paginas/menuvisual.py`

Both screens pre-date the `Configuration` refactor and still call methods and attributes that no longer exist. **These screens will crash at runtime.** Enumerated failures:

**Methods that were removed:**
- `self.parent.config.consultar()` — ×3 in `menuauditivo`, ×2 in `menuvisual`
- `self.parent.config.cargar_default()` — ×1 in `menuauditivo`
- `self.parent.config.guardar_preferencias()` — ×1 in `menuauditivo`, ×2 in `menuvisual`

**Direct attribute reads/writes that bypass the new API:**
- `.cache` (dead attribute — now a preference key, not a direct attribute)
- `.disc_audi` — ×6 in `menuauditivo`
- `.genero` — ×4 in `menuauditivo`
- `.color` — ×6 in `menuauditivo`
- `.velocidad` — ×1 in `menuauditivo`
- `.ubx` — ×1 in `menuauditivo`
- `.synvel` — ×8 in `menuvisual`
- `.preferencias["t_fuente"]` — ×2 in `menuvisual` (raw dict access, violates API)

**Wrong method used as condition:**
- `menuvisual.py` line 206: `if self.parent.config.set_screen_reader_enabled(True):` — a setter used as a boolean condition; should be `is_screen_reader_enabled()`.

**Fix:** Replace every removed method and direct attribute with the corresponding new API:
- `consultar()` → remove (config is already in-memory; re-loading from disk is unnecessary)
- `cargar_default()` → `update_preferences(config.get_default_config())`
- `guardar_preferencias()` → `flush()` (or `save_config()`)
- Direct attribute writes (`.disc_audi = x`, `.genero = x`, etc.) → `set_preference("disc_audi", x)` etc.
- `.preferencias["t_fuente"]` → `get_font_size()` or `get_preference("t_fuente")`
- `.cache = True` → `set_preference("cache", True)` (then `flush()` at save time)

---

### P. Glossary screen (`pantalla10`) uses stale `palabra` attribute names

**Files:** `paginas/pantalla10.py`

`pantalla10.py` is the in-app glossary screen. It interacts directly with `palabra` sprite objects and uses the old attribute and method names that were renamed during the `palabra` refactor. **This screen will crash when a user clicks a glossary entry.**

Stale API usage (all at the `sprite[0]` level):
- `.definible` → should be `.definable`
- `.definicion` → should be `.definition`
- `.selec = True` → should be `.selected = True`
- `.destacar()` → should be `.highlight()`
- `.restaurar()` → should be `.restore()`
- `.negrita()` → **method removed with no direct equivalent**; the new `update(2)` + `render()` flow handles bold-on-selection automatically via `selected` flag
- `.palabra` (as text string) → should be `.text`
- `.codigo` → already correct (`.code` is the new name, but `.codigo` was the old one — verify which is current)

**Fix:** Update every stale call in `pantalla10.py` to the current `palabra` API. For `.negrita()`, remove the explicit call; setting `sprite[0].selected = True` before `render()` (or `highlight()`) achieves the same visual result via the new render path.

---

### Q. `popups.py` uses stale `Text` attribute

**Files:** `librerias/popups.py`

`PopUp.__init__` and at least one other location reference `txt.ancho_final` — an attribute that was renamed `total_height` during the `texto.py` refactor. Any screen that loads a popup will crash at construction time.

**Fix:** Replace `txt.ancho_final` → `txt.total_height` in `popups.py`.

---

## Priority order for remaining work

1. **O — Fix accessibility config screens** (`menuauditivo`, `menuvisual`): critical path for every new user setting up the app. ~25 mechanical substitutions, no logic changes.

2. **P — Fix glossary screen** (`pantalla10`): the in-app dictionary is entirely broken. ~10 attribute/method renames.

3. **Q — Fix `popups.py`** stale attribute: causes a crash on any screen that shows a popup. Quick single-line fix.

4. **L — Move glossary vocabulary to JSON**: content addition no longer requires touching Python.

5. **G — Fix `resume()`/`start()` split**: clean up screen lifecycle.

6. **J — Replace `import *` for assets**: explicit imports + optional startup validation.

7. **N — Split `interpretar()`**: separate Blenderplayer launch from glossary navigation.

---

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
