# BookBridge requirements analysis models

**AI-assisted review draft — 2026-11-02.** This package prepares the models for Task3, Option 2 (Object-Oriented Requirements Analysis). It needs team review and incorporation into the final report. It does not assert that any member authored, reviewed or submitted this package, or that the acceptance scenarios have passed.

## Basis and scope

The requirements baseline is *BookBridge D2-Team7 User Requirements Specification*, version 1.0, dated 12 October 2026. The applicable assignment is *Task3 Requirements Analysis*, pages 1 and 3. The assignment requires a use case diagram, an object diagram, and a sequence diagram for **each** use case. Additional diagrams are optional. The report must identify the division of labour, use tool-drawn diagrams, and be submitted as one PDF by the team leader.

BookBridge is a local, single-store prototype with sample book records and predefined customer and staff identities. Customers find books, reserve copies of one title, manage their own reservations and collect books in person. Staff maintain books and stock, confirm collection, query reservations and view completed-reservation totals. Payment, physical collection and the existing bookstore software are outside the system boundary. No registration, shopping cart, online payment, delivery, notification, expiry, refund or legacy-system synchronisation is added here.

## Model inventory

There are **12 diagrams**: one use case diagram with nine goals, one genuine object diagram, nine corresponding sequence diagrams, and one supplementary state diagram. `manifest.json` records each diagram's ID, purpose, requirement coverage and source/output filenames.

| Model | Content | Files |
|---|---|---|
| UC-OVERVIEW | Nine customer/staff user goals within the BookBridge boundary | `01-use-cases.*` |
| OD-01 | Concrete identities, books and reservations with slot values and links | `02-object-snapshot.*` |
| SD-01 to SD-09 | One dynamic model for each UC-01 to UC-09 | `03-sequence-uc-01.*` to `11-sequence-uc-09.*` |
| ST-01 | Creation, cancellation, collection and retained terminal states | `12-reservation-state.*` |

The `*.puml` files are standalone PlantUML sources. The `*.dot` files and corresponding SVGs provide a locally rendered Graphviz edition of the same model logic. The SVGs are vector images suitable for insertion into a report. The renderer can generate local `previews/` PNG review copies; these are not committed. No online rendering service is required.

| Figure | View the rendered model | Editable PlantUML source |
| --- | --- | --- |
| Use case overview | [SVG](01-use-cases.svg) | [Source](01-use-cases.puml) |
| Object snapshot | [SVG](02-object-snapshot.svg) | [Source](02-object-snapshot.puml) |
| UC-01 Catalogue | [SVG](03-sequence-uc-01.svg) | [Source](03-sequence-uc-01.puml) |
| UC-02 Stock receipts | [SVG](04-sequence-uc-02.svg) | [Source](04-sequence-uc-02.puml) |
| UC-03 Discovery | [SVG](05-sequence-uc-03.svg) | [Source](05-sequence-uc-03.puml) |
| UC-04 Reservation | [SVG](06-sequence-uc-04.svg) | [Source](06-sequence-uc-04.puml) |
| UC-05 Cancellation | [SVG](07-sequence-uc-05.svg) | [Source](07-sequence-uc-05.puml) |
| UC-06 Collection | [SVG](08-sequence-uc-06.svg) | [Source](08-sequence-uc-06.puml) |
| UC-07 Own reservations | [SVG](09-sequence-uc-07.svg) | [Source](09-sequence-uc-07.puml) |
| UC-08 Staff query | [SVG](10-sequence-uc-08.svg) | [Source](10-sequence-uc-08.puml) |
| UC-09 Completed totals | [SVG](11-sequence-uc-09.svg) | [Source](11-sequence-uc-09.puml) |
| Reservation lifecycle | [SVG](12-reservation-state.svg) | [Source](12-reservation-state.puml) |

Validation on 2 November: all 12 Graphviz outputs rendered and were visually reviewed; an independent source review found no blocking inconsistency against Task2. The PlantUML source was retained but not compiled in this environment. Student review and formal acceptance are still pending.

## Reading the sequence diagrams

These are UML **system sequence diagrams** at requirements level. The actor and the BookBridge system are the lifelines. Numbered solid arrows are requests; dashed arrows are responses. `alt` frames show mutually exclusive alternatives; `opt` frames show optional behaviour. Notes specify required validation and observable data effects. They do not prescribe frameworks, endpoints, database tables or controller classes.

Every protected operation checks the current predefined identity. Staff permissions and customer ownership are explicit alternatives where relevant. An error does not establish a new successful state. The sequence models cover normal results, invalid or unauthorised input, and save/read failures. Catalogue creation, editing and listing are alternative behaviours within UC-01 rather than additional unmodelled user goals. Read-only lists may offer another use case as an action; they do not automatically execute cancellation or collection. Therefore the overview does not use misleading mandatory `include` relationships.

