# BookBridge model traceability

**AI-assisted review draft — 2026-11-02.** IDs refer to the submitted Task2 version 1.0 baseline. “Acceptance” below means planned criteria from that specification, not a claim that the tests were executed or passed.

## Functional requirements

| Requirement | User goal | Dynamic model | Key governing rules | Planned acceptance |
|---|---|---|---|---|
| FR-01 Maintain catalogue | UC-01 | SD-01 | DR-08 preserves unlisted books/records; DR-09 validates initial stock; SEC-02 staff access; saved prices preserved | AT-01, AT-06 |
| FR-02 Stock receipts | UC-02 | SD-02 | DR-09 positive additions only; SEC-02 staff access; no partial addition | AT-01 |
| FR-03 Browse/find | UC-03 | SD-03 | DR-02 listed zero-stock titles remain visible but cannot be reserved | AT-01, AT-03 |
| FR-04 Create reservation | UC-04 | SD-04 | DR-01 one title/positive integer; DR-02 listing/stock; DR-03 initial state and deduction; DR-04 saved price; REL-02 atomic effects | AT-02, AT-03; AT-05 price continuity |
| FR-05 Cancel own pending | UC-05 | SD-05 | DR-05 own cancellation/restoration once; DR-07 terminal states; DR-08 unlisting; SEC-01 ownership; REL-02 atomic effects | AT-04, AT-06 |
| FR-06 Confirm collection | UC-06 | SD-06 | DR-04 saved price; DR-06 staff completion/no deduction; DR-07 terminal states; DR-08 unlisting; SEC-02 staff access | AT-05, AT-06 |
| FR-07 Own queries | UC-07 | SD-07 | SEC-01 owner-only list/detail; stored state and saved amount; no read side effects | AT-07; AT-04 foreign-detail denial |
| FR-08 Staff queries/filter | UC-08 | SD-08 | SEC-02 staff-only; three exact status values; read-only access | AT-07 |
| FR-09 Completed summary | UC-09 | SD-09 | DR-10 Completed only; DR-04 saved prices; SEC-02 staff-only; no read side effects | AT-08; AT-05 price continuity |

UC-OVERVIEW contains all nine goals and the two actors. OD-01 supplies illustrative instances of the logical Book, Reservation and TestIdentity concepts used throughout. ST-01 cross-checks the state-changing goals UC-04, UC-05 and UC-06. There is exactly one sequence diagram for each use case in the overview; no hidden additional registration, payment or administrative goal is introduced.

## Domain rule coverage

| Rule | Main model evidence |
|---|---|
| DR-01 One title and positive integer quantity | UC/SD-04; OD-01 one reserved-title link per reservation |
| DR-02 Listed title and enough stock; visible zero-stock titles | UC/SD-03 and 04 |
| DR-03 Unique reference, owner, initial status and one stock deduction | UC/SD-04; ST-01 |
| DR-04 Saved price and derived amount | UC/SD-04, 06 and 09; OD-01 current price 50.00 versus saved 30.00 |
| DR-05 Owning customer cancels pending and restores once | UC/SD-05; ST-01 |
| DR-06 Staff completes pending without another deduction | UC/SD-06; ST-01 |
| DR-07 Terminal states; no repeated effects or reversal | UC/SD-05 and 06 refusal alternatives; ST-01 |
| DR-08 Unlisting blocks new reservations and preserves old ones | UC/SD-01, 03, 04, 05 and 06; OD-01 unlisted book retains link |
| DR-09 Initial non-negative stock and later positive receipts | UC/SD-01 and 02 |
| DR-10 Completed-only totals from saved values | UC/SD-09; OD-01 summary example |

## Cross-cutting quality targets

| Baseline target | How the models respect it | Evidence still required beyond models |
|---|---|---|
| PERF-01 Response within 3 seconds | Search, submission and query have explicit result/error responses | Timed representative actions on the recorded demo computer/browser |
| SEC-01 Customer ownership | UC/SD-05 and 07 check owner before details or changes | Two-customer list/detail/cancellation checks, AT-04 and AT-07 |
| SEC-02 Staff restrictions | UC/SD-01, 02, 06, 08 and 09 reject unauthorised actors | Customer attempts against all protected operations, including AT-06 |
| SEC-03 Sample data and predefined roles | OD-01 uses fictional labels; no real phone/address/payment data | Inspection of demo data and displayed inputs |
| AVA-01 Local classroom availability | One local system boundary; no hosting service is modelled | Successful operation throughout the agreed demonstration session |
| CAP-01 20 titles and up to 100 reservations | No extra scale or concurrent-load assumption is introduced | Acceptance dataset prepared and recorded for AT-09 |
| CAP-02 One active operator | Sequential actor-system interactions | Recorded test setup; concurrent-user load is not claimed |
| REL-01 Persistence through normal refresh/restart | Stored logical records retained across read operations | Refresh and normal shutdown/restart checks, AT-09 |
| REL-02 Consistent state/stock changes | UC/SD-04 and 05 show all-or-neither saves; ST-01 rejects repeat terminal actions | Successful and failed-operation checks; inspect both record and stock |
| USE-01 Consistent labels and clear validation | Exact three status labels; explicit empty/error alternatives | Browser review of labels and field-specific errors, AT-09 |

## Important baseline choices

- The model uses the later Task2 baseline: local sample data, predefined identities, one active operator, and no required reporting-period filter or concurrent-load testing.
- Nine functional requirements are nine user-goal use cases here. Catalogue creation/editing/listing share UC-01; optional detail viewing is part of discovery/query goals. This keeps every use case paired with a sequence diagram.
- A terminal operation is explicitly refused and leaves data unchanged. The model does not depict a successful repeated cancellation/collection or a return to Pending collection.
- Financial values are generic demo units. Completed reservation amount is derived from saved prices and is not evidence of payment.
- The object diagram is an illustrative snapshot that supports relationship and slot reasoning. It is not the full acceptance dataset, and its examples do not assert actual transactions or test outcomes.
