#TODO Recipe (nume, porții, ingrediente, pași, tag-uri)
import json
import os
from meal.domain.Ingredient import Ingredient
from meal.domain.RecipeCooked import RecipeCooked


class Recipe:
    def __init__(self, name: str="", servings: int=0, ingredients: list[Ingredient]=[], steps: list=[], tags: list=[], calories_per_serving: int=0, macros: dict={}, image=""):
        self.name = name
        self.servings = servings
        self.ingredients = ingredients  # List of Ingredient objects
        self.steps = steps  # List of strings
        self.tags = tags  # List of strings(mic-dejun, pranz, cina, desert, vegetarian, vegan, etc.)
        self.calories_per_serving = calories_per_serving
        self.macros = macros  # Dictionary with keys like 'protein', 'carbs', 'fats'
    
    def __str__(self) -> str:  # Used by templates and prints
        protein = self.macros.get("protein", 0)
        carbs = self.macros.get("carbs", 0)
        fats = self.macros.get("fats", 0)
        macros_str = f"Protein: {protein}g, Carbs: {carbs}g, Fats: {fats}g"
        return f"{self.name} - {self.servings} servings - Tags: {', '.join(self.tags)} - Calories/serving: {self.calories_per_serving} - Macros: {macros_str}"

    def __repr__(self) -> str:  # Keep previous representation behavior
        return self.__str__()
    
    def get_protein(self):
        return self.macros.get("protein", 0)
    
    def get_carbs(self):
        return self.macros.get("carbs", 0)

    def get_fats(self):
        return self.macros.get("fats", 0)

    def from_dict(data):
        '''
        Creates a Recipe object from a dictionary.
        data: Dictionary containing recipe data.
        '''
        data["ingredients"] = [Ingredient.from_dict(ing) for ing in data["ingredients"]]
        return Recipe(**data)
    
    def to_dict(self):
        '''
        Converts the Recipe object to a dictionary.
        '''
        return {
            "name": self.name,
            "servings": self.servings,
            "ingredients": [ing.to_dict() for ing in self.ingredients],
            "steps": self.steps,
            "tags": self.tags,
            "calories_per_serving": self.calories_per_serving,
            "macros": {
            "protein": self.macros.get("protein", 0),
            "carbs": self.macros.get("carbs", 0),
            "fats": self.macros.get("fats", 0),
            },
        }
    
    @classmethod
    def read_from_json(self, file_name: str):
        '''
        Reads recipe data from a JSON file and populates the recipe object.
        file_name: Name of the JSON file (without .json extension) located in the data directory.
        '''
        recipes = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, '..', 'data', file_name+'.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                recipes_data = json.load(f)
                for recipe_data in recipes_data:
                    recipes.append(self.from_dict(recipe_data))
        except Exception as e:
            print(f"Error reading recipes: {e}")
        return recipes
    
    def check_ingredients(self, available_ingredients: list):
        '''
        Checks if all ingredients required for the recipe are available.
        available_ingredients: List of Ingredient objects that are available.
        Returns True if all ingredients are available, False otherwise.
        '''
        for ingredient in self.ingredients:
            required_qty = ingredient.default_quantity
            total_available = 0
            # Adună cantitățile tuturor ingredientelor disponibile cu același nume
            for avail_ing in available_ingredients:
                if avail_ing.name == ingredient.name:
                    total_available += avail_ing.default_quantity
            if total_available < required_qty:
                return False
        return True

    def cook(self, available_ingredients: list):
        '''
        Simulates the cooking process.
        available_ingredients: List of Ingredient objects that are available.
        If all ingredients are available, it deducts the used quantities from available ingredients
        and returns a RecipeCooked object. Otherwise, it returns None.
        '''
        if self.check_ingredients(available_ingredients):
            print(f"Cooking {self.name}...")
            for ingredient in self.ingredients:
                for avail_ing in available_ingredients:
                    if ingredient.name == avail_ing.name:
                        needed = ingredient.default_quantity
                        same_name = [ing for ing in available_ingredients if ing.name == ingredient.name]
                        same_name.sort(key=lambda x: (getattr(x, 'expiration_date', getattr(x, 'expiry_date', None)) is None,
                                                      getattr(x, 'expiration_date', getattr(x, 'expiry_date', None))))
                        for ing_obj in same_name:
                            if needed <= 0:
                                break
                            take = min(ing_obj.default_quantity, needed)
                            ing_obj.set_quantity(-take)
                            needed -= take
                            if ing_obj.default_quantity <= 0:
                                try:
                                    available_ingredients.remove(ing_obj)
                                except ValueError:
                                    pass
                        break
            for step in self.steps:
                print(step)
            print(f"{self.name} is ready to serve!")
            return RecipeCooked(self.name, self.servings, kallories=self.calories_per_serving, tags=self.tags)
        return None