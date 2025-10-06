#TODO ShoppingListBuilder , Template Method: (pipeline pentru listă)
from collections import defaultdict
from typing import Dict, List, Any
from datetime import date as _date, datetime

from meal.domain.Plan import Plan


def _normalize(name: str) -> str:
    return (name or '').strip().lower()

def _stem(word: str) -> str:
    # reguli simple pentru plural -> singular (nu perfecte, dar utile aici)
    if word.endswith('ies') and len(word) > 3:

        return word[:-3] + 'y'  # candies -> candy
    if word.endswith('oes') and len(word) > 3:
        # tomatoes -> tomato, potatoes -> potato
        return word[:-3] + 'o'
    if word.endswith('ses') and len(word) > 3:
        return word[:-2]  # classes -> classe (limitare acceptată)
    if word.endswith('es') and len(word) > 2 and word[-3] not in 'aeiou':
        # generic fallback: boxes -> box, dishes -> dish (nu tratăm toate excepțiile)
        return word[:-2]
    if word.endswith('s') and not word.endswith('ss') and len(word) > 1:
        return word[:-1]
    return word

def _key(name: str) -> str:
    return _stem(_normalize(name))


def build_shopping_list(plan: Plan, recipes: List[Dict[str, Any]], pantry_ingredients: List[Dict[str, Any]], *, skip_past_days: bool = False):
    """
    Calculează lista de cumpărături (ingrediente lipsă) pe baza:
      - planului săptămânal (Plan)
      - rețetelor disponibile (lista de dict din recipes.json)
      - ingredientelor din cămară (Pantry_ingredients.json)

    Returnează o listă de dicționare cu structura:
        {"name": str, "unit": str, "required": int, "have": int, "missing": int}
    Doar ingredientele cu missing > 0 sunt incluse.

    Potrivirea se face case-insensitive și încearcă să unifice forme plural/singular simple.

    Parametri nou:
      skip_past_days: dacă True și plan-ul conține câmpul 'date' pe fiecare zi (format dd.mm.YYYY),
                      mesele ale căror date sunt < astăzi sunt ignorate (util pentru săptămâna curentă după ce unele zile au trecut).
    """
    if not plan or not recipes:
        return []

    today = _date.today()
    recipe_index: Dict[str, Dict[str, Any]] = {_normalize(r.get('name', '')): r for r in recipes}

    required: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"unit": "", "quantity": 0, "display_name": ""})

    for meals in plan.meals.values():
        # Skip past days if requested
        if skip_past_days:
            d_str = meals.get('date')
            if d_str:
                try:
                    d = datetime.strptime(d_str, '%d.%m.%Y').date()
                    if d < today:
                        continue
                except Exception:
                    pass
        for slot_val in meals.values():
            # Ignore date or empty markers
            if not slot_val or slot_val == '-' or slot_val == meals.get('date'):
                continue
            # If slot value is a cooked dict, skip (already executed meal)
            if isinstance(slot_val, dict):
                if slot_val.get('cooked'):
                    continue  # do not include already cooked recipes in future shopping list
                recipe_name = slot_val.get('name', '')
            else:
                recipe_name = slot_val
            if not isinstance(recipe_name, str) or not recipe_name.strip():
                continue
            recipe = recipe_index.get(_normalize(recipe_name))
            if not recipe:
                continue
            for ing in recipe.get('ingredients', []):
                name = ing.get('name')
                if not name:
                    continue
                k = _normalize(name)
                qty = ing.get('default_quantity', 0) or 0
                unit = ing.get('unit', '') or ''
                if required[k]["unit"] in ("", unit):
                    required[k]["unit"] = unit
                required[k]["quantity"] += qty
                if not required[k]['display_name']:
                    required[k]['display_name'] = name

    have_totals: Dict[str, int] = defaultdict(int)
    for p in pantry_ingredients:
        k = _normalize(p.get('name',''))
        try:
            have_totals[k] += int(p.get('default_quantity') or 0)
        except Exception:
            pass

    shopping_list: List[Dict[str, Any]] = []
    for norm_name, data in required.items():
        have = have_totals.get(norm_name, 0)
        required_qty = int(data['quantity'])
        missing = required_qty - have
        if missing > 0:
            shopping_list.append({
                'name': data['display_name'] or norm_name,
                'unit': data['unit'],
                'required': required_qty,
                'have': have,
                'missing': missing
            })

    shopping_list.sort(key=lambda x: x['name'].lower())
    return shopping_list


__all__ = ['build_shopping_list']
