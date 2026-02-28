# Technical Improvement Suggestions

**Project:** Sembrando para el futuro (sv2)  
**Analysis Date:** February 2025  
**Stack:** Python 3.9, Pygame, Pipenv

---

## Executive Summary

This is an educational accessibility application built with Pygame, featuring screen magnification, text-to-speech (screen reader), keyboard navigation, and sign language interpreter integration. The codebase has a solid State pattern architecture for screen management but several technical debt items and potential runtime bugs that should be addressed.

---

## 1. Critical Bugs

### 1.1 Missing `consultar()` Method

**Location:** `Configuration` class in `src/librerias/configuration.py`

The method `consultar()` is invoked in multiple places but **does not exist** in the Configuration class:

- `src/manejador.py:148`
- `src/paginas/menuauditivo.py:131`, `230`
- `src/paginas/menuvisual.py:152`, `322`, `343`

**Impact:** `AttributeError` at runtime when accessibility features are used.

**Suggestion:** Add the missing method. Based on usage context (called when opening interpreter/visual/auditory menus), it likely syncs interpreter or voice settings. Implement or remove the calls.

---

### 1.2 `config.definicion` Attribute

**Location:** `src/manejador.py:187`, `src/paginas/pantalla10.py:40-45`

Code sets `self.config.definicion = codigo` and reads it in pantalla10. The `Configuration` class stores data in `self.preferences` and does not define `definicion` as an attribute. This works by dynamic attribute assignment but is fragile.

**Suggestion:** Add `definicion` to the configuration schema—either as a proper preference with `get_preference`/`set_preference` or as an explicit instance attribute in `__init__`.

---

### 1.3 Bare `except:` Clauses

**Locations:**

- `src/manejador.py:182` – Blender interpreter subprocess
- `src/paginas/actividad1.py:645` – Popup value handling

Bare `except:` catches all exceptions (including `KeyboardInterrupt`, `SystemExit`) and can hide real errors.

**Suggestion:** Replace with specific exceptions, e.g.:

```python
except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
    print(f"No se ha podido cargar el interprete virtual: {e}")
```

```python
except (KeyError, IndexError) as e:
    print(f"Valor fuera de rango: {e}")
```

---

## 2. Path and File Resolution

### 2.1 Relative Paths Depend on CWD

Paths like `./iconos/`, `./interprete/`, `paginas/text/content.json`, `user_config.json` assume the process is run from `src/`. Running from the project root will cause `FileNotFoundError`.

**Locations:**

- `src/manejador.py:55` – `./iconos/sembrando96x96.png`
- `src/manejador.py:193` – `paginas/text/content.json`
- `src/librerias/configuration.py:12` – `user_config.json`
- `src/librerias/button.py:271` – `../imagenes/png/varios/`
- `src/librerias/cajatexto.py:79-87` – `../imagenes/png/varios/`
- `src/librerias/personaje.py:33` – `../imagenes/png/varios/`

**Suggestion:** Use path resolution based on the package/module location:

```python
import os

# At the top of configuration.py or a shared paths module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Then use:
config_file = os.path.join(BASE_DIR, "user_config.json")
icon_path = os.path.join(BASE_DIR, "iconos", "sembrando96x96.png")
```

This keeps paths correct regardless of the current working directory.

---

### 2.2 Duplicate `user_config.json`

`user_config.json` exists in both `src/` and `src/librerias/`. With a relative path, which file is used depends on CWD, risking inconsistent or duplicated config.

**Suggestion:** Use a single canonical location (e.g. `src/user_config.json`) and resolve it via `BASE_DIR` as above.

---

### 2.3 Python 2 Cache Reference

**Location:** `src/manejador.py:153`

References `interprete.cpython-32.pyc` (Python 2 32-bit). The project targets Python 3.9.

**Suggestion:** Remove or generalize the cache cleanup logic. For Python 3, cache files use names like `interprete.cpython-39.pyc`. Consider `shutil.rmtree("./interprete/__pycache__", ignore_errors=True)` or skipping manual cleanup and relying on `pycache` behavior.

---

## 3. Code Style and Modernization

### 3.1 Python 2 Metaclass Syntax

**Location:** `src/manejador.py:22`

```python
__metaclass__ = Singleton  # Python 2 style
```

**Suggestion:** Use Python 3 syntax:

```python
class Manejador(metaclass=Singleton):
```

---

### 3.2 Singleton Implementation

**Location:** `src/librerias/singleton.py`

The implementation is correct but uses old-style `super(Singleton, self)`. Consider using `super()` without arguments (Python 3) and adding thread-safety if the app may use multiple threads.

---

### 3.3 Class-Level Side Effects

**Location:** `src/manejador.py:55-56`

```python
icon = pygame.image.load("./iconos/sembrando96x96.png")
pygame.display.set_icon(icon)
```

These run at import/class definition time, before `pygame.init()` in `__init__`. Loading images before `pygame.init()` can cause issues on some platforms.

**Suggestion:** Move icon loading into `__init__` after `pygame.init()`.

---

### 3.4 Duplicate Key in `assets_data.py`

**Location:** `src/librerias/assets_data.py:314-326`

The key `"boton_or_padres"` is defined twice. The second definition overwrites the first.

**Suggestion:** Remove the duplicate and keep a single entry.

---

## 4. Testing and Quality Assurance

### 4.1 No Automated Tests

The project has no test files (e.g. `test_*.py`, `*_test.py`).

**Suggestion:**

1. Add `pytest` to dev dependencies.
2. Start with unit tests for pure logic (e.g. `Configuration`, path helpers).
3. Add integration tests for state transitions and screen loading.
4. Consider `pytest-pygame` or similar for UI-related tests.

