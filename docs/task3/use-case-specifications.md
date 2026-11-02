# BookBridge use case specifications

**AI-assisted review draft — 2026-11-02.** The following nine goals refine the Task2 version 1.0 baseline. They describe required behaviour, not completed development or executed tests. Each has a corresponding SD diagram.

Common context: the local prototype is running with its sample dataset. Protected operations use the current predefined identity. Rejected changes preserve all stored data; failed reads show an error rather than invented results. Inputs, status names and errors use consistent labels. No real customer contact or payment details are collected.

## UC-01 Maintain the book catalogue

**Primary actor:** Staff. **Requirement:** FR-01. **Dynamic model:** SD-01.

**Goal and trigger:** Create a title, edit basic details, or change its listing state. Staff open the catalogue and submit the chosen operation.

**Input:** Title, author, category, non-negative unit price with at most two decimals and listing state. Creation also takes non-negative integer initial stock; editing identifies an existing book.

**Main flow:** The system checks staff access and validates the input. For creation, it assigns a unique identifier and prepares the new book. For editing/listing, it changes only the selected basic details or listing state. It saves the valid change and displays the stored book, updated catalogue and success message.

**Alternatives:** Reject non-staff access, missing required text, invalid price/initial stock or unknown book. A save failure shows a specific error and preserves editable input without a partial stored change.

**Postconditions and invariants:** No physical deletion. Editing does not reset stock or alter saved reservation prices. Unlisting blocks new reservations but preserves all existing records. Later stock additions use UC-02.

**Planned acceptance:** AT-01 and AT-06.

## UC-02 Record stock receipts

**Primary actor:** Staff. **Requirement:** FR-02. **Dynamic model:** SD-02.

**Goal and trigger:** Record received copies of an existing title. Staff select the title and enter a receipt quantity.

**Preconditions/input:** Current staff identity, existing book identifier and a positive integer quantity. The title may be listed or unlisted; listing is not a stated prerequisite for recording receipts.

**Main flow:** Show the selected book and current available quantity. Validate the role, identifier and quantity. Add the received quantity once to stored availability. Save and display the resulting stored quantity with a success message.

**Alternatives:** Reject non-staff access, an unknown book, or a blank, zero, negative or fractional quantity. A failed save leaves stock unchanged.

**Postconditions and invariants:** Availability increases by exactly the confirmed receipt quantity. Existing reservations are unchanged. Stocktaking reductions, purchase orders, suppliers and external synchronisation are outside scope.

**Planned acceptance:** AT-01.

## UC-03 Browse and find books

**Primary actor:** Customer. **Requirement:** FR-03. **Dynamic model:** SD-03.

**Goal and trigger:** Find a suitable listed title and inspect its details. The customer opens the catalogue, searches, filters, sorts or selects a title.

**Input:** Optional title-or-author keyword, optional category, price ascending/descending order, or selected book identifier.

**Main flow:** Trim the keyword, search title or author, apply the category filter and requested price order, and return matching listed titles. Display title, author, category, current price and availability. If the customer opens a result, recheck its existence/listing and display its details.

**Alternatives:** Blank keyword means all listed titles subject to category. No matches is a normal empty result. Listed zero-stock titles remain visible and are marked unavailable for reservation. A missing or newly unlisted selected title gives an unavailable message and a route back to the catalogue. Read failures give an error.

**Postconditions:** Catalogue and reservation data are unchanged. Reserving is the separate UC-04 goal.

**Planned acceptance:** AT-01 and AT-03.

## UC-04 Create a reservation

**Primary actor:** Customer. **Requirement:** FR-04. **Dynamic model:** SD-04.

**Goal and trigger:** Reserve a positive number of copies of one title for collection. The customer submits the reservation form.

**Input/preconditions:** Current customer identity, one book identifier and positive integer quantity. Show current price and availability before submission. The customer does not supply the price or contact/payment details.

**Main flow:** Suppress repeated submission while processing. Recheck current listing, price and stock. Allocate a unique reservation reference, retain the owner, title, quantity and current unit-price snapshot, and set Pending collection. Save the reservation and stock reduction together. Show the reference, title, quantity, saved price, derived amount and status.

**Alternatives:** Reject missing customer context, invalid quantity, unknown/unlisted title or insufficient stock. Preserve editable input and show the specific reason. If saving fails, create no reservation and do not reduce stock. Repeated submission of the same operation or refreshing its successful result must not create a second reservation.

**Postconditions:** Available stock falls by the reserved quantity once. Amount equals quantity times saved price and survives later catalogue price changes.

**Planned acceptance:** AT-02 and AT-03; saved-price continuity is also exercised by AT-05.

## UC-05 Cancel an own pending reservation

**Primary actor:** Customer. **Requirement:** FR-05. **Dynamic model:** SD-05.

