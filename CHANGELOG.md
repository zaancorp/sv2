## Changelog

Improvements applied so far, in reverse chronological order.

---

### ✅ SV2-053 — Assorted small dead code and minor bugs across content screens *(2026-03)*

**Files changed:** `paginas/pantalla2.py`, `paginas/pantalla3.py`, `paginas/pantalla4.py`, `paginas/pantalla6.py`, `paginas/pantalla9.py`, `paginas/pantalla10.py`

- **`pantalla2`** — Removed unreachable `"act1"` and `"act2"` entries from `button_actions` (no corresponding buttons exist); dropped `update()` override identical to base class default.
- **`pantalla3`** — Removed dead first `nav_list` assignment in `reproducir_animacion` (was immediately overwritten by the second).
- **`pantalla4`** — Removed redundant `if self.current_anim == 1: clear_groups(); resume()` tail in `go_back()` that caused step 1 to be set up twice when stepping back from step 2.
- **`pantalla6`** — Removed `self.repeticion = True` assignment from `go_next()`; the attribute was set but never read anywhere.
- **`pantalla9`** — Added `self._announce_region(lista[0].id)` to the mouse-click branch of `handleEvents` so that screen-reader users who click a map region with the mouse now receive TTS feedback, matching the keyboard-RETURN path. Removed the first (dead) `processtext` call in `resume()` that was immediately superseded by the second.
- **`pantalla10`** — Removed duplicate `self.word_group.add(self.abc.words)` call in `__init__` (the same words had already been added three lines earlier).

---

### ✅ SV2-052 — `pantalla11` mouse and keyboard handlers unified via `button_actions` *(2026-03)*

**Files changed:** `paginas/pantalla11.py`

Added `_go_back()` helper and a `button_actions` dict mapping `"puerta"` and the three audience button IDs to their respective callables. Replaced the duplicated inline `if/elif` logic in both the keyboard-RETURN branch and the mouse-collision branch with a single `button_actions.get(id, lambda: None)()` dispatch call in each, eliminating the duplication identified in SV2-052.

---

### ✅ SV2-051 — `pantalla10` and `pantalla11` bare-`if` dispatch and `update()` overrides cleaned up *(2026-03)*

**Files changed:** `paginas/pantalla10.py`, `paginas/pantalla11.py`

- **Bare-`if` → `elif`** in both screens: all event-type checks and sprite-collision scans are now in a proper `if / elif / elif` chain, so collision scans no longer run unconditionally on every event in the loop.
- **`pantalla11` nav rebuild** moved from inside the `KEYDOWN` block to a `_rebuild_nav()` call at the end of the event loop. `keyboard_nav_active` is now set to `True` in `K_LEFT`/`K_RIGHT` handlers and gated in `K_RETURN`, consistent with all other screens.
- **`update()` overrides dropped** from both screens; the three-line default is provided by the base class since SV2-045.
- **`pantalla10`**: the two `changeState(pantalla2.Screen(...))` calls (K_ESCAPE and "home" button) replaced by `self.go_home()` (base-class helper from SV2-048); `from paginas import pantalla2` import removed.

---

### ✅ SV2-050 — `pantalla8.go_back()` from step 1 rendered a blank screen *(2026-03)*

**Files changed:** `paginas/pantalla8.py`

`go_back()` previously guarded `if self.current_anim > 0` but still let `current_anim` reach 0, then called `reproducir_animacion(0)` which matched neither the `>= 4` transition nor any key in `animation_states`, leaving the screen blank. Fixed in two steps:

1. `go_back()` simplified to a plain `self.current_anim -= 1; self.reproducir_animacion(self.current_anim)` (the redundant `<= 0` reset removed).
2. `reproducir_animacion()` gained a `if animation_index <= 0: self.go_home(); return` guard at the top, matching the pattern used by `pantalla4`.

---

### ✅ SV2-048 — `go_home` / `go_config` promoted to the `Screen` base class *(2026-03)*

