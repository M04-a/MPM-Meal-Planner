# Meal Planner & Pantry Tracker – Documentation (EN)

This project provides a web application (FastAPI + Jinja2) for:
- Pantry management (ingredients with quantities, units, expiry dates, tags)
- Recipe management (ingredients, steps, nutrition, images)
- Weekly meal planning (breakfast / lunch / dinner, by day)
- Shopping list generation from the plan (subtracting pantry items)
- Purchases (marking items as bought and consolidating ingredients)
- Cooked meal tracking
- Weekly nutrition summary calculation
- Low-stock and near-expiry alerts (via EventBus + web buffer)

---

## 1. Project Structure
```
meal/
  main.py                  # Uvicorn startup (simple entry point)
  api/                     # HTTP layer (FastAPI) + template pages
    api_run.py             # FastAPI instance, HTML pages, JSON endpoints
    routes/                # Logical subroutes: recipes, pantry, logs, add, ...
  domain/                  # Core entities (Ingredient, Recipe, Plan, Pantry, ...)
  infra/                   # JSON persistence + PDF utilities
  rules/                   # Business logic (shopping list builder, planning strategies)
  services/                # Service facades – TODO
  events/                  # Event Bus + web observers
  utilities/               # Constants & helpers
  static/                  # CSS, JS, images, thumbnails
  templates/               # Jinja2 HTML templates
  tests/                   # Unit / API tests (partial)
  data/                    # Persistent JSON files
```
There is also an earlier file `README-Meal-Planner-and-Pantry.md` (English summary).  
This document (`README_EN.md`) is the **extended and up-to-date version**.

---

## 2. Domain Entities (`domain/` folder)
### Ingredient
Fields: `name`, `unit`, `default_quantity`, `expiry_date`, `tags`
Methods: `set_quantity(delta)`, `from_dict`, `to_dict`, `__str__`

### Recipe
Fields: `name`, `servings`, `ingredients` (list of Ingredient), `steps`, `tags`, `calories_per_serving`, `macros`
Features: dict conversion, JSON read (`read_from_json`), ingredient availability check (`check_ingredients`), cooking simulation (`cook`) – consumes ingredients and returns a `RecipeCooked`.

### RecipeCooked
Extends `Ingredient` (to treat leftovers as short-expiry ingredients). Adds `calories`.

### Pantry
Contains a list of `Ingredient` and an `EventBus` for notifications.  
On add / modify, it triggers:
- `pantry.low_stock` if quantity ≤ threshold per unit (`LOW_STOCK_THRESHOLD`)
- `pantry.near_expiry` if expiry date ≤ `DAYS_BEFORE_EXPIRY` days away  
Main methods: `add_item`, `remove_item`, `update_quantity`, `scan_and_notify`

### Plan
Structure: `week_number`, `year`, `meals` (dict: Day → { breakfast, lunch, dinner, date }).  
Dates are injected by the repository each time the plan is loaded.

---

## 3. Persistence & Infra (`infra/` folder)
Local JSON persistence (no DB). Key files in `meal/data/`:
- `recipes.json` – recipe catalog
- `Pantry_ingredients.json` – pantry inventory
- `Pantry_recipe_cooked.json` – cooked meals
- `plan.json` – weekly plans keyed by `YYYY-Www`
- `shopping_transactions.json` – purchase history (append/merge)

Repositories:
- `Plan_Repository.py` – creates/maintains weekly plan structure (fills dates, randomizes weeks).  
  Saves without `date` (derived on load).  
- `Recipe_Repository.py` / `Pantry_Repository.py` – basic JSON readers (some partially replaced by modern API routes).

`pdf_utils.generate_pdf_for_week(plan)` – exports the weekly plan to PDF (A4 landscape, ReportLab).

---

## 4. Events (`events/` folder)
`Event_Bus.py` implements a simple Observer-style bus. Used events:
- `pantry.low_stock`
- `pantry.near_expiry`
- `pantry.expiring_snapshot` (periodic snapshot / on page access)

`web_observers.py` subscribes to the first two and keeps an in-memory ring buffer for AJAX polling (`/api/pantry/alerts`).  
Response structure:
```json
{
  "events": [
    { "id": 1, "type": "pantry.low_stock", "ts": "...", "name": "...", "quantity": ..., "threshold": ..., "days_left": ... }
  ],
  "next_cursor": <last_id>
}
```
The client polls incrementally using `since=<next_cursor>`.

`event_helpers.py` provides sugar functions: `publish_low_stock`, `publish_near_expiry`, `publish_expiring_snapshot`.

