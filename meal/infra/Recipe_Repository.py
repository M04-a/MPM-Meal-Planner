import os
import json
from meal.domain.Recipe import Recipe

def reading_from_recipes():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', 'data', 'recipes.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            recipes_data = json.load(f)
        recipes = []
        for entry in recipes_data:
            recipe = Recipe(
                **entry
                # name=entry.get('name'),
                # servings=entry.get('servings'),
                # ingredients=entry.get('ingredients'),
                # steps=entry.get('steps'),
                # tags=entry.get('tags', [])
            )
            recipes.append(recipe)
        return recipes
    except Exception as e:
        print(f"Error reading recipes: {e}")