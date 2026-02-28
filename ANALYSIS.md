# sv2 — Architectural Analysis

This document analyses the current codebase with an eye towards simplification and maintainability. The goal is to identify what is working well, what are genuine anti-patterns, and where the most repetition lives so we can prioritise what to improve first.

---

## What works well

### 1. The game loop and state machine are clean
`inicio.py` is exactly four lines of actual logic. The `Manejador` state stack with `changeState` / `pushState` / `popState` is a solid and well-understood pattern. The lifecycle contract (`start → pause → resume → cleanUp`) is the right idea even if it's not perfectly consistent in implementation.

### 2. Asset data is centralised
`assets_data.py` holds every button, animation, and banner spec in one place. The loader methods on `Pantalla` (`load_buttons`, `load_animations`, `load_banners`) iterate over those specs and do the heavy lifting. Screen files only declare which assets they need, not how to load them. That is a good separation.

### 3. Text content is in JSON
Moving all user-facing Spanish text to `content.json` was the right call. Text that changes together belongs together, and it gives a single place to make translation or copy edits without touching Python files.

### 4. `TextLoader` is a good accessor
The `get` / `require` / `screen_content` / `concept` API is clean. `require` raising a `KeyError` with a readable path is better than a silent `None`. LRU-caching the JSON load in `text_repository.py` is correct.

### 5. `FontManager` caches fonts properly
Font creation is expensive. `FontManager` in `palabra.py` memoises by `(size, bold, underline)` tuples, which avoids creating a new `pygame.font.Font` on every render call.

### 6. Accessibility is first-class
Screen magnifier, TTS / screen reader, keyboard navigation, and configurable font size and character skin colour are all built into the base layer. For a personal project this is genuinely impressive.

---

## Anti-patterns and areas for improvement

These are ordered roughly from most impactful to least.

---

### A. Class-level mutable state on `Pantalla` — shared between all screens

**Files:** `librerias/pantalla.py`

Every sprite group, every list, and several flags are defined as *class* attributes on `Pantalla`:

```python
class Pantalla(object):
    grupo_anim = RenderAnim()
    grupo_botones = RenderButton()
    lista_final = []
    lista_botones = []
    lista_palabra = []
    entrada_primera_vez = True
    elemento_actual = -1
    ...
```

In Python, mutable class attributes are shared by every instance. This means every screen object shares the exact same `grupo_anim`, the same `lista_final`, etc. The only reason the app does not visibly break is that there is almost never more than one screen alive at once, and `limpiar_grupos()` empties everything before a new screen starts.

This is fragile. Any time two screens coexist (e.g. via `pushState` for the config overlay) they corrupt each other's state. The correct fix is to move all of these into `__init__` so each screen gets its own copies.

**Fix:** Move every mutable group and list into `__init__`:
```python
def __init__(self, parent, screen_id):
    self.parent = parent
    self.grupo_anim = RenderAnim()
    self.grupo_botones = RenderButton()
    self.lista_final = []
    ...
```

---

### B. The Manejador Singleton is broken (Python 2 syntax)

**Files:** `librerias/singleton.py`, `manejador.py`

```python
class Manejador(object):
    __metaclass__ = Singleton   # Python 2 only — does nothing in Python 3
```

`__metaclass__` is silently ignored in Python 3. The `Singleton` metaclass is never applied. `Manejador` is not actually a singleton — you can create multiple instances and each will call `pygame.init()` again and create a new display.

The code "works" only because:
- `inicio.py` only ever creates one `Manejador`, and
- The class-level attributes (`config = Configuration()`, `grupo_magnificador = Rendermag()`) are shared across all instances by accident of Python's class model.

The `Configuration()` and `Rendermag()` being class attributes means they are instantiated at *class definition time*, before `pygame.init()` is called. `Rendermag` probably survives this, but anything that touches pygame display surfaces would not.

**Fix options:**
1. Fix the Singleton properly: `class Manejador(metaclass=Singleton)`.
2. Or drop the Singleton entirely — just create one instance in `inicio.py` and pass it around (which is already what happens). Document the assumption explicitly. The Singleton pattern buys nothing here.

---

### C. `Button` imports `Manejador` as its "parent" — class not instance

**Files:** `librerias/button.py`

```python
from manejador import Manejador as parent

class Button(GameObject):
    def __init__(self, ...):
        self.parent = parent          # This is the CLASS, not an instance
        my_font = SysFont("arial", self.parent.config.get_font_size())
```

`self.parent` on `Button` is the `Manejador` **class** itself, not a game manager instance. It then accesses `self.parent.config` which resolves to the class-level attribute `config = Configuration()` on `Manejador`. This works as a back-channel to the configuration singleton but it is deeply unintuitive — an object whose `parent` is a class, not an object.

The accidental correctness here depends on `config` being a class attribute, which depends on the Singleton being broken, which depends on nobody ever creating two `Manejador`s. It is a house of cards.

**Fix:** Pass the `Manejador` instance to `Button` from the screen that creates it (screens already have `self.parent`). Or just pass `config` directly. Either way, pass data explicitly.

---

### D. Configuration is saved on every single key write

**Files:** `librerias/configuration.py`

```python
def set_preference(self, key, value):
    self.preferences[key] = value
    self.save_config()   # full JSON write every time
```

`save_config()` writes and flushes the entire JSON file synchronously. If a screen updates three settings at once (e.g. the accessibility menu saving magnifier + font size + screen reader), that is three blocking file writes in a row. `update_preferences()` exists and does one write for N changes, but screens rarely use it.

