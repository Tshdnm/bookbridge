# BookBridge

A simple online book browsing and reservation system for a local bookstore.

BookBridge is D2-Team7's local Software Engineering course prototype. This implementation follows the submitted Task2 user requirements: one store, sample records, predefined customer/staff identities, and in-store collection. It uses Flask and SQLite.

## Current stage: 9–15 November 2026

Task1 and Task2 were submitted previously. Task3's 35-page final analysis report has now been submitted to Moodle, as confirmed by the team leader on 9 November; the actual submission date is still to be supplied. The first presentation is scheduled for 12 November. Its 16-slide English deck and four Chinese scripts are ready for rehearsal.

- [Requirements baseline](docs/requirements-baseline.md)
- [This week's plan and functional ownership](docs/week-2026-11-09.md)
- [Refined Task3 models used for the final report](docs/task3-final/README.md)
- [First-presentation outline, scripts and speaking schedule](docs/presentation-1/README.md)
- [Actual review evidence and remaining checks](docs/development-status.md)
- [Previous 2–8 November plan](docs/week-2026-11-02.md)

This update adds analysis, presentation and progress materials. The application remains the initial local prototype; it does not claim a new feature implementation, completed group rehearsal or full manual acceptance. The report and presentation materials were prepared with AI assistance. Assigned ownership remains distinct from completed contribution.

Task3's published deadline is **12 November 2026 at 23:59**. **5 December 2026** is the team's internal project readiness target; the official final-project date remains to be confirmed. Optional online hosting is a later experiment.

## Run locally

Python 3.9 or later is required. From this directory on Windows:

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python run.py
```

Open http://127.0.0.1:5000 in your browser. The first start creates `instance/bookbridge.sqlite`, seeds 20 invented book titles, and stores a local session secret. Later starts preserve the data. Keep `instance/` out of Git. Stop the server with Ctrl+C.

On macOS/Linux use `python3 -m venv .venv`, then `.venv/bin/python` instead of the Windows executable paths.

## Try the main workflow

1. Use Demo customer A and find **The Quiet Bookshop** (initial stock 5, unit price 30.00).
2. Reserve 2 copies. The reservation amount is 60.00 and available stock becomes 3.
3. Switch to Demo staff and confirm collection in Staff reservations. Stock stays 3.
4. View Catalogue & summary: completed copies 2, completed reservation amount 60.00.
5. For a separate cancellation example, create another pending reservation as a customer and cancel it. Its stock is restored once.

Predefined identities are a deliberate classroom demonstration feature. They are not production authentication. The application listens only on localhost. It does not process payment, delivery or real customer details, and does not synchronize with a live bookstore database.

## Requirements and ownership

| Area | Requirement IDs | Functional owner |
| --- | --- | --- |
| Catalogue, listing and stock receipts | FR-01, FR-02 | F1 owner |
| Browse, details, search, category and price order | FR-03 | F2 owner |
| Reservation, cancellation and collection | FR-04, FR-05, FR-06 | F3 owner (team coordinator) |
| Personal/staff queries and completed totals | FR-07, FR-08, FR-09 | F4 owner |

These are planned team responsibilities, not a claim that each member authored or verified the initial implementation. The initial prototype was prepared with AI assistance and should be reviewed and demonstrated by its functional owners.

## Business rules

- One reservation contains one title and a positive whole-number quantity.
- Creating a reservation saves the price and reduces available stock atomically.
- Only its customer can cancel a pending reservation. Cancellation restores stock once.
- Only staff can confirm collection. Completion does not deduct stock again.
- Completed and Cancelled are terminal states. Further cancellation/collection actions are rejected clearly and have no additional effect.
- Unlisting preserves existing records while blocking new reservations.
- Summary amounts describe completed BookBridge reservations, not verified payment revenue.
- Repeated submission with the same request key does not create a second reservation.

## Check the implementation

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```

Tests use isolated temporary databases, leaving demonstration data untouched. The ten automated tests cover the nine acceptance scenarios' API rules, with an additional CSRF/stock check. The capacity test exercises 20 titles and 100 reservations with one operator. Its timing measurement is an API check; it is not a full browser response-time or classroom acceptance result.

See [development status](docs/development-status.md) for evidence and remaining team work.

## Source layout

- `bookbridge/__init__.py`: request validation, role checks and JSON endpoints.
- `bookbridge/db.py`, `schema.sql`, `seed.py`: SQLite transactions, schema and sample data.
- `bookbridge/templates/index.html`, `static/`: browser interface.
- `tests/test_acceptance.py`: isolated acceptance checks.
- `run.py`: local-only server entry point.

Task3 remains a separate requirements-analysis report. The software and its tests do not substitute for the required models and team contribution statement.
