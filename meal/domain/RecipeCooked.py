from datetime import date, timedelta
from meal.domain.Ingredient import Ingredient
from meal.utilities.constants import DATE_FORMAT

class RecipeCooked(Ingredient):
    def __init__(self, name: str="", default_quantity: int=0, unit: str='pcs', data_expirare: date=date.today()+timedelta(days=5), tags: list = [], kallories: int=0):
        super().__init__(name, unit, default_quantity, data_expirare, tags)
        self.kallories = kallories

    def __str__(self) -> str:
        return f"{super().__str__()} - Kcal: {self.kallories}"
    
    def __repr__(self):
        return self.__str__()