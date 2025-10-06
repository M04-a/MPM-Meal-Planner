import json, os
from typing import Optional
from datetime import timedelta, date
from meal.domain.Plan import Plan
import random
from datetime import date, datetime
from meal.api.routes.recipes import load_recipes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAN_FILE = os.path.normpath(os.path.join(BASE_DIR, "../data/plan.json"))

def _week_key(year: int, week_number: int) -> str:
    return f"{year}-W{week_number:02d}"

class PlanRepository:
    def get_week_plan(self, week_number: int, year: Optional[int] = None) -> Plan:
        if year is None:
            year = date.today().isocalendar().year

        # init store
        if not os.path.exists(PLAN_FILE):
            with open(PLAN_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

        try:
            with open(PLAN_FILE, "r", encoding="utf-8") as f:
                store = json.load(f) or {}
        except Exception:
            store = {}

        key = _week_key(year, week_number)

        # dacă nu există săptămâna, creează default
        if key not in store:
            store[key] = {
                d: {"breakfast": "-", "lunch": "-", "dinner": "-"}
                for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            }
            with open(PLAN_FILE, "w", encoding="utf-8") as f:
                json.dump(store, f, indent=2, ensure_ascii=False)

        meals = store[key]

        # (RE)CALCULEAZĂ mereu datele pentru UI
        monday = date.fromisocalendar(year, week_number, 1)
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        for i, day_name in enumerate(days):
            d = monday + timedelta(days=i)
            # asigură structura
            if day_name not in meals:
                meals[day_name] = {"breakfast": "-", "lunch": "-", "dinner": "-"}
            else:
                meals[day_name].setdefault("breakfast", "-")
                meals[day_name].setdefault("lunch", "-")
                meals[day_name].setdefault("dinner", "-")
            # suprascrie întotdeauna data pentru săptămâna curentă
            meals[day_name]["date"] = d.strftime("%d.%m.%Y")

        plan = Plan(week_number, meals, year=year)
        plan.week = week_number
        plan.year = year
        return plan

    def save_week_plan(self, week_number: int, plan: Plan, year: Optional[int] = None) -> None:
        if year is None:
            year = getattr(plan, "year", date.today().isocalendar().year)

        try:
            with open(PLAN_FILE, "r", encoding="utf-8") as f:
                store = json.load(f) or {}
        except Exception:
            store = {}

        key = _week_key(year, week_number)

        # NU salvăm câmpul 'date'
        clean_meals = {
            day: {k: v for k, v in meals.items() if k != "date"}
            for day, meals in plan.meals.items()
        }
        store[key] = clean_meals

        with open(PLAN_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)

    def reset_week(self, week_number: int, year: Optional[int] = None):
        """Resetează toate mesele din săptămâna dată la '-'."""
        plan = self.get_week_plan(week_number, year)
        for day, meals in plan.meals.items():
            meals["breakfast"] = "-"
            meals["lunch"] = "-"
            meals["dinner"] = "-"
        self.save_week_plan(week_number, plan, year)

    def randomize_week(self, week_number: int, year: Optional[int] = None):
        """
        Completeaza doar zilele care nu au trecut.
        - Pentru o saptamana din viitor: umple TOATE sloturile (overwrite).
        - Pentru saptamana curenta: umple DOAR sloturile goale ('-') de AZI si VIITOR.
        - Pentru zilele trecute: nu modifica nimic.
        """
        plan = self.get_week_plan(week_number, year)
        recipes = load_recipes()
        recipe_names = [r["name"] for r in recipes] if recipes else []

        today = date.today()

        # Determinam daca intreaga saptamana e in viitor (pentru a permite overwrite complet)
        day_dates = []
        for meals in plan.meals.values():
            try:
                day_dates.append(datetime.strptime(meals["date"], "%d.%m.%Y").date())
            except Exception:
                pass

        entire_week_in_future = bool(day_dates) and min(day_dates) > today
        fill_only_empty = not entire_week_in_future  # curent => doar sloturi '-'; viitor => overwrite

        for day, meals in plan.meals.items():
            try:
                day_date = datetime.strptime(meals["date"], "%d.%m.%Y").date()
            except Exception:
                continue

            # sari peste zilele trecute
            if day_date < today:
                continue

            for meal in ("breakfast", "lunch", "dinner"):
                if fill_only_empty and meals.get(meal) not in (None, "", "-"):
                    # pastreaza ceea ce utilizatorul a setat deja
                    continue
                meals[meal] = random.choice(recipe_names) if recipe_names else "-"

        self.save_week_plan(week_number, plan, year)