**Goal and trigger:** Release an own reservation that is still pending. The customer selects the cancellation action for its reference.

**Input/preconditions:** Current customer identity and reservation reference. The successful path requires ownership and current Pending collection status; check both when the action is requested.

**Main flow:** Verify identity and ownership without disclosing another customer's details. Read the current status. Change Pending collection to Cancelled and restore the quantity stored on that reservation exactly once. Save stock and status together and show the retained Cancelled record and confirmation.

**Alternatives:** Reject missing identity, unknown/foreign-owned records, and Completed or Cancelled states. This includes repeat cancellation: return a clear refusal with no additional restoration. On save failure, neither status nor stock changes. Unlisting the title does not block an otherwise eligible cancellation.

**Postconditions:** The reservation remains in history as Cancelled. No refund, expiry, extension, staff cancellation or reversal occurs.

**Planned acceptance:** AT-04 and AT-06.

## UC-06 Confirm collection

**Primary actor:** Staff. **Requirement:** FR-06. **Dynamic model:** SD-06.

**Goal and trigger:** Record that a pending reservation has been collected. Staff request a reference, check its collection details, then confirm.

**Input/preconditions:** Current staff identity and reservation reference. Display owner/demo identity, title, quantity, saved unit price, amount and current status before confirmation.

**Main flow:** Verify staff access and locate the record. Staff check reference, owner, title and quantity. Recheck Pending collection status at confirmation, save Completed and show success. Keep the existing quantity and saved price.

**Alternatives:** Reject non-staff access, unknown references and terminal states. Repeat collection or collection of a Cancelled record gives a clear refusal and no further change. A failed save leaves status unchanged. A title's later unlisting does not prevent collection of an existing pending reservation.

**Postconditions:** Stock is unchanged because it was deducted at creation. The record enters completed totals once. Payment and physical collection happen outside BookBridge; this action does not authorise or verify payment.

**Planned acceptance:** AT-05 and AT-06.

## UC-07 View own reservations

**Primary actor:** Customer. **Requirement:** FR-07. **Dynamic model:** SD-07.

**Goal and trigger:** Inspect personal reservation history or a selected record. The customer opens My reservations or requests a reference.

**Input/preconditions:** Current customer identity; optional selected reference. Ownership filtering applies before data is returned, including detail requests.

**Main flow:** Return only records owned by the current customer across the three statuses. Show reference, title, quantity, saved price, derived amount and current status. Offer the separate UC-05 action only for eligible pending records.

**Alternatives:** An empty list gives a no-reservations message. Reject missing identity or another customer's reference without revealing its contents. An unknown reference gives not found; a read failure gives an error.

**Postconditions:** Read-only. Opening or refreshing does not alter stock or records. No editing of items/quantities, export or notification is available.

**Planned acceptance:** AT-07, with foreign-detail denial also covered by AT-04.

## UC-08 View and filter all reservations

**Primary actor:** Staff. **Requirement:** FR-08. **Dynamic model:** SD-08.

**Goal and trigger:** Inspect all BookBridge reservations or those in a selected status. Staff open reservations, choose a filter or select a reference.

**Input/preconditions:** Staff identity; All, Pending collection, Completed or Cancelled; optional selected reference.

**Main flow:** Check staff access and supported status. Read matching records across customers. Show reference, customer demo identity, title, quantity, saved amount and current status. All includes all three statuses. Pending records may expose the separate UC-06 collection action.

**Alternatives:** Reject non-staff access and unsupported status values. An empty filtered list gives an explicit empty-results message. An unknown selected reference gives not found; a failed read gives an error.

**Postconditions:** Read-only. No staff cancellation, arbitrary reservation editing, date-range analytics or file export is added.

**Planned acceptance:** AT-07.

## UC-09 Summarise completed reservations

**Primary actor:** Staff. **Requirement:** FR-09. **Dynamic model:** SD-09.

**Goal and trigger:** View completed-copy count and completed-reservation amount. Staff request the summary.

**Input/preconditions:** Current staff identity. No reporting-period selection or currency conversion is required.

**Main flow:** Check staff access. Select only Completed records. Sum their quantities and sum each quantity times its saved unit price. Display Completed copies and Completed reservation amount, with the latter formatted to two decimal places and labelled as covering BookBridge records only.

**Alternatives:** If no completed records exist, both totals are zero. Reject non-staff access. If records cannot be read, show an error instead of a misleading zero or partial total.

**Postconditions:** Read-only; repeated reads do not alter totals. Pending and Cancelled records are excluded. Current catalogue prices are not used. The amount is not verified payment revenue or the bookstore's overall sales.

**Planned acceptance:** AT-08; AT-05 additionally checks saved-price continuity through collection.