## Object snapshot

OD-01 is an instance snapshot, **not a class diagram**. Each underlined `instance : Type` heading identifies an object; each `attribute = value` entry is a slot. Lines are actual owner/title links in the illustrated snapshot. Each reservation has exactly one owner and one book. `/amount` is derived from its stored quantity and saved unit price.

The example is deliberately illustrative. A consistent history is: book A starts with five copies; an earlier one-copy reservation is cancelled and restores stock; a later two-copy reservation leaves three available; its saved price is 30.00 even after the catalogue price changes to 50.00. Book B starts with five copies; a one-copy reservation is completed, leaving four available, and the title is subsequently unlisted. Only the completed R-02 contributes to the snapshot summary: **one copy and 20.00 demo units**. The unlinked staff identity illustrates the permitted role; the requirements do not mandate recording a staff-reservation association.

## Rules that must remain consistent

1. One reservation contains one title and a positive integer quantity. A new reservation needs a listed title and enough available copies.
2. Creation saves the current price, quantity, owner and Pending collection state, and deducts stock once. These changes succeed together or neither changes.
3. Only the owning customer may cancel a pending reservation. Cancellation restores the stored quantity once and preserves the Cancelled record, even if the title has since been unlisted.
4. Only staff may confirm collection. Completion does not deduct stock again and retains the saved price and quantity.
5. Completed and Cancelled are retained terminal states. Repeated or conflicting transitions receive a clear refusal and have no further stock, state or total effect. No reversal is modelled.
6. Unlisting prevents new reservations while preserving the book and existing reservations. Editing book details does not reset stock or change saved reservation prices. Later stock receipts only add positive integers.
7. Summary totals include Completed records only, using saved prices. These are reservation amounts, not verified payment receipts or all bookstore sales.

## Coverage and review

`use-case-specifications.md` contains the nine goal specifications. `traceability.md` connects FRs, UCs, sequence diagrams, domain rules and planned acceptance scenarios, and lists cross-cutting quality targets. These targets are not claimed to be verified by a diagram.

The acceptance mapping includes FR-03 → AT-01/AT-03, FR-04 → AT-02/AT-03/AT-05, FR-05 → AT-04/AT-06, FR-06 → AT-05/AT-06 and FR-09 → AT-05/AT-08. AT-09 covers cross-cutting response, persistence, capacity and interface consistency checks; it is not a tenth user goal.

Suggested review ownership below follows the module allocation already stated in Task2. It is **not** a completed-contribution record; the final report must describe work actually performed.

| Suggested reviewer | Scope to review |
|---|---|
| F1 owner | UC/SD-01 and 02, catalogue and receipt rules |
| F2 owner | UC/SD-03, customer discovery path and overview |
| F3 owner (team coordinator) | UC/SD-04 to 06, state model and cross-model consistency |
| F4 owner | UC/SD-07 to 09, ownership/query filters and summary arithmetic |
| Whole team | Object snapshot, requirement coverage, final wording and actual division of labour |

Before submission, verify that Option 2 is the team's chosen route, review all figures and labels, integrate them with the course cover and report narrative, and replace the suggested review allocation with the actual contribution record. The Moodle screenshot supplied by the team gives the Task3 deadline as **12 November 2026 at 23:59**. This draft is not a Moodle submission.

## Rebuilding the local diagram edition

`generate_models.py` generates the nine sequence source pairs, the overview/object DOT sources and the manifest. The standalone overview/object PlantUML and state sources are maintained alongside it. Run the generator with Python 3, then run `render_models.mjs` with Node.js and an installed `@viz-js/viz` plus `sharp`. The renderer supports `TASK3_NODE_MODULES` to locate those packages. It uses Graphviz `dot` for the object and state diagrams, and fixed-position `neato` for the overview and system sequence diagrams. PlantUML sources remain available for an independent standard PlantUML rendering workflow.

## Sources

- *Task3 Requirements Analysis*, PDF pages 1 and 3: choice of route, required diagrams, report and submission rules.
- *BookBridge D2-Team7 User Requirements Specification*, version 1.0, 12 October 2026: pages 4–8 scope and users; pages 9–17 FR-01 to FR-09; page 18 logical records; page 19 quality targets; page 20 domain rules and state transitions; page 21 AT-01 to AT-09; page 22 requirements traceability.
- *Surface for Requirements Analysis*: report cover and structural template. Its placeholder content is not project evidence.

The proposal's earlier tentative scope is not used to add date-range analytics or concurrent-load acceptance to the later Task2 baseline.
