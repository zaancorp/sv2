# sv2 — Architectural Analysis

This document analyses the current codebase with an eye towards simplification and maintainability. The goal is to identify what is working well, what are genuine anti-patterns, and where the most repetition lives so we can prioritise what to improve first.

---

## What works well

### 1. The game loop and state machine are clean
`inicio.py` is exactly four lines of actual logic. The `Manejador` state stack with `changeState` / `pushState` / `popState` is a solid and well-understood pattern. The lifecycle contract (`start → pause → resume → cleanUp`) is the right idea even if it's not perfectly consistent in implementation.

### 2. Asset data is centralised
`assets_data.py` holds every button, animation, and banner spec in one place. The loader methods on `Pantalla` (`load_buttons`, `load_animations`, `load_banners`) iterate over those specs and do the heavy lifting. Screen files only declare which assets they need, not how to load them. That is a good separation.

### 3. Text content is in JSON
All user-facing Spanish text lives in `content.json`, including the glossary vocabulary look-up tables (`ENTRIES`, `DEFINITIONS`, `INDICES`, `INTERCALATED`) that mark which words in running text are clickable. Text that changes together belongs together, and it gives a single place to make translation or copy edits without touching Python files.

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

### 11. Screen lifecycle is cleanly separated *(fixed in G)*
Screens are constructed via `__init__`, then `Manejador.changeState` calls `start()`. `start()` delegates to `resume()`, which populates the sprite groups and sets flags. Returning from a pushed overlay calls `resume()` directly. One-time setup and visual-reset logic are no longer interleaved.

### 12. Asset dicts are imported explicitly *(fixed in J)*
`pantalla.py` imports `backgrounds`, `banners`, `images`, `animations`, and `buttons` from `assets_data.py` using private-prefixed names (`_backgrounds`, `_banners`, etc.). The wildcard import is gone; the names are scoped and not visible to subclasses.

### 13. Glossary vocabulary lives in JSON *(fixed in L)*
`ENTRIES`, `DEFINITIONS`, `INDICES`, and `INTERCALATED` now live in `content.json` under `"glossary"`. Adding a new concept no longer requires touching Python source. `Manejador.load_text_content()` injects the tables into `palabra`'s class attributes at startup via a local import.

### 14. `Manejador.interpretar()` is correctly dispatched *(fixed in N)*
`interpretar(codigo)` is now a thin dispatcher: it calls `_launch_interpreter(codigo)` (Blenderplayer sign-language interpreter) if auditory-disability mode is active, or `_show_glossary(codigo)` otherwise. Dead Python 3.2 bytecode cache cleanup code has been removed.

### 15. Accessibility config screens use the current Configuration API *(fixed in O)*
`menuauditivo.py` and `menuvisual.py` no longer call the removed `consultar()`, `cargar_default()`, or `guardar_preferencias()` methods, and no longer read or write preferences as direct object attributes. All preference access goes through `get_preference()` / `set_preference()` / `flush()`.

### 16. Glossary screen uses the current `palabra` API *(fixed in P)*
`pantalla10.py` uses the current attribute and method names: `.definable`, `.definition`, `.selected`, `.highlight()`, `.text`, `.code`. The removed `.negrita()` calls have been deleted; bold-on-selection is handled automatically by the new render path.

---

## Open anti-patterns

### Critical — crash risk

#### R. `TextType` enum receives string values (`texto.py` / `palabra.py`)

`palabra.__init__` converts its `text_type` argument with `self.text_type = TextType(text_type)`. `TextType` is an `IntEnum` with values `1`–`8` (`NORMAL=1`, `ACTIVE=2`, …, `TEXT_BOX=8`). `texto.py` constructs every `palabra` sprite by forwarding the human-readable string it received — `"definicion"`, `"indice"`, `"concepto"`, `"texto_act"`, etc. — directly to that constructor. `TextType("definicion")` raises `ValueError` at runtime; no `palabra` sprite can ever be created.

This affects every call site that passes a string text-type, which is every caller in the codebase:
- All `Text(…, "definicion", …)` / `"indice"` / `"concepto"` / `"texto_act"` calls in `pantalla10.py`
- All `Text(…, "texto_act", …)` calls in `popups.py` (tipo 0 and tipo 1)
- `TextButton(fondo=1)` in `button.py`, which passes `"texto_act"`

Either `TextType` must be changed to accept string values (e.g. by keying on `.name` rather than `.value`), or every call site must be updated to pass the correct integer constant.

#### S. Empty `Text("")` crashes `_layout_words` (`texto.py`)

`pantalla10.py` creates a placeholder concept text object with an empty string:

```python
self.concepto = Text(600, 200, "", self.parent.config.get_font_size(), "concepto", 1000)
```

`Text._layout_words` iterates `self.words` and ends with:

```python
return max_width, total_height + word.rect.height
```

