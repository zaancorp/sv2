# Text Content in Python — Analysis and Migration Plan

This document analyzes where text content is embedded in Python structures (classes, dicts, modules) and outlines a plan to centralize all text in JSON with a text loader.

---

## 1. Current State Overview

### 1.1 Existing JSON Infrastructure

`src/paginas/text/content.json` already exists and contains:

| Section | Purpose | Used By |
|---------|---------|---------|
| `concepts` | Glossary definitions (concept_id → definition text) | pantalla3, 4, 5, 6, 8, 10 |
| `content` | Screen-specific content by `screen_id` (text_2, anim_1, etc.) | pantalla2–11, pantalla5, 6, 8, 9 |
| `popups` | Screen-specific popup/reader text (text_1, reader_1, text_magnifier) | menucfg, pantalla2, pantalla9 (partial) |

Text is loaded in `Manejador.load_text_content()` and exposed as `self.parent.text_content`.

### 1.2 Duplication: textopopups.py vs content.json

`src/librerias/textopopups.py` defines `p1`, `p1_vis`, `p2`, `p9` dicts that **duplicate** content already in `content.json`:

| textopopups key | content.json equivalent | Used by |
|-----------------|-------------------------|---------|
| `p1` | `popups.screen_1` | menucfg (commented), pantalla2 (commented) |
| `p1_vis` | `popups.screen_1_reader.text_magnifier` | menuvisual |
| `p2` | `popups.screen_2` | Not directly used (content.json used instead) |
| `p9` | `popups.screen_9` | pantalla9 |

**Finding:** `textopopups.py` is redundant. `content.json` popups already cover this. pantalla9 still uses `p9` from textopopups; menuvisual uses `p1_vis`.

---

## 2. Inventory: Text Embedded in Python

### 2.1 Dedicated Data Modules (pure text structures)

| File | Structure | Content Type | ~Items |
|------|-----------|--------------|--------|
| **`librerias/textopopups.py`** | `p1`, `p1_vis`, `p2`, `p9` dicts | Popup / reader strings | 4 screens |
| **`librerias/prp.py`** | `dic_pr`, `dic_pre`, `dic_res`, `dic_res_lector`, `dic_pistas`, `r_correcta`, `instruc`, `marcas_n1`, `marcas_n2` | Activity 1: questions, answers, hints, instructions, markers | 10 questions + level markers |
| **`librerias/palabra.py`** | `ENTRIES`, `DEFINITIONS` | Word → concept code mappings | ~15 entries each |
| **`librerias/object.py`** | `PropObject.aumentos` | Tooltip labels for objects | 6 items |

### 2.2 Inline in Screen/Activity Classes

| File | Location | Content Examples |
|------|----------|------------------|
| **`paginas/menuauditivo.py`** | `__init__`, Text() calls | "Configuración de discapacidad auditiva.", "1.- ¿Te gustaría hacer el recorrido con un intérprete virtual?", "Sí No", "2.- Selecciona el género del intérprete...", "Pulsa sobre el botón guardar..." |
| **`paginas/menuvisual.py`** | `__init__`, Text() calls, PopUp, variables | "1.- ¿Te gustaría hacer el recorrido con un Magnificador...", "Sí No", "Pulsa sobre el botón guardar...", `instrucciones`, `pregunta1`, `pregunta2`, plus `p1_vis["texto_mag"]` |
| **`paginas/pantalla10.py`** | `cargar_textos()` | "A B C D E...", glossary term labels (Absorber, Célula, etc.) |
| **`paginas/pantalla11.py`** | `cargar_textos()` spserver call | "Pantalla: Orientaciones y Sugerencias: Pulsa sobre cada botón..." — inline screen reader string |
| **`paginas/actividad1.py`** | Various | "Siembra la semilla", "Pulsa la tecla F1...", "¡Muy bien! Has finalizado...", prp.instruc, prp.dic_pistas, prp.marcas_n1/n2, sound descriptions, popup strings |
| **`paginas/actividad2.py`** | `__init__`, nivel1/2/3 | instruccion1, texto, texto_ayuda, pregunta, pregunta_lector, texto_bien, texto_mal, texto_vacio, "Pulsa enter...", "escribe tu respuesta..." |

### 2.3 Screen Reader / Caption Announcements (inline strings)

| File | String |
|------|--------|
| pantalla3.py | "Pantalla: Las Plantas" |
| pantalla4.py | "Pantalla: Partes de una planta" |
| pantalla5.py | "Pantalla: Reproducción de las plantas." |
| pantalla8.py | "Pantalla: La Agricultura en Venezuela: " |
| pantalla9.py | "Pantalla: La Agricultura en Venezuela: " |
| pantalla11.py | "Pantalla: Orientaciones y Sugerencias: ..." (in cargar_textos) |
| pantalla11.py | "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. " |
| pantalla11.py | "Fin de contenido, regresa al menú. " |

### 2.4 Object/Label Mappings (object.py, actividad1)