**Files changed:** `components/screen.py`, `paginas/pantalla3.py`, `paginas/pantalla4.py`, `paginas/pantalla5.py`, `paginas/pantalla6.py`, `paginas/pantalla8.py`, `paginas/pantalla9.py`

Six content screens each defined identical `go_home()` and `go_config()` methods. Both methods are now in `Screen` (base class) using deferred local imports (same pattern as `Manager.finish_config()`), eliminating the circular-import risk. All six screens had their copy of the methods and the now-redundant `from paginas import pantalla2` / `from paginas import menucfg` module-level imports removed.

---

### ✅ SV2-047 — `pantalla5` event handling rewritten to the standard pattern *(2026-03)*

**Files changed:** `paginas/pantalla5.py`

`pantalla5` had a completely non-standard event-handling paradigm. All six issues identified in SV2-047 resolved:

1. **K_ESCAPE quit** — The four custom handler methods (`handle_quit`, `handle_keydown`, `handle_mousebuttondown`, `handle_selection`) were removed. The new `handleEvents` uses the standard `if QUIT / elif KEYDOWN / elif MOUSEBUTTONDOWN` chain; K_ESCAPE is not handled (matching `pantalla4`/`pantalla6` which also omit it).
2. **Sprite-object `button_actions` keys** — Changed to string IDs (`"home"`, `"config"`, `"back"`, `"next"`), consistent with every other screen and resilient to `load_buttons()` rebuilds.
3. **Missing `handle_magnifier`** — Added `self.handle_magnifier(events)` at the end of `handleEvents`.
4. **Missing `clear_groups()` on navigation** — Resolved by inheriting `go_home()` / `go_config()` from the base class (SV2-048), which calls `clear_groups()` internally.
5. **Missing `is_overlay` forwarding to config** — Resolved by the same base-class `go_config()`.
6. **Manual nav rebuild** — Replaced by `self._rebuild_nav()` call. Word clicks now correctly call `self.parent.show_concept()` (matching `pantalla4`/`pantalla6`).

---

### ✅ SV2-046 — `_save_and_exit()` navigation tail extracted to `Manager.finish_config()` *(2026-03)*

**Files changed:** `manejador.py`, `paginas/menuauditivo.py`, `paginas/menuvisual.py`, `paginas/menugeneral.py`

All three config screens (`menuauditivo`, `menuvisual`, `menugeneral`) ended `_save_and_exit()` with an identical six-line navigation tail:

```python
self.clear_groups()
if self.parent.first_run:
    self.parent.changeState(pantalla2.Screen(self.parent))
else:
    if self.is_overlay:
        self.parent.RETURN_TO_PREV_SCREEN = True
    self.parent.popState()
```

Added `Manager.finish_config(screen)` to `manejador.py`. It clears the screen's sprite groups, then either transitions to the first content screen on a first run or returns to the previous screen otherwise. The `pantalla2` import is deferred inside the method body (following the same lazy-import pattern already used by `Manager.load_text_content()`) to avoid the circular dependency that a module-level import would create.

Each screen's `_save_and_exit()` now ends with `self.parent.finish_config(self)` in place of the six-line tail. The `from paginas import pantalla2` import was removed from all three screen files.

---

### ✅ SV2-045 — Menu screen one-pass cleanup *(2026-03)*

**Files changed:** `components/screen.py`, `paginas/menucfg.py`, `paginas/menuauditivo.py`, `paginas/menuvisual.py`, `paginas/menugeneral.py`

Seven issues identified and fixed in a single analysis pass over all four config menu screens.

**A. `pops` renamed to `popups_path` in `screen.Screen` (latent `AttributeError`)**
`screen.py` defined the popup image path as `pops = "./imagenes/png/popups/"`, but every caller throughout the codebase (including `screen.load_images()` itself, `menucfg`, `menuvisual`, `actividad1`, `actividad2`, `playground`) accessed it as `self.popups_path`. The attribute was never accessible under the name `pops`. Renamed to `popups_path` to match all usage.

