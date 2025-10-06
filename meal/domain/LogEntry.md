# LogEntry

## Rolul log.py (Daily Log)

Scopul lui este să înregistreze ce s-a întâmplat efectiv în fiecare zi cu mesele planificate.

De ce? Pentru că există o diferență între:

Plan → ce intenționezi să gătești (ex. luni seara: chili)

Log → ce s-a întâmplat în realitate (ai gătit chili, dar ai făcut mai puține porții și au rămas 2 porții extra)

###
## Explicație pe câmpuri:

day: date → ziua pentru care loghezi (ex. 2025-09-22).

meal: str → ce masă e (ex. "dinner", "lunch", "breakfast").

cooked: bool → dacă masa chiar a fost gătită sau nu.

exemplu: poate ai sărit peste ea → cooked=False.

leftovers: float → câte porții au rămas și trebuie să se întoarcă în Pantry.

exemplu: ai gătit 4 porții, ai mâncat 2, ți-au rămas 2 → acestea se adaugă în pantry ca „leftover food”.

###
## 🔗 Cum se leagă LogEntry de restul

 ##Plan → Log

Planul spune că luni la cină trebuie să faci „Chili”.

Când rulezi comanda CLI meal cook --date 2025-09-22 --meal dinner --leftovers 2, se creează un LogEntry.

###
## Log → Pantry

Când cooked=True, pantry-ul scade ingredientele folosite.

Dacă leftovers > 0, acestea se adaugă ca item nou în pantry („Chili leftovers, 2 servings”).

###
## Observer

După fiecare log, se trimit evenimente către sistemul de alerte (de exemplu, dacă un ingredient a scăzut sub minim → mesaj la raport).

###
## Reporting

LogEntry permite să generezi rapoarte:

Progresul săptămânii (câte mese planificate chiar ai gătit).

Estimarea de „waste” (dacă ai loguri cu cooked=False, înseamnă mâncare risipită sau plan ratat).