- **`object.py`**: `aumentos` keys like "la carretilla. ", "las semillas. ", "el controlador biológico. "
- **`actividad1.py`**: PropObject `nombre` args, e.g. "la pala. ", "el abono. ", "el controlador biológico. " — these match `aumentos` keys

---

## 3. Proposed JSON Structure

Extend `content.json` (or split into multiple files) with these sections:

```json
{
  "concepts": { ... },
  "content": { ... },
  "popups": { ... },

  "activity1": {
    "screen_title": "Siembra la semilla",
    "questions": {
      "0": {
        "question": "...",
        "options": ["1. Tallo ", "2. Flor ", "3. Raíz "],
        "options_reader": ["1. Tallo. ", "2. Flor. ", "3. Raíz. "],
        "correct": "3. Raíz ",
        "hints": ["...", "...", "¡Muy bien! Sabías que..."]
      }
    },
    "instructions": {
      "text": "...",
      "reader": "..."
    },
    "markers": {
      "nivel1": { "semilla": ["...", "..."], "regadera": [...] },
      "nivel2": { ... }
    },
    "popups": {
      "instruc": "...",
      "final_nivel1": "...",
      "sonido_correcto": "...",
      "sonido_obstaculo": "...",
      "nivel1_intro": "...",
      "nivel2_intro": "...",
      "final_recoleccion": "...",
      "excelente_salir": "...",
      "enunciado_pregunta": "Selecciona la opción que corresponde al siguiente enunciado: "
    }
  },

  "activity2": {
    "instructions": {
      "f1": "...",
      "main": "..."
    },
    "niveles": {
      "1": {
        "pregunta": "...",
        "pregunta_lector": "...",
        "texto_bien": "...",
        "texto_mal": "...",
        "texto_vacio": "...",
        "texto_ayuda": "..."
      },
      "2": { ... },
      "3": { ... }
    },
    "common": {
      "enter_confirmar": "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
      "terminaste": "Terminaste todos los problemas! Pulsa enter para volver al menú del recurso.",
      "siguiente": "Pulsa enter para pasar al siguiente problema."
    }
  },

  "word_mappings": {
    "entries": { "absorbe": "absorber", "célula": "celula", ... },
    "definitions": { "Absorber": "absorber", "Célula": "celula", ... }
  },

  "glossary_index": {
    "labels": ["A B C D E ...", "Absorber ", "Célula ", ...],
    "order": ["a_absorber", "c_celula", ...]
  },

  "config_screens": {
    "auditory": {
      "title": "Configuración de discapacidad auditiva.",
      "prompts": {
        "interpreter": "1.- ¿Te gustaría hacer el recorrido con un intérprete virtual? ",
        "gender": "2.- Selecciona el género del intérprete con el que desees hacer el recorrido. ",
        "color_m": "3.- Elige el color de la camisa del intérprete virtual.  ",
        "color_f": "3.- Elige el color de la camisa de la intérprete virtual.  ",
        "speed_m": "4.- Elige la velocidad del intérprete virtual. ",
        "speed_f": "4.- Elige la velocidad de la intérprete virtual. ",
        "save": "Pulsa sobre el botón guardar para salvar tu configuración. "
      },
      "options": { "sino": "Sí            No ", "fm": "F             M " }
    },
    "visual": {
      "title": "1.- ¿Te gustaría hacer el recorrido con un Magnificador de Pantalla? ",
      "prompts": { ... },
      "reader_prompts": {
        "instrucciones": "Pantalla: Discapacidad visual: Instrucciones: ...",
        "pregunta1": "¿Deseas activar el lector de pantalla? ...",
        "pregunta2": "Elige la velocidad del lector de pantalla: ..."
      },
      "config_success": "Has configurado el lector de pantalla exitosamente, presiona enter para continuar. "
    }
  },

  "screen_readers": {
    "screen_3": "Pantalla: Las Plantas",
    "screen_4": "Pantalla: Partes de una planta",
    "screen_5": "Pantalla: Reproducción de las plantas.",
    "screen_8": "Pantalla: La Agricultura en Venezuela: ",
    "screen_9": "Pantalla: La Agricultura en Venezuela: ",
    "screen_11": {
      "intro": "Pantalla: Orientaciones y Sugerencias: Pulsa sobre cada botón...",
      "siguiente": "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. ",
      "fin": "Fin de contenido, regresa al menú. "
    }
  },

  "objects": {
    "prop_labels": {
      "carretilla": "la carretilla. ",
      "semillas": "las semillas. ",
      "regadera": "la regadera. ",
      "pala": "la pala. ",
      "abono": "el abono. ",
      "controlador_biologico": "el controlador biológico. "
    }
  }
}
```

---

## 4. Text Loader Design

### 4.1 API