When the input string is empty, `self.words` is `[]`, the loop body never runs, `word` is never bound, and the `return` raises `UnboundLocalError`. `_estimate_total_height` similarly raises `IndexError` on `self.words[0]`. Any screen that creates a `Text` object with an empty string will crash immediately on construction.

#### T. Missing `.config.` on `set_text_change_enabled` (`menuauditivo.py`, `menuvisual.py`)

Three call sites introduced during fix O call the method on the wrong object:

- `menuauditivo.py` line 412: `self.parent.set_text_change_enabled(True)`
- `menuvisual.py` line 335: `self.parent.set_text_change_enabled(True)`
- `menuvisual.py` line 526: `self.parent.set_text_change_enabled(True)`

`set_text_change_enabled` is a method on `Configuration`, not on `Manejador`. All three calls raise `AttributeError` the moment the user saves a preference that triggers the font-change flag. The correct call is `self.parent.config.set_text_change_enabled(True)`.

#### U. `TextButton` uses renamed attribute `txt.ancho_final` (`button.py`)

`TextButton.__init__` (the `fondo=1` path, line 238) constructs a `Text` object and then reads:

```python
self.rect = Rect(0, 0, self.ancho, txt.ancho_final)
```

`Text.ancho_final` was renamed to `total_height` during the Q fixes. The attribute no longer exists; any `TextButton` with `fondo=1` crashes on construction with `AttributeError`.

#### V. `get_preference("definicion", "")[0]` on empty default (`pantalla10.py`)

`pantalla10.__init__` line 40:

```python
inicial = self.parent.config.get_preference("definicion", "")[0].upper()
```

On first launch, before the user has ever selected a glossary word, the `"definicion"` key is absent from the config file and `get_preference` returns the default `""`. Indexing an empty string with `[0]` raises `IndexError`. The glossary screen therefore crashes on every fresh install.

---

### High severity

#### W. Class-level sprite groups in `actividad1.py`

Fix A moved all sprite-group declarations from class-level to instance-level in `Pantalla`. `actividad1.py` was not updated and still declares them as class attributes:

```python
class estado(pantalla.Pantalla):
    tiempo = 0
    reloj = pygame.time.Clock()
    anim_fondo = RenderAnim()
    grupo_botones = RenderButton()
    grupo_texto = RenderText()
    grupo_anim = RenderAnim()
    grupo_banner = RenderBanner()
    grupo_tooltip = RenderTooltip()
```

All instances share the same group objects. If the activity screen is ever pushed onto the stack with another screen underneath (or constructed more than once in a session), sprite state bleeds across instances — the exact bug that fix A was intended to eliminate.

#### X. Bare `except:` in `Manejador._launch_interpreter`

`manejador.py` line 177:

```python
except:
    print("No se ha podido cargar el interprete virtual.")
```

The naked `except` clause catches everything, including `KeyboardInterrupt`, `SystemExit`, and memory errors. It also silently drops the exception object, making it impossible to distinguish a missing binary from a permission error, a corrupt blend file, or an OOM condition. It should be `except OSError as e:` (or `FileNotFoundError`) with the error logged.

---

### Medium severity

#### Y. `pantalla2.py` reads a dead configuration key

`pantalla2.py` line 92 uses:

```python
self.parent.config.get_preference("texto_cambio", True)
```

The key `texto_cambio` was migrated away from `user_config.json` during fix K; the live key is `text_change`, accessed via `is_text_change_enabled()` / `set_text_change_enabled()`. Because `texto_cambio` is never written, `get_preference` always returns the hardcoded default `True`. The intended optimisation — skipping a font reload when nothing changed — is permanently disabled; the screen always reloads fonts on every resume.

#### Z. `has_visited_screen("p2")` condition is inverted (`pantalla2.py`)

```python
if self.parent.config.has_visited_screen("p2"):
    self.parent.config.mark_screen_visited("p2")
else:
    self.spserver.processtext(…)
```

The logic is backwards: the TTS announcement fires on every *revisit* (when the screen has already been visited) and is skipped on the *first* visit. The `mark_screen_visited` call in the `if` branch is also redundant — the screen is already marked. The branches should be swapped.

#### AA. Dead circular import in `speechserver.py`

`speechserver.py` line 6:

```python
from manejador import Manejador as parent
```

This import is at module level. The import chain is:

```
pantalla.py  →  speechserver.py  →  manejador.py  →  pantalla.py
```

The name `parent` is referenced only in code that is entirely commented out. The import serves no purpose and creates a circular dependency that will cause an `ImportError` under any import order that starts from `manejador`. It should be deleted.

#### BB. `Speechserver` is entirely stubbed — TTS is non-functional

Every method in `Speechserver` (`processtext`, `processtext2`, `stopserver`, `repetir`, `quitserver`, `actualizar_servidor`) has a body of `pass`. No text is ever synthesised or spoken. The screen-reader feature advertised as a first-class accessibility capability (see point 6 in "What works well") is silently inert. This is not a crash risk but it means the accessibility promise is currently unmet.