---

## 5. Business Rules (`rules/` folder)

### Shopping_List_Builder
Main function: `build_shopping_list(plan, recipes, pantry, skip_past_days=False)`  
Returns a list of dicts: `{ name, unit, required, have, missing }` (only items with `missing > 0`).  
Features:
- Name normalization (case-insensitive, trimmed)
- Simple plural → singular stemming (`ies→y`, `oes→o`, `es/s→remove`)
- Can skip past days if `skip_past_days=True` and plan has `date`.

### TODO placeholders
- `Plan_Strategy.py` – Strategy Pattern (balanced / leftovers-first / budget)
- `Meal_State.py` – State Pattern (Planned → Cooked → Logged)
- `Recipe_Importer.py` – Template Method for multi-format import (JSON/YAML)

---

## 6. API & UI Layer (`api/` folder)

### `api_run.py`
Initializes FastAPI, mounts static files & templates, starts event observers.  
HTML Pages (Jinja2):
- `/` – dashboard: plan + alerts + nutrition
- `/meal-plan/{week}` – view a specific week
- `/shopping-list` – shopping list (optionally skipping past days)
- `/camara` – pantry status + cooked meals + alerts
- `/camara/edit` – pantry editor
- `/recipe/{recipe_name}` – recipe details
- `/recipes-page` – all recipes (with tag filter)
- `/add-recipe` – add recipe form (with image upload + Spoonacular nutrition fetch)

Main JSON endpoints:
- `GET /api/shopping-list` (params: `week`, `year`, `skip_past=1`)
- `GET /api/shopping-list/current` – current week shortcut
- `POST /api/shopping-list/buy` – mark list as bought (merges into pantry JSON, logs transaction)
  - Normalizes + stems names
  - Merges items with same expiry
  - Creates new ingredients if missing
  - Skips items with no `missing`
- `GET /api/pantry/alerts` – fetches recent alert events (incremental polling)

Pantry CRUD:
- `POST /api/pantry/ingredient` – add ingredient (unique by name)
- `PUT /api/pantry/ingredient/{name}` – edit ingredient (avoids name collisions)
- `DELETE /api/pantry/ingredient/{name}` – delete ingredient
- `POST /api/pantry/ingredients/bulk-delete` – bulk delete

Cooked recipes:
- `POST /api/pantry/cooked`
- `PUT /api/pantry/cooked/{name}`
- `DELETE /api/pantry/cooked/{name}`

Recipes:
- `GET /_debug/recipes` / `/_debug/recipes-path`
- `POST /recipes` – save + enrich with Spoonacular nutrition (API key hardcoded; see Security)

Plan update:
- `POST /update_meal` – replaces a slot recipe (form-data or JSON)

### Normalization & Sanitization
- `routes/pantry.py` enforces tag validity and fills missing fields
- `routes/logs.py` converts old date format (YYYY-MM-DD → DD-MM-YYYY) once

---

## 7. Nutrition Calculation
`Reporting_Service.compute_week_nutrition(plan, recipes)` outputs:
```json
{
  "days": {
    "Monday": { "date": "...", "calories": ..., "protein": ..., "carbs": ..., "fats": ..., "meals": { "breakfast": {...}, ... } }
  },
  "week_totals": { "calories": ..., "protein": ..., "carbs": ..., "fats": ... }
}
```
Macronutrients are normalized (carbohydrates ↔ carbs, fat ↔ fats). Used in index and meal-plan pages.

---

## 8. Data Files (format examples)
**Ingredient (`Pantry_ingredients.json`):**
```json
{
  "name": "Chicken breast",
  "unit": "g",
  "default_quantity": 500,
  "expiry_date": "05-10-2025",
  "tags": ["meat-chicken"]
}
```
**Recipe (`recipes.json`):**
```json
{
  "name": "Chicken Curry",
  "servings": 4,
  "ingredients": [{"name": "Chicken breast", "unit": "g", "default_quantity": 500}],
  "steps": ["Cut chicken", "..."],
  "tags": ["dinner"],
  "calories_per_serving": 420,
  "macros": {"protein": 35, "carbohydrates": 20, "fats": 18},
  "image": "chicken_curry.jpg"
}
```
**Plan (`plan.json`):**
```json
{
  "2025-W39": {
    "Monday": {"breakfast": "-", "lunch": "Chicken Curry", "dinner": "-"}
  }
}
```
Dates are added at runtime (not persisted to avoid drift).

---

