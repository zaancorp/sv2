# sv2 — Architectural Analysis

This document analyses the current codebase with an eye towards simplification and maintainability. The goal is to identify what is working well, what are genuine anti-patterns, and where the most repetition lives so we can prioritise what to improve first.

Resolved issues are tracked in `CHANGELOG.md`. When an issue is fixed, move its entry from this file to `CHANGELOG.md` under the next SV2-XXX number in sequence.

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
Font creation is expensive. `FontManager` in `words.py` memoises by `(size, bold, underline)` tuples, which avoids creating a new `pygame.font.Font` on every render call.

### 6. Accessibility is first-class
Screen magnifier, TTS / screen reader, keyboard navigation, and configurable font size and character skin colour are all built into the base layer. For a personal project this is genuinely impressive.

### 7. Per-screen sprite groups are now instance-level *(SV2-001)*
Each screen gets its own fresh sprite groups at construction time, eliminating the silent state-sharing bug that corrupted `pushState` scenarios.

### 8. `Configuration` has a clean getter/setter API *(SV2-004, SV2-011)*
Dead keys are auto-migrated. `set_preference` only writes to memory; an explicit `flush()` / `save_config()` persists to disk. `mark_screen_visited` still saves immediately (intentional).

### 9. `SpriteSheet` is unified *(SV2-008)*
`components/spritesheet.py` is the single source of truth for loading sprite-sheet images. Both `Animation` (multi-row) and `Button` (single-row) import from it.

### 10. Screen-reader navigation uses a polymorphic protocol *(SV2-009)*
`Button`, `Word`, and `PropObject` each implement `get_reader_text()`. `Screen._announce_current()` calls it without a type-string switch.

### 11. Screen lifecycle is cleanly separated *(SV2-007)*
Screens are constructed via `__init__`, then `Manejador.changeState` calls `start()`. `start()` delegates to `resume()`, which populates the sprite groups and sets flags. Returning from a pushed overlay calls `resume()` directly. One-time setup and visual-reset logic are no longer interleaved.

### 12. Asset dicts are imported explicitly *(SV2-010)*
`screen.py` imports `backgrounds`, `banners`, `images`, `animations`, and `buttons` from `assets_data.py` using private-prefixed names (`_backgrounds`, `_banners`, etc.). The wildcard import is gone; the names are scoped and not visible to subclasses.

### 13. Glossary vocabulary lives in JSON *(SV2-012)*
`ENTRIES`, `DEFINITIONS`, `INDICES`, and `INTERCALATED` now live in `content.json` under `"glossary"`. Adding a new concept no longer requires touching Python source. `Manejador.load_text_content()` injects the tables into `Word`'s class attributes at startup via a local import.

### 14. `Manejador.show_concept()` is correctly dispatched *(SV2-014)*
`show_concept(codigo)` is now a thin dispatcher: it calls `_launch_interpreter(codigo)` (Blenderplayer sign-language interpreter) if auditory-disability mode is active, or `_show_glossary(codigo)` otherwise. Dead Python 3.2 bytecode cache cleanup code has been removed.

### 15. Accessibility config screens use the current Configuration API *(SV2-015)*
`menuauditivo.py` and `menuvisual.py` no longer call the removed `consultar()`, `cargar_default()`, or `guardar_preferencias()` methods, and no longer read or write preferences as direct object attributes. All preference access goes through `get_preference()` / `set_preference()` / `flush()`.

### 16. Glossary screen uses the current `Word` API *(SV2-016)*
`pantalla10.py` uses the current attribute and method names: `.definable`, `.definition`, `.selected`, `.highlight()`, `.text`, `.code`. The removed `.negrita()` calls have been deleted; bold-on-selection is handled automatically by the new render path.

---

## Open issues

### SV2-023 — Class-level sprite groups in `actividad1.py`

SV2-001 moved all sprite-group declarations from class-level to instance-level in `Screen`. `actividad1.py` was not updated and still declares them as class attributes:

```python
class Screen(screen.Screen):
    elapsed_ms = 0
    clock = pygame.time.Clock()
    anim_fondo = RenderAnim()
    button_group = RenderButton()
    character_group = RenderChar()
    boundaries = pygame.sprite.Group()
    prop_group = pygame.sprite.Group()
    marker_group = pygame.sprite.Group()
    popup_group = pygame.sprite.OrderedUpdates()
    prop_image_group = pygame.sprite.OrderedUpdates()
    # … and many more boolean/int class-level flags
```

All instances share the same group objects. If the activity screen is ever pushed onto the stack with another screen underneath (or constructed more than once in a session), sprite state bleeds across instances — the exact bug that SV2-001 was intended to eliminate.

---


