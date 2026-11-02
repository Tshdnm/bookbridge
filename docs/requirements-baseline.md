# BookBridge requirements baseline

Review draft recorded on **2 November 2026**, based on the team's submitted Task2 User Requirements Specification, version 1.0 dated 12 October 2026. This summary does not change that submitted baseline.

## Purpose and boundary

A browser-based prototype for **one local bookstore**. Customers find a title, reserve copies and collect them in store. Staff maintain sample catalogue records and received stock, confirm collection, query reservations and inspect completed totals.

The acceptance setup uses 20 sample titles, up to 100 reservations, at least two predefined customer identities and one staff identity. One operator performs actions sequentially in the chosen desktop browser. These identities demonstrate role rules; they are not real customer accounts.

## Functional ownership and traceability

| Requirement | User goal | Planned functional owner | Acceptance coverage |
| --- | --- | --- | --- |
| FR-01 | Maintain catalogue fields and listing status | F1 owner | AT-01, AT-06 |
| FR-02 | Add a positive whole-number stock receipt | F1 owner | AT-01 |
| FR-03 | Browse details, search title/author, filter category, sort price | F2 owner | AT-01, AT-03 |
| FR-04 | Reserve copies of one listed, available title | F3 owner (team coordinator) | AT-02, AT-03, AT-05 |
| FR-05 | Cancel an owned pending reservation | F3 owner (team coordinator) | AT-04, AT-06 |
| FR-06 | Staff confirm collection of a pending reservation | F3 owner (team coordinator) | AT-05, AT-06 |
| FR-07 | Customer view only their own reservations | F4 owner | AT-07 |
| FR-08 | Staff view all reservations and filter by status | F4 owner | AT-07 |
| FR-09 | Show completed reservation quantities and saved amounts | F4 owner | AT-05, AT-08 |

AT-09 is cross-cutting: it checks response time, capacity, persistence and demonstration availability under the stated sample conditions.

These allocations reproduce the submitted report's responsibilities. They do not assert that a member authored or accepted the current AI-assisted initial implementation.

## Business invariants

1. Each reservation concerns exactly one title and a positive whole-number quantity.
2. Creation rechecks listing, available stock and current price; it saves the price and deducts stock once in the same transaction.
3. A repeated submission for the same request does not create another reservation.
4. Only the owning customer may cancel a **Pending collection** reservation. Cancellation restores the reserved quantity once.
5. Only staff may complete a pending reservation. Collection changes the status to **Completed** without a second deduction.
6. **Completed** and **Cancelled** are terminal states. Further transitions are rejected with a clear message and no data change.
7. Unlisting prevents new reservations but preserves existing reservation records.
8. Summary values use only completed records and their saved unit prices. They are not verified payments or all bookstore sales.

## Quality and data requirements

- Relevant search, reservation and query actions must display a result or specific error within the Task2 three-second target under the stated sample conditions. Full browser timing remains to be measured.
- Committed catalogue and reservation data must survive normal refresh and restart.
- Reservation and stock changes must succeed together or neither may be saved.
- Customer ownership and staff-only operations must be checked.
- Use sample data without real addresses, phone numbers or payment credentials.
- Consistent labels, specific errors and empty-result messages are required.

## Outside the agreed initial scope

No cart, online payment, delivery, registration/password recovery, notification service, automatic reservation expiry, staff cancellation, arbitrary reservation editing, stocktaking corrections, physical record deletion, recommendation engine, or live bookstore database synchronization.

Online demonstration hosting is an **optional later experiment**. The TA clarified that local operation is acceptable; hosting does not make the prototype a production bookstore system or expand the agreed feature scope.

## Source and open decisions

- Submitted Task1 Project Proposal: purpose, functional ownership and preliminary plan.
- Submitted Task2 User Requirements Specification v1.0: authoritative FR-01 through FR-09, domain rules, quality constraints and planned AT-01 through AT-09.
- Task3 assignment: one modelling route; this draft uses the object-oriented route, including an object diagram and a sequence diagram for each use case.
- Course page: Task3 PDF deadline **12 November 2026, 23:59**.
- TA clarification supplied by the team on 2 November: no fixed current implementation milestone; submit actual progress; local demonstration is acceptable.
- The official final-project date and final material list remain unconfirmed. **5 December 2026** is the team's internal readiness target only.