---

### 4.2 Linting and Formatting

No `pyproject.toml`, `setup.cfg`, or lint config (e.g. ruff, flake8, black) was found.

**Suggestion:** Add a `pyproject.toml`:

```toml
[project]
name = "sv2"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["pygame", "numpy"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Use `ruff` for linting/formatting and run it in CI.

---

## 5. Dependency Management

### 5.1 Pipfile Location

`Pipfile` and `Pipfile.lock` live under `src/` instead of the project root. This is unconventional and can confuse tooling.

**Suggestion:** Move `Pipfile` and `Pipfile.lock` to the repository root (`/home/fran/Projects/zaancorp/sv2/`).

---

### 5.2 Dependency Pinning

`Pipfile` uses `pygame = "*"` and `numpy = "*"`, so any version can be installed.

**Suggestion:** Pin versions for reproducibility, e.g.:

```
[packages]
pygame = ">=2.5.0,<3.0"
numpy = ">=1.24,<2.0"
```

---

## 6. Architecture and Design

### 6.1 Speech Server Stub

`Speechserver` in `src/librerias/speechserver.py` is effectively a no-op: implementations are commented out. Screen reader support is currently disabled.

**Suggestion:** Either:

1. Re-enable and adapt the original implementation (e.g. speech-dispatcher), or  
2. Document that TTS is disabled and consider alternative backends (e.g. pyttsx3, gTTS) for portability.

---

### 6.2 Configuration Save Frequency

`Configuration.set_preference()` and `update_preferences()` call `save_config()` on every change. Frequent I/O can add latency and wear on storage.

**Suggestion:** Implement debounced or explicit saves:

- Batch updates and save on screen exit or application shutdown.
- Or add a `dirty` flag and save periodically or on explicit `save_config()`.

---

### 6.3 Magic Numbers and Constants

**Examples:**

- `src/manejador.py:126` – `tick(30)` (target FPS)
- `src/manejador.py:164-166` – interpreter window size `"512", "372", ...`
- `src/inicio.py:12` – `(1024, 572)` screen size

**Suggestion:** Extract to named constants or config:

```python
TARGET_FPS = 30
SCREEN_SIZE = (1024, 572)
INTERPRETER_WINDOW_SIZE = (512, 372)
```

---

## 7. Documentation and Maintainability

### 7.1 Empty README

`README.md` is empty.

**Suggestion:** Add at least:

- Short project description
- Prerequisites (Python 3.9+, pipenv, optional: Blender, wmctrl, speech-dispatcher)
- How to install and run (e.g. `cd src && pipenv run python inicio.py`)
- Basic configuration notes

---

### 7.2 Outdated Docstring Style

Docstrings use `@param` and `@type` (Epydoc style). Many IDEs and tools favor Google- or NumPy-style docstrings.

**Suggestion:** Standardize on one style. Example (Google style):

```python
def changeState(self, gameState):
    """Load a new screen, replacing the current one.

    Args:
        gameState: The screen state to load.
    """
```

---

### 7.3 Spanish/English Mix

Code and comments mix Spanish and English. Not wrong, but consistency improves readability.

**Suggestion:** Choose a primary language (e.g. Spanish for user-facing strings, English for code/comments) and apply it consistently.

---

## 8. Security and Robustness

### 8.1 External Command Execution

**Location:** `src/manejador.py`

Uses `subprocess.Popen`, `subprocess.call`, `pgrep`, `pkill`, `wmctrl` with user/configurable inputs (`codigo`, `self.config.color`, etc.). Ensure these values cannot be abused for injection.

**Suggestion:** Validate/sanitize any values passed to shell commands. Prefer `subprocess` with list arguments (no shell) to avoid shell injection.

---

### 8.2 Platform Assumptions

Use of `wmctrl` and `blenderplayer` implies a Linux desktop environment.

**Suggestion:** Document supported platforms and add graceful fallbacks or clearer errors when tools are missing (e.g. `wmctrl` not installed).

---

## 9. Prioritized Action Summary

| Priority | Item                                      | Effort |
|----------|-------------------------------------------|--------|
| P0       | Add or fix `consultar()` in Configuration | Low    |
| P0       | Fix bare `except:` clauses                | Low    |
| P1       | Path resolution (BASE_DIR)                | Medium |
| P1       | Move icon loading into `__init__`         | Low    |
| P1       | Fix `config.definicion` handling          | Low    |
| P2       | Add `pyproject.toml` + lint config        | Low    |
| P2       | Introduce basic tests                     | Medium |
| P2       | Populate README                           | Low    |
| P3       | Move Pipfile to project root              | Low    |
| P3       | Pin dependencies                          | Low    |
| P3       | Speech server implementation or docs      | Medium |

---

## Appendix: Project Structure Overview

```
sv2/
├── src/
│   ├── inicio.py              # Entry point
│   ├── manejador.py           # State manager (Singleton)
│   ├── Pipfile, Pipfile.lock  # Dependencies (consider moving to root)
│   ├── user_config.json       # User preferences
│   ├── librerias/             # Shared utilities
│   │   ├── configuration.py  # Config manager
│   │   ├── pantalla.py       # Base screen class
│   │   ├── speechserver.py   # TTS (currently stubbed)
│   │   ├── singleton.py
│   │   └── ...
│   └── paginas/              # Screen states
│       ├── menucfg.py
│       ├── menuauditivo.py
│       ├── menuvisual.py
│       ├── pantalla*.py
│       └── text/content.json
├── AUTHORS, COPYING, LICENSE
└── README.md (empty)
```

Gitignored assets: `iconos/`, `imagenes/`, `audio/`, `interprete/`, `paquetes/`
