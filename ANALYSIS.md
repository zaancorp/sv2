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

---

### SV2-068 — `handleEvents` body is copy-pasted across all content screens

**Affected files:** `paginas/pantalla2.py`, `paginas/pantalla3.py`, `paginas/pantalla4.py`, `paginas/pantalla5.py`, `paginas/pantalla6.py`, `paginas/pantalla8.py`, `paginas/pantalla11.py`

Every content screen's `handleEvents` method is near-identical: check QUIT, handle K_RIGHT/K_LEFT with `keyboard_nav_active`, dispatch K_RETURN to `button_actions` or `show_concept`, handle MOUSEBUTTONDOWN on `word_group` then `button_group`, then call `_rebuild_nav()` and `handle_magnifier(events)`. Aside from an occasional extra key (K_F1 in pantalla2, K_SPACE in pantalla3, K_ESCAPE in pantalla10–11) and one structural inconsistency (noted separately in SV2-080), the bodies are verbatim duplicates spanning ~30 lines each.

**Concrete recommendation:** Add a `handle_standard_events(events)` method to `Screen` that encodes the common QUIT + keyboard nav + button/word mouse dispatch + `_rebuild_nav()` + `handle_magnifier()` sequence. Each screen overrides `handleEvents` only for its screen-specific keys, then delegates to `super().handle_standard_events(events)` (or calls `self.handle_standard_events(events)` if no extra keys are needed). This eliminates approximately 200 lines of duplicated code.

---

### SV2-069 — Text-reload guard in `resume()` is copy-pasted across all content screens

**Affected files:** `paginas/pantalla3.py:66-69`, `paginas/pantalla4.py:96-99`, `paginas/pantalla5.py:98-101`, `paginas/pantalla6.py:98-101`, `paginas/pantalla8.py:87-90`, `paginas/pantalla9.py:137-140`

Every content screen's `resume()` opens with the identical three-line block:

```python
if self.parent.config.is_text_change_enabled():
    self.load_buttons(buttons)
    self.load_texts()
    self.parent.config.set_text_change_enabled(False)
```

**Concrete recommendation:** Promote this to a `Screen.reload_if_config_changed(buttons_list)` helper that screens call at the top of `resume()`. Alternatively, override `resume()` in `Screen` to call `self.on_resume()` (a subclass hook), and move the reload guard into the base `resume()` body.

---

### SV2-070 — `reproducir_animacion()` manually rebuilds the nav-list instead of calling `_rebuild_nav()`

**Affected files:** `paginas/pantalla3.py:173-175`, `paginas/pantalla4.py:217-219`, `paginas/pantalla5.py:208-210`, `paginas/pantalla6.py:211-213`, `paginas/pantalla8.py:215-217`

Every `reproducir_animacion()` method ends with:

```python
self.collect_buttons(self.button_group)
self.nav_list = self.word_list + self.button_list
self.element_count = len(self.nav_list)
```

This is exactly what `Screen._rebuild_nav()` already does (`screen.py:370-379`). The inline copy exists because `_rebuild_nav()` was added after these methods were written.

**Concrete recommendation:** Replace the three-line tail in each `reproducir_animacion()` with `self._rebuild_nav()`.

---

### SV2-071 — `_label()` helper is triplicated across config screens

**Affected files:** `paginas/menuauditivo.py:89-91`, `paginas/menuvisual.py:111-113`, `paginas/menugeneral.py:68-70`

All three config sub-screens define an identical `_label(self, x, y, key, right=N)` method that wraps `Text(x, y, self.parent.text_loader.ui("config_screens", SECTION, key), 20, 1, right)`. The only variation is the hard-coded section string (`"auditory"`, `"visual"`, `"general"`).

**Concrete recommendation:** Add a `_config_label(self, section, x, y, key, right=700)` method to `Screen` (or to a `ConfigScreen` intermediate base class). Each config screen calls it with its own section name, or the intermediate class stores the section once and provides a `_label()` that supplies it automatically.

---

### SV2-072 — `update()` body is duplicated across content screens

**Affected files:** `paginas/pantalla3.py:177-189`, `paginas/pantalla4.py:163-176`, `paginas/pantalla5.py:167-179`, `paginas/pantalla6.py:215-229`, `paginas/pantalla8.py:149-178`

Every content screen overrides `update()` with the same three base-class lines followed by a guard:

```python
def update(self):
    self.mouse.update()
    self.magnifier.magnificar(self.parent.screen)
    self.button_group.update(self.tooltip_group)
    if self.current_anim == 1 and not self.parent.config.is_screen_reader_enabled():
        if not self.elapsed_ms < 1000:
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto_N_2.words)
            self.txt_actual = self.texto_N_2.words
            self.collect_words(self.txt_actual)
            self.animation_N.continuar()
    self.elapsed_ms += self.frame_clock.get_time()
```

The first three lines duplicate the base `Screen.update()` without calling `super().update()`. The "show text after 1-second delay on step 1" pattern is identical across all five screens — only the attribute names (`self.texto3_2`, `self.texto4_2`, etc. and `self.animation_3`, `self.animation_4`, etc.) differ.

**Concrete recommendation:** Have each screen call `super().update()` for the first three lines. Extract the delayed-first-step reveal into a helper: `_start_delayed_text(self, text_obj, anim_obj)` that performs the `elapsed_ms` check and group updates. Content screens that need it call `self._start_delayed_text(self.texto_N_2, self.animation_N)` in their `update()` override, which can now be just three lines.

---

### SV2-073 — `pantalla3.draw()` is a no-op override identical to the base class

**Affected file:** `paginas/pantalla3.py:191-205`

`pantalla3.Screen.draw()` overrides `Screen.draw()` with a body that is literally line-for-line identical to `screen.Screen.draw()`. No drawing step is added, removed, or reordered. The override serves no purpose and is a maintenance liability — changes to the base class draw order will not automatically propagate to `pantalla3`.

**Concrete recommendation:** Delete the `draw()` method from `pantalla3.py` entirely.

---

### SV2-074 — Accumulated dead code: four unreachable or discontinued items

**Affected files:** `paginas/pantalla2.py:140-146`, `components/button.py:139-149`, `components/popups.py:233-241`, multiple screens

Four distinct dead-code sites:

1. **`pantalla2.go_act1()` and `go_act2()` (lines 140–146)** — Both methods are defined but neither appears in the `button_actions` dict (lines 54–60), and neither button ID (`"act1"`, `"act2"`) appears in the `buttons` list. They are unreachable from the UI.

2. **`Button.play_sound()` (button.py:139–149)** — The only functional line in the method body (`canal.play(self.sonido)`) is commented out, leaving the method as a near-no-op. `self.sonido` is never assigned anywhere on `Button`. The method is never called.

3. **`PopUp.redraw_button()` (popups.py:233–241)** — Docstring says "discontinued". The method is never called anywhere in the codebase.

4. **`self.creado = True` in content-screen `resume()` (pantalla3:74, pantalla4:103, pantalla5:108, pantalla6:107, pantalla8:95)** — The attribute `creado` ("created") is written in every content screen's `resume()` but read nowhere — not in the screens themselves, not in the base class, not in `manejador.py`.

**Concrete recommendation:** Delete all four. For `go_act1`/`go_act2`, keep the `actividad1` import if activity screens are intended to be reachable but add the button IDs to the `button_actions` dict and `buttons` list (or open a separate issue). For `Button.play_sound`, remove the method and `self.sonar`. For `redraw_button`, delete the method. For `creado`, delete all five assignments.

---

### SV2-075 — `first_entry` is set *after* `reproducir_animacion()` in `pantalla5.resume()`, making the guard inert

**Affected file:** `paginas/pantalla5.py:115-116`

In `pantalla5.Screen.resume()`:

```python
self.reproducir_animacion(self.current_anim)   # line 115 — reads self.first_entry
self.first_entry = True                         # line 116 — set too late
```

`reproducir_animacion()` at step 1 checks `if … self.first_entry:` to decide between `processtext2` (non-interrupting) and `processtext` (interrupting). Because `first_entry` is assigned on the line *after* the call, it reads whatever value `first_entry` already had — `True` from `Screen.__init__` on first construction, but stale on any subsequent `resume()`. The `True` reset at line 116 takes effect only for the *next* resume, not the current one.

Compare: `pantalla6.resume()` correctly sets `self.first_entry = True` on line 112, *before* `self.reproducir_animacion(self.current_anim)` on line 113.

**Concrete recommendation:** Swap the two lines — move `self.first_entry = True` to before the `reproducir_animacion()` call, matching the pattern used in `pantalla6` and `pantalla8`.