```python
# src/librerias/text_loader.py

class TextLoader:
    def __init__(self, content: dict):
        self._content = content

    def get(self, *keys, default=None):
        """Navigate nested dict: loader.get("activity1", "questions", "0", "question")"""
        ...

    def screen_content(self, screen_id: str) -> dict:
        """Shortcut for content["content"][screen_id]"""
        ...

    def concept(self, concept_id: str) -> str:
        """Shortcut for concepts[concept_id]"""
        ...

    def popup(self, screen_id: str, key: str = "text_1") -> str:
        """Shortcut for popups[screen_id][key]"""
        ...

    def activity1_question(self, idx: int) -> dict:
        """Shortcut for activity1.questions[str(idx)]"""
        ...

    def config_screen(self, screen_type: str) -> dict:
        """Shortcut for config_screens[auditory|visual]"""
        ...
```

### 4.2 Integration

- Keep loading in `Manejador.load_text_content()`.
- Add `TextLoader(self.text_content)` and store as `self.text_loader` (or wrap `text_content` with helper methods).
- Screens receive loader via `self.parent.text_loader` or `self.parent.text_content` (backward compatible during migration).

---

## 5. Migration Plan

### Phase 1: Infrastructure (low risk)

1. **Create `TextLoader`** in `src/librerias/text_loader.py`.
2. **Integrate in Manejador** — after `load_text_content()`, build `TextLoader` (optional: also expose `text_content` for gradual migration).
3. **Add `screen_readers` section** to content.json and migrate inline "Pantalla: ..." strings from pantalla3, 4, 5, 8, 9, 11.
4. **Remove `textopopups.py`** — replace `p1_vis`, `p9` usage with `text_content["popups"]`. content.json already has equivalent data.

**Deliverables:** TextLoader in use, screen reader strings in JSON, textopopups.py removed.

---

### Phase 2: Configuration Screens (medium effort)

5. **Add `config_screens`** to content.json with menuauditivo and menuvisual texts.
6. **Refactor menuauditivo.py** — replace inline strings with loader calls.
7. **Refactor menuvisual.py** — replace inline strings and `p1_vis` with loader calls.

**Deliverables:** menuauditivo and menuvisual fully driven by JSON.

---

### Phase 3: Activity 1 (highest effort)

8. **Add `activity1`** to content.json (questions, hints, instructions, markers).
9. **Refactor `prp.py`** — load from `parent.text_content["activity1"]` instead of class attributes; or deprecate prp and use loader directly in actividad1.
10. **Refactor actividad1.py** — replace prp usage and inline strings with loader.

**Deliverables:** prp.py reduced to a thin wrapper or removed; activity1 texts in JSON.

---

### Phase 4: Activity 2

11. **Add `activity2`** to content.json.
12. **Refactor actividad2.py** — replace all `self.pregunta`, `self.texto_bien`, etc. with loader calls.

---

### Phase 5: Glossary and Word Mappings (lower priority)

13. **Add `word_mappings`** to content.json (ENTRIES, DEFINITIONS from palabra.py).
14. **Refactor palabra.py** — load mappings from JSON (or keep as fallback if not found).
15. **Add `glossary_index`** for pantalla10 labels — or derive from word_mappings + concepts.
16. **Refactor pantalla10.py** — load labels from JSON.
17. **Add `objects.prop_labels`** — migrate object.py `aumentos` keys; optionally keep values in Python if they are numeric.

---

## 6. Summary Table

| Source | Content Type | JSON Target | Phase |
|--------|--------------|-------------|-------|
| textopopups.py | p1, p1_vis, p2, p9 | popups (existing) | 1 |
| pantalla3–11 | "Pantalla: ..." | screen_readers | 1 |
| menuauditivo.py | Config prompts | config_screens.auditory | 2 |
| menuvisual.py | Config prompts | config_screens.visual | 2 |
| prp.py | Questions, hints, markers | activity1 | 3 |
| actividad1.py | Inline popups, captions | activity1.popups | 3 |
| actividad2.py | Questions, feedback | activity2 | 4 |
| palabra.py | ENTRIES, DEFINITIONS | word_mappings | 5 |
| pantalla10.py | Glossary labels | glossary_index | 5 |
| object.py | Prop labels (aumentos keys) | objects.prop_labels | 5 |

---

## 7. File Changes Overview

| Action | File(s) |
|--------|---------|
| Create | `src/librerias/text_loader.py` |
| Extend | `src/paginas/text/content.json` |
| Modify | `src/manejador.py` (add TextLoader) |
| Delete | `src/librerias/textopopups.py` (after Phase 1) |
| Refactor | menuauditivo, menuvisual, actividad1, actividad2, pantalla3–11, pantalla10, palabra, object, prp |

---

## 8. Recommended Starting Point

Begin with **Phase 1**:

1. Implement `TextLoader`.
2. Add `screen_readers` to content.json.
3. Replace inline "Pantalla: ..." in pantalla3, 4, 5, 8, 9, 11.
4. Switch pantalla9 from `p9` to `parent.text_content["popups"]["screen_9"]`.
5. Switch menuvisual from `p1_vis` to `parent.text_content["popups"]["screen_1_reader"]`.
6. Remove `textopopups.py` and its imports.

This yields immediate wins: unified text source, no duplicate popup data, and a pattern for the rest of the migration.