**B. Default `update()` added to `screen.Screen`; four identical overrides removed**
All four menu screens defined the same three-line `update()`:
```python
def update(self):
    self.mouse.update()
    self.magnifier.magnificar(self.parent.screen)
    self.button_group.update(self.tooltip_group)
```
The base class had no `update()` method, so each screen duplicated the definition. Added it as the default implementation in `screen.Screen`. Deleted the override from `menucfg`, `menuauditivo`, `menuvisual`, and `menugeneral`.

**C. `menucfg` keyboard/mouse navigation dispatch unified**
The keyboard K_RETURN block and the mouse block each contained all five navigation actions (`intro`, `puerta`, `deaf-menu-btn`, `visual-menu-btn`, `general-menu-btn`) as separate `if/elif` chains — 30 lines of near-identical code. Added a `button_actions` dict in `__init__`; both branches now delegate via `self.button_actions.get(id, lambda: None)()`. The only asymmetry (`stopserver()` on mouse click) is preserved in the mouse branch.

**D. `menugeneral` bare `if` event blocks changed to `elif`; `button_actions` added; `_select_language` extracted**
`menugeneral.handleEvents` used bare `if` for both the `KEYDOWN` and sprite-collision checks (the SV2-042 fix that corrected `menuauditivo` and `menuvisual` missed this screen). Both changed to `elif`. The `lang_es` and `lang_hu` handlers were mirror images of each other; extracted as `_select_language(lang)` using an idempotent remove-all / add-correct dict pattern. Added `button_actions` dict; `handleEvents` now delegates via `.get()`. Added missing class docstring.

**E. `menuvisual` redundant no-op lifecycle overrides removed**
`menuvisual.Screen` overrode `start()`, `cleanUp()`, `pause()`, and `resume()` with single-line `pass` bodies. `screen.Screen` already defines all four as `pass` stubs. The four overrides were deleted.

---

### ✅ SV2-044 — Config screen constructor boilerplate cleaned up *(2026-03)*

**Files changed:** `paginas/menucfg.py`, `paginas/menuauditivo.py`, `paginas/menuvisual.py`, `paginas/menugeneral.py`

Three related boilerplate issues resolved across all config menu screens:

**1. Redundant `self.parent = parent` before `super().__init__` removed.**
All four config screens assigned `self.parent = parent` before calling `super().__init__`, which overwrites it immediately (line 40 of `screen.py` is `self.parent = parent`). The pre-super assignments were removed from `menucfg.py`, `menuauditivo.py`, `menuvisual.py`, and `menugeneral.py`. Content screens never had this line; config screens now match.

**2. `_label()` helper added; 21 hardcoded `Text(…, 20, 1, right)` constructors replaced.**
Each config screen now has a private `_label(self, x, y, key, right=N)` method that wraps the constant `size=20, text_type=1` arguments and the per-screen `text_loader.ui("config_screens", section, key)` path. All Q&A label constructions are now single-line `self._label(x, y, "key")` calls.

- `menuauditivo._label` — section `"auditory"`, default `right=700`; 9 constructors replaced.
- `menuvisual._label` — section `"visual"`, default `right=400`; 9 constructors replaced.
- `menugeneral._label` — section `"general"`, default `right=700`; 3 constructors replaced.

**3. `load_preferences` renamed to `_load_preferences` in `menuauditivo` and `menuvisual`.**
`menugeneral` already used the private convention. `menuauditivo` and `menuvisual` used the public name `load_preferences()`, which is only ever called from `__init__`. Both renamed to `_load_preferences` for consistency.

---

### ✅ SV2-043 — `_save_and_exit()` extracted in `menuauditivo.py` and `menugeneral.py` *(2026-03)*

**Files changed:** `paginas/menuauditivo.py`, `paginas/menugeneral.py`

The `set_preference("cache") → flush → clear_groups → changeState/popState` tail was copy-pasted in both screens' `"guardar"` handlers, matching the duplication that SV2-041 had already fixed in `menuvisual.py` by introducing `_save_and_exit()`.

