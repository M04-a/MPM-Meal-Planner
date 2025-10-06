#TODO Ingredient (nume, cantitate, unitate)
from datetime import date, datetime, timedelta
from meal.utilities.constants import DATE_FORMAT


class Ingredient:
    def __init__(self, name: str="", unit: str="", default_quantity: int =0, data_expirare: date=None , tags: list = []):
        self.name = name
        self.unit = unit
        self.default_quantity = default_quantity
        self.data_expirare = data_expirare
        self.tags = tags
    
    def set_quantity(self, quantity: int):
        '''
        Adjusts the quantity by the specified amount.
        '''
        self.default_quantity += quantity
    
    def __str__(self) -> str:
        parts = [f"{self.name} - {self.default_quantity} {self.unit}"]
        if self.data_expirare:
            parts.append(f"Exp: {self.data_expirare.strftime(DATE_FORMAT)}")
        if self.tags:
            parts.append("Tags: " + ", ".join(self.tags))
        return " - ".join(parts)

    def __repr__(self) -> str:
        return self.__str__()

    def from_dict(data):
        '''
        Creates an Ingredient object from a dictionary. Ignores unknown keys like batch_id.
        '''
        d = dict(data) if isinstance(data, dict) else {}
        if "data_expirare" in d and d["data_expirare"] and not isinstance(d["data_expirare"], (datetime, date)):
            try:
                d["data_expirare"] = datetime.strptime(d["data_expirare"], DATE_FORMAT).date()
            except Exception:
                # fallback: drop invalid date
                d["data_expirare"] = None
        allowed = {"name","unit","default_quantity","data_expirare","tags"}
        filtered = {k: v for k, v in d.items() if k in allowed}
        # ensure defaults
        filtered.setdefault("name", "")
        filtered.setdefault("unit", "")
        filtered.setdefault("default_quantity", 0)
        filtered.setdefault("tags", [])
        return Ingredient(**filtered)

    def to_dict(self):
        '''
        Converts the Ingredient object to a dictionary. Gracefully handles missing/invalid expiration dates.
        '''
        if isinstance(self.data_expirare, (datetime, date)):
            exp_val = self.data_expirare.strftime(DATE_FORMAT)
        else:
            # If it's an empty string/None or already a string leave as-is (fallback '')
            exp_val = self.data_expirare if isinstance(self.data_expirare, str) else ""
        return {
            "name": self.name,
            "unit": self.unit,
            "default_quantity": self.default_quantity,
            "data_expirare": exp_val,
            "tags": self.tags
        }