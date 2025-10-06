from collections import defaultdict
from typing import Dict, Any, List

# Structure expected for plan.meals:
# plan.meals[day] = { 'date': 'dd.mm.yyyy', 'breakfast': 'RecipeName' | '-', 'lunch': 'RecipeName', 'dinner': 'RecipeName' }
# Recipes list: each recipe is a dict with keys: name, calories_per_serving, macros{ protein, carbohydrates|carbs, fats }

def _normalize_macros(macros: Dict[str, Any]):
    if not isinstance(macros, dict):
        return {'protein': 0, 'carbs': 0, 'fats': 0}
    return {
        'protein': macros.get('protein', 0) or 0,
        'carbs': macros.get('carbs', macros.get('carbohydrates', 0) or 0) or 0,
        'fats': macros.get('fats', macros.get('fat', 0) or 0) or 0,
    }

def compute_week_nutrition(plan, recipes: List[dict]):
    """
    Returns aggregated nutrition stats for the given plan & recipe catalog.
    Output shape:
    {
      'days': {
         'Monday': {'date': 'dd.mm.yyyy', 'calories': int, 'protein': g, 'carbs': g, 'fats': g,
                     'meals': { 'breakfast': { 'name': str, 'calories': int, 'protein': g, 'carbs': g, 'fats': g }, ... }},
         ...
      },
      'week_totals': { 'calories': int, 'protein': g, 'carbs': g, 'fats': g }
    }
    """
    if not plan or not getattr(plan, 'meals', None):
        return { 'days': {}, 'week_totals': { 'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0 } }

    # Index recipes by lower-case name for quick lookup
    recipe_index = { (r.get('name') or '').lower(): r for r in recipes }

    days_result = {}
    totals = defaultdict(int)

    for day, meals in plan.meals.items():
        if not isinstance(meals, dict):
            continue
        day_cal = day_pro = day_carbs = day_fats = 0
        meal_details = {}
        for slot in ('breakfast', 'lunch', 'dinner'):
            raw_val = meals.get(slot)
            if not raw_val or raw_val == '-':
                continue
            recipe_name = raw_val.get('name') if isinstance(raw_val, dict) else raw_val
            if not isinstance(recipe_name, str):
                continue
            r = recipe_index.get(recipe_name.lower())
            if not r:
                continue
            cals = r.get('calories_per_serving', r.get('kalories_per_serving', 0)) or 0
            macros_norm = _normalize_macros(r.get('macros', {}))
            meal_details[slot] = {
                'name': recipe_name,
                'calories': cals,
                'protein': macros_norm['protein'],
                'carbs': macros_norm['carbs'],
                'fats': macros_norm['fats'],
            }
            day_cal += cals
            day_pro += macros_norm['protein']
            day_carbs += macros_norm['carbs']
            day_fats += macros_norm['fats']
        # Accumulate day
        days_result[day] = {
            'date': meals.get('date'),
            'calories': day_cal,
            'protein': day_pro,
            'carbs': day_carbs,
            'fats': day_fats,
            'meals': meal_details
        }
        totals['calories'] += day_cal
        totals['protein'] += day_pro
        totals['carbs'] += day_carbs
        totals['fats'] += day_fats

    return {
        'days': days_result,
        'week_totals': {
            'calories': totals['calories'],
            'protein': totals['protein'],
            'carbs': totals['carbs'],
            'fats': totals['fats'],
        }
    }

