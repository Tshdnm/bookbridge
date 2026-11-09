# Task3 refined requirements-analysis model pack

Recorded on 9 November 2026. This pack contains the 12 model editions used for the final Task3 report, prepared and visually checked during 7–8 November. It supersedes the earlier system-level sequence draft for report use; the [2 November draft](../task3/README.md) remains available as historical evidence.

## Report status

The 35-page English report follows the school cover and report template. On 9 November, the team leader confirmed that the final PDF had been submitted to Moodle. The actual submission date has not yet been supplied. **9 November is the confirmation-record date, not an inferred submission date.** The published course deadline is 12 November 2026 at 23:59.

The submitted report's PDF and editable Word file remain in the team's delivery files. They are not copied into this public pack because their cover contains student identifiers. This public pack provides the editable technical models without those identifiers.

## Model inventory

There is one use-case diagram, one object snapshot, nine sequence diagrams (one per UC-01 through UC-09), and one supplementary reservation-state diagram. The nine refined sequences show interactions between the user, boundary views, business controls and logical domain objects or collections. They remain requirements-analysis models, not a prescription of implementation classes, endpoints or database tables.

| ID | Model | View | Editable sources |
| --- | --- | --- | --- |
| UC-OVERVIEW | BookBridge user goals | [SVG](models/01-use-cases.svg) | [PlantUML](models/01-use-cases.puml) / [Graphviz](models/01-use-cases.dot) |
| OD-01 | Illustrative BookBridge object snapshot | [SVG](models/02-object-snapshot.svg) | [PlantUML](models/02-object-snapshot.puml) / [Graphviz](models/02-object-snapshot.dot) |
| SD-01 | Maintain the book catalogue | [SVG](models/03-sequence-uc-01.svg) | [PlantUML](models/03-sequence-uc-01.puml) / [Graphviz](models/03-sequence-uc-01.dot) |
| SD-02 | Record stock receipts | [SVG](models/04-sequence-uc-02.svg) | [PlantUML](models/04-sequence-uc-02.puml) / [Graphviz](models/04-sequence-uc-02.dot) |
| SD-03 | Browse and find books | [SVG](models/05-sequence-uc-03.svg) | [PlantUML](models/05-sequence-uc-03.puml) / [Graphviz](models/05-sequence-uc-03.dot) |
| SD-04 | Create a reservation | [SVG](models/06-sequence-uc-04.svg) | [PlantUML](models/06-sequence-uc-04.puml) / [Graphviz](models/06-sequence-uc-04.dot) |
| SD-05 | Cancel an own pending reservation | [SVG](models/07-sequence-uc-05.svg) | [PlantUML](models/07-sequence-uc-05.puml) / [Graphviz](models/07-sequence-uc-05.dot) |
| SD-06 | Confirm collection | [SVG](models/08-sequence-uc-06.svg) | [PlantUML](models/08-sequence-uc-06.puml) / [Graphviz](models/08-sequence-uc-06.dot) |
| SD-07 | View own reservations | [SVG](models/09-sequence-uc-07.svg) | [PlantUML](models/09-sequence-uc-07.puml) / [Graphviz](models/09-sequence-uc-07.dot) |
| SD-08 | View and filter all reservations | [SVG](models/10-sequence-uc-08.svg) | [PlantUML](models/10-sequence-uc-08.puml) / [Graphviz](models/10-sequence-uc-08.dot) |
| SD-09 | Summarise completed reservations | [SVG](models/11-sequence-uc-09.svg) | [PlantUML](models/11-sequence-uc-09.puml) / [Graphviz](models/11-sequence-uc-09.dot) |
| ST-01 | Reservation lifecycle | [SVG](models/12-reservation-state.svg) | [PlantUML](models/12-reservation-state.puml) / [Graphviz](models/12-reservation-state.dot) |

`models/manifest.json` records model purposes, requirements and file names. Each SVG is the rendered Graphviz edition; `.dot` and `.puml` are editable alternatives. The Graphviz editions were rendered and visually checked as part of the report preparation. PlantUML files are retained as source alternatives; this update does not claim a separate PlantUML compilation run.

## Consistency rules

- One reservation contains one title and a positive whole-number quantity.
- Creation saves the owner, quantity, price and Pending collection state while deducting stock once; these changes succeed together or neither changes.
- Only the owning customer cancels a pending reservation; cancellation restores the stored quantity once.
- Only staff confirm collection; completion does not deduct stock again.
- Completed and Cancelled are terminal states. Repeated or conflicting transitions are refused without further data effects.
- Unlisting blocks new reservations and retains existing records. Catalogue price edits do not change saved reservation prices.
- Completed totals use saved prices and quantities. They are reservation amounts, not verified payments or all bookstore revenue.

The object snapshot is an illustrative instant containing concrete object identities, slots and links. Its values are not a claim about the current demonstration database.

## Ownership and verification

F1 owns catalogue/receipt models and the object snapshot; F2 owns discovery and the use-case overview; F3 owns reservation, cancellation, collection and the state model; F4 owns query/totals models and traceability. This is the assigned responsibility map, not a claim that each member independently authored or reviewed the common material.

The submitted Task2 baseline remains unchanged. Acceptance mappings and use-case specifications can be read in the [earlier traceability file](../task3/traceability.md) and [use-case specifications](../task3/use-case-specifications.md). A completed report does not establish completed software acceptance. See the [current status](../development-status.md) and [9–15 November plan](../week-2026-11-09.md) for remaining reviews.
