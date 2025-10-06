import unittest
from fastapi.testclient import TestClient
from meal.api.api_run import app
from meal.infra.Plan_Repository import PlanRepository
from datetime import date
class TestShoppingListAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_api_shopping_list_basic(self):
        # Pregătește planul pentru săptămâna ISO curentă (dinamic)
        iso = date.today().isocalendar()
        week = iso.week
        repo = PlanRepository()
        plan = repo.get_week_plan(week)

        # Setăm rețetele necesare pentru a reproduce așteptările testului:
        #  - 3x Chicken Curry (pentru deficit Chicken breast)
        #  - 1x Vegetable Stir Fry (Bell pepper lipsă din pantry -> trebuie să apară)
        #  - 1x Spaghetti Bolognese (Spaghetti există suficient și nu trebuie să apară ca missing)
        # Curățăm întâi zilele pentru a avea control:
        for day, meals in plan.meals.items():
            meals['breakfast'] = '-'
            meals['lunch'] = '-'
            meals['dinner'] = '-'

        days = list(plan.meals.keys())
        if len(days) >= 5:
            plan.meals[days[0]]['lunch'] = 'Chicken Curry'
            plan.meals[days[1]]['breakfast'] = 'Vegetable Stir Fry'
            plan.meals[days[2]]['dinner'] = 'Chicken Curry'
            plan.meals[days[3]]['dinner'] = 'Spaghetti Bolognese'
            plan.meals[days[4]]['lunch'] = 'Chicken Curry'
        else:
            # fallback (teoretic nu ar trebui, dar mențin robust)
            first = days[0]
            plan.meals[first]['breakfast'] = 'Vegetable Stir Fry'
            plan.meals[first]['lunch'] = 'Chicken Curry'
            plan.meals[first]['dinner'] = 'Chicken Curry'

        repo.save_week_plan(week, plan)

        resp = self.client.get('/api/shopping-list')  # fără param -> week curent
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('week', data)
        self.assertEqual(data['week'], week)
        self.assertIn('items', data)
        self.assertIn('count', data)
        items = data['items']
        if items:
            for it in items:
                for key in ('name','unit','required','have','missing'):
                    self.assertIn(key, it)
        # Bell pepper trebuie să apară ca lipsă
        bell = [i for i in items if i['name'].lower() == 'bell pepper']
        self.assertTrue(bell, 'Bell pepper should be missing (not in pantry).')
        # Spaghetti nu trebuie să apară (avem 500, cerință 400)
        # Spaghetti nu trebuie să apară (avem 500, cerință 400)
        # Chicken breast trebuie să fie missing cu 1000 (1500 necesar - 500 existent)
        self.assertFalse(spaghetti, 'Spaghetti should not be missing (pantry has enough).')
        # Chicken breast trebuie să fie missing cu 1000 (1500 necesar - 500 existent)
    unittest.main()