Changes made:
- **`menuauditivo.py`**: Added `_save_and_exit()` (sets cache, checks font-size change, flushes, clears groups, then `changeState` or `popState`). The `"guardar"` handler retains only the screen-specific pre-flush step (recording the slider position `ubx` when velocity is at the default) before delegating to `_save_and_exit()`.
- **`menugeneral.py`**: Added `_save_and_exit()` (sets cache, flushes, calls `reload_text_content()`, clears groups, then `changeState` or `popState`). The `"guardar"` handler is now a single `self._save_and_exit()` call.

All three config screens (`menuauditivo`, `menuvisual`, `menugeneral`) now share the `_save_and_exit()` convention; each encapsulates only its screen-specific pre-flush logic.

---

### ✅ SV2-042 — `menuauditivo.py` and `menuvisual.py` event-type branches changed to `elif` *(2026-03)*

**Files changed:** `paginas/menuauditivo.py`, `paginas/menuvisual.py`

Both screens used bare `if` for the sprite-collision block (and `menuvisual` also used bare `if` for the `KEYDOWN` block), causing unnecessary sprite-collision scans on every event in the list — including `QUIT`, `KEYDOWN`, `MOUSEMOTION`, and `KEYUP`. This is the same structural issue fixed in `menucfg.py` as part of SV2-039.

Changes made:
- **`menuauditivo.py`**: `if pygame.sprite.spritecollideany(...)` → `elif`, forming a correct `if QUIT / elif collision` chain.
- **`menuvisual.py`**: `if event.type == pygame.KEYDOWN` → `elif`, and `if pygame.sprite.spritecollideany(...)` → `elif`, forming a correct `if QUIT / elif KEYDOWN / elif collision` chain.

---

### ✅ SV2-041 — `menuvisual.py` duplicate save path extracted; raw key codes fixed *(2026-03)*

**Files changed:** `paginas/menuvisual.py`

The save-and-navigate sequence (8 lines: set cache, check font change, flush, update TTS server, clear groups, changeState or popState) was copy-pasted identically between `handle_key_input(opcion=3, key=4)` and the mouse `"guardar"` handler. The keyboard wizard path also used raw integer literals `49`/`50`/`51` for key detection instead of named pygame constants.

Changes made:
- Extracted a `_save_and_exit()` method containing the shared save-and-navigate block (includes `stopserver()` so both call sites behave consistently). Both `handle_key_input` and the mouse handler now delegate to it.
- Replaced `event.key == 49` / `50` / `51` with `event.key == pygame.K_1` / `pygame.K_2` / `pygame.K_3`.

---

### ✅ SV2-040 — `menuauditivo.py` word_group.remove copy-paste bug fixed *(2026-03)*

**Files changed:** `paginas/menuauditivo.py`

Both gender-toggle handlers called `word_group.remove` with a label repeated three times:

- `gender-boy-btn`: `q3_label_female.words` appeared at arguments 1, 2, and 4; `q4_label_female.words` appeared once (correct). A separate `word_group.remove(q4_label_male.words)` followed immediately.
- `gender-girl-btn`: `q3_label_male.words` appeared at arguments 1, 2, and 4; `q4_label_male.words` appeared once (correct). A redundant `word_group.remove(q4_label_male.words)` followed.

Because `pygame.sprite.Group.remove` is idempotent, no crash occurred, but the intent was obscured. Each handler now lists each label exactly once, with the follow-up `remove` call incorporated into or removed from the main call.

---

### ✅ SV2-039 — `menucfg.py` keyboard nav switched to base Screen infrastructure *(2026-03)*

**Files changed:** `paginas/menucfg.py`

