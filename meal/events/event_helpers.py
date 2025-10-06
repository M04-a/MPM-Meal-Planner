"""Event helper utilities.

Acest modul oferă functii dedicate pentru publicarea evenimentelor
legate de camara (pantry), folosind busul global.

Import rapid:
    from meal.events.event_helpers import (
        publish_low_stock, publish_near_expiry, publish_expiring_snapshot,
        PANTRY_LOW_STOCK, PANTRY_NEAR_EXPIRY, PANTRY_EXPIRING_SNAPSHOT
    )

"""
from __future__ import annotations
from typing import Iterable, Any
from .Event_Bus import (
    crea, create_event,  # aliasuri
    PANTRY_LOW_STOCK, PANTRY_NEAR_EXPIRY, PANTRY_EXPIRING_SNAPSHOT,
    GLOBAL_EVENT_BUS
)

__all__ = [
    'publish_low_stock', 'publish_near_expiry', 'publish_expiring_snapshot',
    'PANTRY_LOW_STOCK', 'PANTRY_NEAR_EXPIRY', 'PANTRY_EXPIRING_SNAPSHOT',
    'crea', 'create_event'
]

def publish_low_stock(ingredient: Any, remaining: int, threshold: int):
    """Publică un eveniment pantry.low_stock."""
    crea(PANTRY_LOW_STOCK, {
        'ingredient': ingredient,
        'remaining': remaining,
        'threshold': threshold
    })

def publish_near_expiry(ingredient: Any, days_left: int, threshold: int):
    """Publică un eveniment pantry.near_expiry."""
    crea(PANTRY_NEAR_EXPIRY, {
        'ingredient': ingredient,
        'days_left': days_left,
        'threshold': threshold
    })

def publish_expiring_snapshot(items: Iterable[dict]):
    """Publică un snapshot cu ingredientele care expiră curând.

    Payload:
        {
          'count': <numar>,
          'items': [ { name, quantity, unit, exp, days_left, tag }, ... ]
        }
    """
    items_list = list(items) if not isinstance(items, list) else items
    crea(PANTRY_EXPIRING_SNAPSHOT, {
        'count': len(items_list),
        'items': items_list
    })

# Exemplu de subscriber opțional (nu este înregistrat implicit)

def _debug_listener(event_name: str, payload):  # pragma: no cover (debug utility)
    print(f'[EVENT DEBUG] {event_name}: {payload}')

# Pentru a activa debug global: decomentează linia următoare
# GLOBAL_EVENT_BUS.subscribe(PANTRY_EXPIRING_SNAPSHOT, _debug_listener)