**Fix:** Use `update_preferences` when changing multiple settings at once, or mark config as dirty and flush once at the end of a frame or on `cleanUp`.

---

### G. `resume()` called from `__init__` — init logic is split in two

**Files:** all `paginas/pantalla*.py`

Every screen's `__init__` ends with `self.resume()`. The `resume()` method re-adds sprites to groups and sets state flags. This means initialisation logic is split across two methods with no clear rule about what belongs where.

The intent seems to be: `resume()` resets the screen to its initial visual state so it can be called both after creation and after returning from a pushed overlay (like the config menu). That is a reasonable idea, but calling it from `__init__` makes `__init__` responsible for setup *and* for calling what is semantically a "return from pause" handler.

The base class also has an empty `start()` that is never called by anything meaningful, and an empty `cleanUp()`. The contract of `start` / `pause` / `resume` / `cleanUp` is informally documented but not enforced.

**Fix:** Distinguish what is one-time setup (belongs in `__init__`) from what is "return to ready state" (belongs in `resume`). Do not call `resume` from `__init__`; call it from `start` instead, which `Manejador.changeState` already invokes.

---

### H. Duplicate `SpriteSheet` implementation

**Files:** `librerias/animations.py` (class `spritesheet`), `librerias/button.py` (class `SpriteSheet`)

Both classes load a sprite sheet image and extract sub-images. The implementations are nearly identical. `animations.py` has a slightly richer `load_strip` (it handles multi-row sheets), but the core logic is the same. If a bug is found in one, it must be fixed in both.

**Fix:** Consolidate into one class in a shared module (e.g. `librerias/spritesheet.py`) and import from both `animations.py` and `button.py`.

---

### I. `tipo_objeto` string dispatch — three identical if/elif blocks

**Files:** `librerias/pantalla.py`

`controlador_lector_evento_K_RIGHT` and `controlador_lector_evento_K_LEFT` each contain:

```python
if self.x.tipo_objeto == "palabra":
    self.definir_rect(self.x.rect)
    self.spserver.processtext("explicar la palabra:" + self.x.palabra, ...)
elif self.x.tipo_objeto == "mapa":
    self.definir_rect(self.x.rect)
    self.spserver.processtext(self.x.id, ...)
elif self.x.tipo_objeto == "boton":
    self.definir_rect(self.x.rect)
    self.spserver.processtext(self.x.tt, ...)
```

Three branches that all call `definir_rect(self.x.rect)` and `spserver.processtext(some_attribute, ...)`. The only difference is which attribute holds the speech text. This is manual dynamic dispatch that should instead be a method on each object type: give `palabra`, `Button`, and map objects a common `get_reader_text()` method.

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

---

## Priority order for simplification

Given the goal of simplifying repetitive patterns while keeping the core working, the remaining open items in rough priority order:

1. **Fix class-level mutable state on `Pantalla`** (A) — latent bug that will bite when any feature uses `pushState` properly. Move all groups and lists into `__init__`.

2. **Consolidate SpriteSheet** (H) — quick win, reduces duplication across two key modules.

3. **Move glossary vocabulary to JSON** (L) — makes content edits possible without touching Python, consistent with the direction already taken with `content.json`.

4. **Fix the Singleton or remove it** (B) — technically harmless today but misleading. Either fix it or delete `singleton.py` and document the assumption.

5. **Fix `resume()`/`start()` split** (G) and **consolidate `tipo_objeto` dispatch** (I) — clean up the screen lifecycle and keyboard navigation respectively.

---

## Changelog

Improvements applied so far, in chronological order.

---

### ✅ E + F — Standardised text loading across all screens *(2026-02)*

**Files changed:** `librerias/pantalla.py`, `paginas/pantalla3–6,8–11.py`

Two problems were solved together:

- **E (two text-access styles):** All raw `self.parent.text_content["content"][self.name]["key"]` lookups were replaced with `self.screen_text("key")`, a thin wrapper around `text_loader.get()` added to `Pantalla`. Every screen now goes through `TextLoader` consistently.

- **F (cargar_textos boilerplate):** `Pantalla` gained a `load_screen_texts(keys, x, y, text_type, right_limit, custom)` helper that builds a `{key → Text}` dict in one call. Screens that had uniform `Text(...)` constructors (pantalla3, 4, 5, 6, 8) now use it. Screens with chained-y layout (pantalla9, 11) keep their explicit `Text(...)` calls but still benefit from `screen_text()` for all their string lookups.

The now-redundant `from librerias.texto import Text` imports were removed from pantalla3, 4, 5, 6, and 8.

---

### ✅ K — Dead config keys removed *(2026-02)*

**Files changed:** `librerias/configuration.py`, `src/user_config.json`, `src/librerias/user_config.json`

`texto_cambio` and `visit` removed from `Configuration.get_default_config()`. A `_migrate()` method was added and called from `__init__` so that any existing saved file has these keys stripped on first load, and the cleaned file is written back immediately.

---

### ✅ M — Named layout constants in `texto.py` *(2026-02)*

**Files changed:** `librerias/texto.py`

Six module-level constants replaced all magic pixel numbers:

```python
_MEASURE_LEFT      = 128   # left edge used when estimating line count
_MEASURE_RIGHT     = 896   # right edge used when estimating line count
_LAYOUT_1LINE      = (256, 768)   # (left, right) margins for single-line text
_LAYOUT_2LINE      = (192, 832)   # margins for two-line text
_LAYOUT_3PLUS      = (32,  992)   # margins for three-or-more lines
_TEXT_AREA_VCENTER = 382   # vertical midpoint of the on-screen text area
```