## 9. Constants (`utilities/constants.py`)
- `DATE_FORMAT = "%d-%m-%Y"`
- `DAYS_BEFORE_EXPIRY = 5`
- `LOW_STOCK_THRESHOLD = {"g":200, "ml":500, "pcs":3, "cloves":2}`

---

## 10. Main Flows
### A. Shopping List Generation
1. User sets recipes in plan.
2. `/shopping-list` loads plan + recipes + pantry.
3. `build_shopping_list` aggregates needs → subtracts pantry → returns missing items.
4. UI allows marking purchased items → `POST /api/shopping-list/buy`.
5. Endpoint merges into pantry JSON and logs transaction.

### B. Pantry Alerts
- On ingredient add/update → evaluate stock + expiry.
- `Pantry` publishes events → `web_observers` store them.
- Frontend polls `/api/pantry/alerts`.

### C. Weekly Nutrition
Computed at page render time; per-slot and total summary.

### D. Add New Recipe
1. Form submits name, servings, ingredients (JSON string), steps, tags, image.
2. Backend calls Spoonacular `analyze`.
3. Extracts macros and saves.

---

## 11. Endpoint Summary
| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | / | Dashboard (plan + alerts + nutrition) |
| GET | /shopping-list | Shopping list (HTML) |
| GET | /camara | Pantry view |
| GET | /recipe/{name} | Recipe details |
| GET | /recipes-page | Recipe catalog (with tag filter) |
| GET | /api/shopping-list | JSON shopping list |
| POST | /api/shopping-list/buy | Mark purchased items |
| GET | /api/pantry/alerts | Recent alert events |
| CRUD | /api/pantry/ingredient[...] | Add / edit / delete / bulk delete |
| CRUD | /api/pantry/cooked[...] | Add / edit / delete cooked meal |
| POST | /update_meal | Update plan slot |
| POST | /recipes | Add recipe (with upload) |

---

## 12. Setup & Run
### Dependencies
See `requirements.txt` (main pinned versions: FastAPI, Uvicorn, Pydantic v2, Jinja2, python-multipart, httpx, reportlab, pytest-asyncio, typer, rich).

### Quick Start (Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn meal.api.api_run:app --reload --host 0.0.0.0 --port 8000
```
Or use: `run_meal_main_WIND.bat`
Access: http://localhost:8000

---

## 13. Testing
Partial tests:
- `test_pantry.py` – add/remove basics
- `test_shopping_list_api.py` – verifies shopping list and specific cases
Run: `pytest -q`

---

## 14. Security & Limitations
- Spoonacular API key is hardcoded → move to environment variable.
- No authentication / ACL.
- JSON writes can race.
- In-memory events only.

---

## 15. Possible Improvements (Roadmap)
1. Implement Strategy for plan generation.
2. State Pattern for meal lifecycle.
3. Import recipes (YAML/PDF/text).
4. Unit conversions (g↔kg, ml↔L).
5. Observability, DB persistence, Auth, UI drag & drop, Caching, More tests.

---

## 16. Handled Edge Cases
- Case-insensitive & space-normalized names.  
- Accepts both `%d-%m-%Y` and `%Y-%m-%d` expiry formats.  
- Skips invalid dates safely.  
- Simple plural → singular rules.  
- Duplicate recipe names → 400 error.  
- Duplicate cooked items (name + date) → blocked.  
- Empty alert buffer triggers initial scan on first poll.

---

## 17. Current Limitations
- Pantry CRUD bypasses `Pantry` class (inconsistent layer).  
- Missing Pydantic validations for payloads.  
- No centralized unit conversions.  
- No full UI for randomize/reset plan (only repository methods exist).

---

## 18. Style & Conventions
- Dates: `DD-MM-YYYY`  
- JSON keys: snake_case  
- Ingredient tags: controlled set (fallback `other`).

---

## 19. How to Extend
1. Add a new alert type (e.g., `high_protein_day`):  
   - Publish a new event from a service.  
   - Subscribe to it in `web_observers.start`.  
2. Add macro calculations to plan:  
   - Extend `compute_week_nutrition` with dynamic servings.  
3. Add DB persistence:  
   - Implement a new repository layer (SQLAlchemy) keeping the same API.

---

## 20. Technical Flow Summary
1. User accesses UI → FastAPI serves Jinja2 template.  
2. Template loads JS/CSS from `/static`.  
3. JS polls `/api/pantry/alerts`.  
4. User actions (update meal / add recipe / buy list) → JSON endpoint → JSON persistence.  
5. Pantry events → event bus → buffer → UI.

---

## 21. License / Attribution
(Not specified yet — add a license if publishing publicly.)

---

## 22. FAQ
**Q:** Why is `date` not persisted in `plan.json`?  
**A:** It’s derived from `(year, week_number)` to avoid calendar drift.

**Q:** How to change expiry warning threshold?  
**A:** Edit `DAYS_BEFORE_EXPIRY` in `utilities/constants.py`.

**Q:** Can I add a new low-stock unit?  
**A:** Add a pair to `LOW_STOCK_THRESHOLD`, then restart.

**Q:** Why no alerts appear?  
**A:** The first `/api/pantry/alerts` call triggers an initial scan.

---

## 23. Contact / Contributions
- Open an issue or pull request for bugs or suggestions.  
- Recommended test areas: pluralization and purchase merging.

---

## 24. Directory Breakdown & Logic Separation

This section explains why each directory exists and how the logic is layered (loosely hexagonal architecture).

### Overview (Layers)
```
[ UI / Presentation ]  ->  api/  + templates/ + static/
        |                (serves pages + exposes REST/HTML endpoints)
        v