`menucfg.py` implemented keyboard navigation manually: a `focus_index` counter, manual `self.x = self.button_list[self.focus_index]`, `speech_server.processtext(self.x.tt, True)`, and `set_focus_rect(self.x.rect)` — duplicating logic that `nav_right()` / `nav_left()` / `_announce_current()` already provide. Additionally, the event type blocks used separate `if` statements (not `elif`), causing the sprite-collision check to run on every event including `KEYDOWN`, and `_rebuild_nav()` was never called so `button_list` could go stale. Dead `self.teclasPulsadas = pygame.key.get_pressed()` was also present before the event loop.

Changes made:
- Replaced the manual K_RIGHT/K_LEFT blocks with `self.nav_right()` / `self.nav_left()`.
- Changed the sprite-collision block to `elif` (so it only runs on non-KEYDOWN events).
- Removed the manual `collect_buttons` + `element_count` assignment inside the KEYDOWN block.
- Removed `self.teclasPulsadas = pygame.key.get_pressed()`.
- Added `self._rebuild_nav()` at the end of `handleEvents`.
- K_RETURN now sets `keyboard_nav_active = False` on activation (consistent with content screens).

---

### ✅ SV2-038 — `menucfg.py` keyboard dispatch wrong button IDs fixed *(2026-03)*

**Files changed:** `paginas/menucfg.py`

The K_RETURN keyboard handler checked `self.x.id == "sordo"` and `self.x.id == "config-vis"`, neither of which matched the actual sprite IDs `"deaf-menu-btn"` and `"visual-menu-btn"`. Pressing Enter on the auditory or visual accessibility buttons via keyboard silently did nothing.

Fixed as part of the SV2-039 rewrite by correcting the ID strings to match the actual sprite IDs used throughout the rest of the handler and in `assets_data.py`.

---

### ✅ SV2-037 — `TextLayout` base class introduced; `Text._layout_words` unified *(2026-03)*

**Files changed:** `components/words.py`, `components/texto.py`, `components/textoci.py`

`Text._layout_words` and `InlineText.__init__`'s positioning loop both walk `words[]`, check `word.rect.width` against `right_limit`, advance `y` on wrap, and set `word.rect.topleft`. The gap mechanisms differ (`Text` uses proportional `word_gaps`; `InlineText` uses per-line justified spacing from `medidas`), and `InlineText` additionally centres words vertically within uniform line heights and handles `|` hard-break tokens — making a fully merged loop impractical without heavy parameterisation.

Changes made:
- **`words.py`**: Added `TextLayout` mixin class at module level. Provides `_wrap_and_position(words, gaps, start_x, start_y)` — the shared gap-before/wrap/position loop that both callers converge on. Returns `(max_width, total_height)`.
- **`texto.py`**: `Text` now extends `TextLayout`. `_layout_words` reduced from 25 lines to 8: computes `start_y` (unchanged), then delegates entirely to `self._wrap_and_position(self.words, self.word_gaps, self.left_limit, y)`. The loop logic lives in one place.
- **`textoci.py`**: `InlineText` now extends `TextLayout`, making the shared base explicit. `calcular` (the variable-line-height measurement pass) deleted — it was dead code (its call was commented out in `__init__`, replaced by `compute_layout`). Two stale commented-out lines in `__init__` (`calcular` call, `line_height[n]` indexing) removed. `InlineText`'s positioning loop stays inline; its justified-spacing + vertical-centring requirements are documented in the `TextLayout` docstring as the reason it doesn't yet call `_wrap_and_position`.

---

### ✅ SV2-034 — `pantalla9.py` 9-region map screen made data-driven *(2026-03)*

**Files changed:** `paginas/pantalla9.py`

The Venezuela agricultural map screen had three layers of repetition totalling ~700 lines:

- **`__init__`**: 9 separate `object_mask()` calls, each with hardcoded pixel offsets relative to `self.zulia` — no shared data structure.
- **`load_texts`**: 28 individual `Text()` calls (3–4 per region) with identical `x=490`, `right_limit=1000`, `text_type=1` parameters; y-positions chained via `prev.y + prev.total_width + 10`; attribute names like `self.texto9_2_1` made iteration impossible.
- **`handleEvents`**: The show-region action (empty `word_group`, `apagar()` all others, `iluminar()` this one, `add()` text words, TTS) written out 9 times in the keyboard block and 9 times again in the mouse block — 18 copies total.

