#TODO PantryRepository (stocare pantry)
import json
import os
from datetime import datetime
from meal.domain.Pantry import Pantry
from meal.domain.Ingredient import Ingredient


def reading_from_ingredients():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, '..', 'data', 'Pantry_ingredients.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            ingredient_data = json.load(f)
        pantry = Pantry()
        for entry in ingredient_data:
            entry["data_expirare"] = datetime.strptime(entry["data_expirare"], "%d-%m-%Y")
            ingredient = Ingredient(**entry)
            pantry.add_item(ingredient)
        return pantry
    except Exception as e:
        print(f"Error reading recipes: {e}")