[ Application / Orchestration ]  -> services/ (facades – placeholders)
        v
[ Domain Core ]  -> domain/ (pure entities + simple internal rules)
        v
[ Business Rules / Policies ]  -> rules/ (algorithms: shopping list, planning, import)
        v
[ Events / Integration ]  -> events/ (publish-subscribe, UI adapters)
        v
[ Infrastructure ]  -> infra/ (JSON persistence, PDF, file access)
        v
[ Data / Storage ]  -> data/ (persistent JSON artifacts)
```

**Dependency direction:** top → down (UI may use services/rules/domain/infra; domain must not import api/ or infra).

### Quick Directory Overview
- `meal/` – main Python package.  
- `meal/main.py` – simple entry point (runs uvicorn with app from `api_run.py`).

#### Presentation Layer
- `meal/api/` – configures FastAPI, mounts static & templates, defines main pages and routers.  
- `meal/api/api_run.py` – FastAPI app, HTML pages, JSON endpoints, starts event observers.  
- `meal/api/routes/` – thematic routers (single-responsibility):
  - `recipes.py`, `pantry.py`, `logs.py`, `add.py`, `plans.py`
- `templates/` – Jinja2 templates (server-side rendered UI).  
- `static/` – front-end resources (CSS, JS, images, icons).

#### Domain Core
- `domain/` – pure model objects (`Ingredient`, `Recipe`, `RecipeCooked`, `Pantry`, `Plan`).  
  No direct I/O.

#### Business Rules / Policies
- `rules/` – algorithms and extensibility patterns.  
  Includes shopping list builder and placeholders for future patterns.

#### Application / Services Layer
- `services/` – orchestrates domain + rules + infra (only `Reporting_Service` implemented).

#### Events / Integration
- `events/` – decoupled event bus for stock/expiry notifications.

#### Infrastructure Layer
- `infra/` – technical-level persistence (JSON + PDF).  
  Includes repositories for plan, pantry, recipes.

#### Data Store
- `data/` – JSON persistence (no code).

#### Utilities
- `utilities/` – global constants, used across layers.

#### Testing
- `tests/` – current unit/integration placeholders.

#### Frontend Assets
- `static/` – structured JS + resources.

#### Root Scripts
- `run_meal_main_WIND.bat`, `requirements.txt`, `README-Meal-Planner-and-Pantry.md`.

### Separation Principles
1. Domain independent from infra/UI.  
2. Rules depend only on domain.  
3. Services orchestrate domain + rules + infra.  
4. API validates and delegates to services/rules.  
5. Events decouple backend ↔ UI.  
6. Infra never calls API.  
7. Utilities contain constants only.

### Ideal Dependency Diagram
```
api ---> services ---> rules ---> domain
  |          |            |         ^
  |          |            v         |
  |          |----------> infra ----|
  |                       |
  |                       v
  |---------------------> events (subscribe)
```

### Maintenance Recommendations
- New algorithm → place in `rules/` and expose via `services/`.  
- Avoid business logic inside `api_run.py`.  
- Move direct JSON access from routes into repositories.

### Refactoring Roadmap
1. Move ingredient/cooked read-write into `PantryRepositoryV2`.  
2. Implement `Planning_Service` (randomization + strategy).  
3. Add `Recipe_Importer` (Template Method).  
4. Add `utilities/units.py` for conversions.

---

Happy cooking & planning! 🍲
