# sv2 — Sembrando para el futuro

Educational accessibility app built with Python + Pygame, targeting plant biology education for students with disabilities.

## Project structure

```
src/
  inicio.py              # Entry point — main() loop
  manejador.py           # State machine (Manejador class)
  librerias/             # Shared modules / library classes
    configuration.py     # User preferences (loads/saves user_config.json)
    text_repository.py   # Loads paginas/text/content.json (LRU-cached)
    text_loader.py       # TextLoader — nested key accessor for text content
    pantalla.py          # Base class for all screens (Pantalla)
    texto.py             # Text rendering
    imagen.py / image.py # Image sprite
    button.py            # Button sprite
    animations.py        # Animation helpers
    magnificador.py      # Screen magnifier
    speechserver.py      # TTS / screen reader server
    singleton.py         # Singleton metaclass
    ...
  paginas/               # Screen modules
    menucfg.py           # Accessibility config menu (first screen loaded)
    menuauditivo.py      # Audio disability menu
    menuvisual.py        # Visual disability menu
    pantalla2.py ...     # Content screens (plants unit)
    actividad1.py ...    # Activities
    playground.py        # Dev playground (uncommented in inicio.py to use)
    text/
      content.json       # All user-facing Spanish text (concepts, screen content, popups, ui)
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

**Screen state machine** (`Manejador`):
- `changeState(estado)` — replaces current screen (cleans up old one)
- `pushState(estado)` — overlays a new screen (pauses current)
- `popState()` — removes top screen and resumes previous
- Each screen is a subclass of `pantalla.Pantalla` with `start()`, `resume()`, `pause()`, `cleanUp()`, `handleEvents()`, `update()`, `draw()`
- `Manejador` is a Singleton

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

- All screen classes are named `estado` and live in `paginas/`
- Assets (images, icons, sounds) are referenced relative to `src/` (e.g., `./iconos/`, `./backgrounds/`, `./banners/`)
- UI text is **always** in Spanish and lives in `content.json` — never hardcode strings in screen files
- New text must be added to `content.json` under the appropriate key before referencing it in code
- Access text through `self.parent.text_loader` (not raw `text_content` dict) — it has safe key traversal and clear error messages
- `Manejador.DRAW_DEBUG_RECTANGLES = True` enables visual debug overlays

## Known issues / design notes

- **Singleton is broken**: `Manejador` declares `__metaclass__ = Singleton` (Python 2 syntax — silently ignored in Python 3). Only one instance should ever be created; this is enforced by convention, not code.
- **Pantalla sprite groups are class-level**: all groups (`grupo_anim`, `grupo_botones`, etc.) are shared across all screen instances. Works because only one screen is normally active at once, but fragile when using `pushState`.
- **Two text-access styles coexist**: older screens use raw `self.parent.text_content["content"][screen][key]`, newer ones use `text_loader`. Prefer `text_loader`.
- **Dead config keys**: `user_config.json` contains unused `texto_cambio` and `visit` keys left over from earlier versions.
- **`Button.parent` is the `Manejador` class, not an instance**: `button.py` imports `Manejador as parent` and assigns it to `self.parent`. Works only because `config` is a class-level attribute on `Manejador`.

## See also

- `ANALYSIS.md` — in-depth architectural analysis with anti-patterns and improvement roadmap

## Dependencies

- **Python** ≥ 3.13.7
- **pygame** ^2.6.1
- **numpy** ^2.4.2
- Managed with **Poetry** (`pyproject.toml`)
