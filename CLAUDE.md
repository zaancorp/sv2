# sv2 — Sembrando para el futuro

Educational accessibility app built with Python + Pygame, targeting plant biology education for students with disabilities.

## Project structure

```
src/
  inicio.py              # Entry point — main() loop
  manejador.py           # State machine (Manager class)
  components/            # Shared modules / library classes
    configuration.py     # User preferences (loads/saves user_config.json)
    text_repository.py   # Loads paginas/text/content.json (LRU-cached)
    text_loader.py       # TextLoader — nested key accessor for text content
    screen.py            # Base class for all screens (Screen)
    texto.py             # Text rendering
    image.py             # Image sprite
    button.py            # Button sprite
    animations.py        # Animation helpers
    magnifier.py         # Screen magnifier
    speechserver.py      # TTS / screen reader server (currently stubbed)
    singleton.py         # Singleton metaclass
    words.py             # Word sprite + TextType enum + FontManager
    ...
  paginas/               # Screen modules
    menucfg.py           # Accessibility config menu (first screen loaded)
    menuauditivo.py      # Audio disability menu
    menuvisual.py        # Visual disability menu
    menugeneral.py       # General settings menu (language, etc.)
    pantalla2.py ...     # Content screens (plants unit)
    actividad1.py ...    # Activities
    playground.py        # Dev playground (uncomment in inicio.py to use)
    text/
      content.json       # All user-facing text (concepts, screen content, popups, ui)
  user_config.json       # Runtime user preferences (gitignored in practice)
```

## Running

```bash
# Install dependencies
poetry install

# Run the app (must run from project root — assets use relative paths from src/)
poetry run python src/inicio.py
```

Window: 1024×572 px, 30 fps. Pass `fullscreen=True` in `Manejador.__init__` to go fullscreen.

## Architecture

**Screen state machine** (`Manager` in `manejador.py`):
- `changeState(state)` — replaces current screen (cleans up old one)
- `pushState(state)` — overlays a new screen (pauses current)
- `popState()` — removes top screen and resumes previous
- Each screen is a subclass of `screen.Screen` with `start()`, `resume()`, `pause()`, `cleanUp()`, `handleEvents()`, `update()`, `draw()`
- `Manager` is a Singleton

**Text content** (`content.json`):
- Single source of truth for all Spanish UI text
- Loaded once at startup via `load_text_content()` (LRU-cached), stored on `Manejador` as `text_content` and `text_loader`
- Access via `self.parent.text_content["content"]["screen_N"]["text_K"]` or the `TextLoader` API:
  - `text_loader.get("content", "screen_3", "text_2")` — safe access with default
  - `text_loader.require(...)` — raises `KeyError` if missing
  - `text_loader.screen_content("screen_3")` — shortcut
  - `text_loader.concept("fotosintesis")` — glossary concept
  - `text_loader.ui(...)` — UI strings

**Configuration** (`Configuration`):
- Reads/writes `user_config.json` relative to cwd (i.e., `src/`)
- Key preferences: `color`, `t_fuente`, `vel_anim`, `audio`, `magnificador`, `activar_lector`, `genero`, `synvel`, `text_change`, `visited_screens`

## Key conventions

- All screen classes are named `Screen` and live in `paginas/`
- Assets (images, icons, sounds) are referenced relative to `src/` (e.g., `./iconos/`, `./backgrounds/`, `./banners/`)
- UI text lives in `content.json` — never hardcode strings in screen files
- New text must be added to `content.json` under the appropriate key before referencing it in code
- Access text through `self.parent.text_loader` (not raw `text_content` dict) — it has safe key traversal and clear error messages
- `Manager.DRAW_DEBUG_RECTANGLES = True` enables visual debug overlays

## Known issues / design notes

- **`actividad1.py` sprite groups are class-level** (SV2-023): all groups in the activity screen (`button_group`, `anim_group`, etc.) are shared across instances. Fragile when the screen is pushed onto the stack. All other screens use instance-level groups.
- **TTS is non-functional** (SV2-028): every method in `Speechserver` is a no-op stub. The screen-reader accessibility feature is silently inert.

## Issue tracking

Issues are tracked as `SV2-NNN` identifiers:
- **Open issues** live in `ANALYSIS.md` — one section per issue.
- **Resolved issues** live in `CHANGELOG.md` — one entry per issue, in reverse chronological order.

When an issue is fixed, move its section from `ANALYSIS.md` to `CHANGELOG.md` and assign it the next SV2-NNN number in sequence. Do not leave resolved issues in `ANALYSIS.md`.

## See also

- `ANALYSIS.md` — open issues only
- `CHANGELOG.md` — resolved issues and architectural improvements

## Dependencies

- **Python** ≥ 3.13.7
- **pygame** ^2.6.1
- **numpy** ^2.4.2
- Managed with **Poetry** (`pyproject.toml`)