---

### SV2-076 — Config sub-screens have no keyboard navigation

**Affected files:** `paginas/menuauditivo.py`, `paginas/menuvisual.py`, `paginas/menugeneral.py`

`menucfg.py` (the accessibility config menu) implements full keyboard navigation with K_RIGHT/K_LEFT and K_RETURN dispatch. The three sub-screens it can push (`menuauditivo`, `menuvisual`, `menugeneral`) have no keyboard-navigation code at all — their `handleEvents` methods contain no `K_RIGHT`, `K_LEFT`, or K_RETURN button-dispatch logic, and none call `_rebuild_nav()`. A user who has enabled keyboard navigation (precisely because they need it for accessibility) must switch to mouse interaction to complete configuration.

**Concrete recommendation:** Add keyboard navigation to all three config sub-screens following the same pattern used in `menucfg.py` and all content screens: `K_RIGHT`/`K_LEFT` advance focus and set `keyboard_nav_active = True`; `K_RETURN` while `keyboard_nav_active` dispatches through `button_actions`. Call `_rebuild_nav()` at the end of each `handleEvents`.

---

### SV2-077 — `pantalla10` (glossary) uses explicit `if/elif` button dispatch instead of the `button_actions` pattern

**Affected file:** `paginas/pantalla10.py:138-144`

```python
elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
    if sprite[0].id == "home":
        self.go_home()
    elif sprite[0].id == "back":
        self.clear_groups()
        self.parent.popState()
```

Every other screen delegates button clicks through a `button_actions` dict and a single `self.button_actions.get(sprite[0].id, lambda: None)()` call. `pantalla10` is the only exception — it uses a hard-coded `if/elif` chain. This inconsistency means adding a new button to the glossary requires editing the event handler rather than just extending the dict.

The screen also has no keyboard navigation (see SV2-076), so the K_ESCAPE handler (`self.go_home()` on line 116) provides only partial accessibility.

**Concrete recommendation:** Add `self.button_actions = {"home": self.go_home, "back": lambda: (self.clear_groups(), self.parent.popState())}` to `__init__`, replace the `if/elif` dispatch with the standard `self.button_actions.get(sprite[0].id, lambda: None)()`, and add K_RIGHT/K_LEFT keyboard navigation.

---

### SV2-078 — `keyboard_nav_active` is not set on K_LEFT in three screens, making left-first navigation impossible

**Affected files:** `paginas/menucfg.py:152-153`, `paginas/pantalla2.py:165-166`, `paginas/pantalla8.py:129`

All content screens and `pantalla11` set `self.keyboard_nav_active = True` for *both* K_RIGHT and K_LEFT. Three screens set it only for K_RIGHT:

- `menucfg.py:149-153` — K_RIGHT sets it, K_LEFT (`self.nav_left()`) does not
- `pantalla2.py:162-166` — same asymmetry
- `pantalla8.py:124-129` — same asymmetry

A user who presses ← first (perhaps navigating toward the rightmost item via wrap-around) will activate `nav_left()` without enabling `keyboard_nav_active`. The focus rectangle is never drawn, the K_RETURN handler never fires, and the user cannot activate any element via keyboard.

**Concrete recommendation:** Add `self.keyboard_nav_active = True` to the K_LEFT branch in `menucfg.py`, `pantalla2.py`, and `pantalla8.py`, matching the pattern used in `pantalla3–6`, `pantalla11`.

---

### SV2-079 — `pantalla11.load_texts()` has a TTS side-effect

**Affected file:** `paginas/pantalla11.py:89-95`

`load_texts()` is called from `__init__` to create `Text` and `_audience_texts` objects. Its first action is a `speech_server.processtext()` call:

```python
def load_texts(self):
    self.speech_server.processtext(
        "Pantalla: Orientaciones y Sugerencias: …",
        self.parent.config.is_screen_reader_enabled(),
    )
    font_size = self.parent.config.get_font_size()
    …
```

A method named `load_texts` should only build data structures. The TTS announcement is a side-effect that will fire every time `load_texts` is invoked — including when the font size changes and `load_texts` is called again from `resume()` if a `text_change_enabled` guard were added (see SV2-069). The coupling also makes the method hard to test or reuse.

**Concrete recommendation:** Move the `speech_server.processtext()` call out of `load_texts()` into `resume()` (where the equivalent TTS announcements live in all other content screens).
