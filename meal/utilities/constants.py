from typing import Final

DATE_FORMAT: Final[str] = "%d-%m-%Y"
DAYS_BEFORE_EXPIRY: Final[int] = 5
LOW_STOCK_THRESHOLD: Final[dict[str, int]] = {"g": 200, "ml": 500, "pcs": 3, "cloves": 2}