Changes made:
- Added module-level `_REGION_SPECS` table (9 tuples): `(region_id, attr_name, dx, dy, img_base, text_prefix, num_paragraphs)`. Positions are expressed as offsets from `_ZULIA_X, _ZULIA_Y = 13, 140` so the geometry is visible in one place.
- `__init__` builds all 9 `object_mask` objects in a loop; stores them in `self.regions` dict (region_id → mask) and `self.region_list` (ordered, for `map_group` z-order). `setattr(self, attr, mask)` preserves `self.zulia`, `self.capital`, etc. for backward compatibility.
- `load_texts` builds all text objects in a loop; stores them in `self.region_texts[region_id]` list instead of 28 individual attributes. y-chaining is preserved exactly.
- `_show_region(region_id)` — turns off all other masks, turns on the target, and populates `word_group`. Single implementation replaces 18 copies.
- `_announce_region(region_id)` — sends TTS for the region (keyboard-nav path only, matching original behaviour where mouse clicks did not trigger TTS).
- `resume()` now loops over `self.regions.values()` for `apagar()` calls (also fixes an original omission where `insu` was never reset on resume).
- `handleEvents` rebuilt using `button_actions` + `go_*` methods for the 3 nav buttons; map dispatch uses `_show_region`/`_announce_region`; clear-when-not-hovering logic moved outside the event loop (once per frame instead of per event — same visual result at 30 fps).
- `pantalla9.py` shrank from ~914 lines to ~235 lines.

---

### ✅ SV2-033 — `handleEvents()` button-action dispatch deduplicated across all content screens *(2026-03)*

**Files changed:** `components/screen.py`, `paginas/pantalla2.py`, `paginas/pantalla3.py`, `paginas/pantalla4.py`, `paginas/pantalla6.py`, `paginas/pantalla8.py`

Every content screen duplicated the same button-action logic twice — once inside the keyboard `K_RETURN` block and again inside the mouse `MOUSEBUTTONDOWN` block — and rebuilt the keyboard-navigation list on every `KEYDOWN` event regardless of which key was pressed.

Changes made:
- **`screen.py`**: added `_rebuild_nav()` helper that calls `collect_buttons(button_group)` and rebuilds `nav_list` and `element_count`. Screens call this once at the end of `handleEvents` instead of repeating the three-line sequence inside every `KEYDOWN` branch.
- **`pantalla4`, `pantalla6`, `pantalla8`, `pantalla3`**: added a `button_actions` dict (string ID → callable) and `go_home`, `go_config`, `go_back`, `go_next` action methods. `handleEvents` now delegates to `button_actions.get(id, lambda: None)()` for both keyboard and mouse paths. Each screen's handler shrank from ~80 lines to ~30 lines.
- **`pantalla2`**: same pattern with 7 navigation targets (`go_plantas`, `go_repro`, `go_agri`, `go_config`, `go_orientacion`, `go_act1`, `go_act2`). Dead `self.teclasPulsadas` assignment removed. Handler shrank from ~90 lines to ~20 lines.
- **`pantalla6`**: mouse word-click changed from `pygame.mouse.get_pressed()` polling to `MOUSEBUTTONDOWN` event handling (consistent with all other screens). K_LEFT now also sets `keyboard_nav_active = True` (bug fix).
- All screens: `if/elif` chain on `event.type` is now a proper `if/elif/elif` instead of separate `if` blocks that rechecked the event on every iteration.

---

### ✅ SV2-032 — Animation state machine unified across all content screens *(2026-03)*

**Files changed:** `components/screen.py`, `paginas/pantalla4.py`, `paginas/pantalla5.py`, `paginas/pantalla6.py`, `paginas/pantalla8.py`

