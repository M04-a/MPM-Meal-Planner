class Plan:
    def __init__(self, week_number, meals, year=None):
        self.week_number = week_number
        self.meals = meals
        self.year = year
        self.week = week_number  # ca să fie consistent cu template-ul