`pantalla4`, `pantalla6`, and `pantalla8` implemented animation playback as long `if animation_index == N:` chains, each block repeating the same 8–10 lines of boilerplate (empty groups, swap animation, reset stop flag, call `continuar`, send TTS). `pantalla5` had already solved this with an `animation_states` dict and a `setup_animation` helper, but the other three screens predated that refactor.

Changes made:
- `setup_animation(animation_obj, text_obj, text_key)` moved from `pantalla5` into the `Screen` base class so all screens inherit it. It empties `anim_group`, `text_bg_group`, and `word_group`; adds the new animation; optionally shows the text panel; calls `continuar()`; and sends a TTS announcement.
- `pantalla5`: removed the now-redundant local `setup_animation` definition (inherits the identical version from `Screen`).
- `pantalla4`: added an `animation_states` dict (8 entries); rewrote `reproducir_animacion` to call `setup_animation` + per-step specials (anim steps re-add `animation_4` as a stopped background; step 1 removes the back button; step 7 re-adds the next button; step 8 cleans tooltips).
- `pantalla6`: added an `animation_states` dict (12 entries); rewrote `reproducir_animacion` to call `setup_animation` + always restore `animation_6_2` as secondary background + per-step specials for the 4 anim steps (which need `animation_6` stopped behind the sub-animation) and steps 1, 2, 11, 12.
- `pantalla8`: added an `animation_states` dict (3 entries); rewrote `reproducir_animacion` to call `setup_animation` + per-step specials; exit to `pantalla9` is now a clean early return at `animation_index >= 4`.
- All four screens now end `reproducir_animacion` with the same `collect_buttons` / nav-list rebuild that `pantalla5` already had, making keyboard navigation consistent.

---

### ✅ SV2-036 — Shared tokenizer extracted from `texto.py` and `textoci.py` *(2026-03)*

**Files changed:** `components/words.py`, `components/texto.py`, `components/textoci.py`

Three pieces of duplicated logic in the text-rendering classes were consolidated:

1. **Image substitution** (`_apply_image_substitution`) — a 5-line inline block appeared identically in `InlineText.calcular` and `InlineText.compute_layout`, and in a 7-line variant in `InlineText.__init__`. Extracted to `_apply_image_substitution(word) → bool` in `InlineText`; callers reduced to a single call each.

2. **Tokenizer** (`_tokenize`) — `texto.py` used `re.split(r"(\s+)", ...)` and `textoci.py` used a character-buffer loop; both skipped `"reproducción"` in non-`active_text` mode and created `Word` sprites. Extracted to module-level `_tokenize(text, size, text_type, space_px) → (words, word_gaps)` in `words.py` (already imported by both callers). `texto.py` drops `import re` and its 20-line loop becomes one line; `textoci.py`'s 14-line char-buffer loop becomes one line and also loses `self.buffer`. As a side effect, `InlineText` no longer silently drops the last word of texts that do not end with a space (latent bug fixed).

The remaining line-wrapping loop duplication (`Text._layout_words` vs. `InlineText.compute_layout`) requires a shared `TextLayout` base class and is tracked separately as SV2-037.

---

### ✅ SV2-035 — `pantalla11.py` audience text loading and event dispatch deduplicated *(2026-03)*

**Files changed:** `paginas/pantalla11.py`

The orientation screen had three audience groups (students / teachers / parents) each with 3 `Text()` calls, and 6 identical event-handler blocks (3 button IDs × keyboard + mouse). Replaced with a module-level `_AUDIENCES` dict keyed by button ID, a `load_texts` loop that chains `y` positions automatically, and a single `_show_audience(button_id)` helper called from both the keyboard and mouse branches. Also fixed a latent bug: the keyboard handler checked stale IDs (`"or-ninos"`, `"or-docentes"`, `"or-padres"`) that never matched the actual button IDs, so keyboard navigation to audience buttons was silently broken; the refactored handler uses `self.x.id in _AUDIENCES` which matches the correct IDs.

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
