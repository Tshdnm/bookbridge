# Development status

## Update recorded on 9 November 2026

This section supplements the 2 November record. Earlier observations retain their original date and scope.

### Requirements analysis and first presentation

The Task3 report was finalised and visually checked on 7–8 November. The 35-page English report contains one use-case diagram, one object snapshot, nine object interaction sequence diagrams and one reservation state diagram. The final PDF and editable Word file are available. On 9 November, the team leader confirmed that the final PDF had been submitted to Moodle. The actual submission date is still to be supplied. The date of this confirmation must not be used as the submission date.

On 9 November, materials were prepared for the first presentation on 12 November: 16 English slides, four Chinese scripts and a rehearsal/Q&A guide. The speaking plan assigns F1 slides 1–5, F2 slides 6–8, F3 slides 9–12 and F4 slides 13–16. It targets 14 minutes plus a one-minute buffer. The slides and script pages were visually checked. Full-group rehearsal and presentation delivery remain planned actions; preparation of common materials does not establish individual completed contributions.

### Focused browser evidence on 9 November

Screenshots were captured from the existing local prototype using a separate sample database, leaving the original application source and existing demonstration data unchanged. The observed paths were:

1. Search with keyword `e`, Technology category and ascending price order.
2. As Demo customer A, reserve two copies of *The Quiet Bookshop* at 30.00 units each. The saved amount is 60.00 and available stock changes from 5 to 3.
3. As Demo staff, confirm collection. Stock remains 3. The completed summary shows one reservation, two copies and 60.00 units.
4. Open the stock-receipt dialog as a preview, without submitting a receipt.

This is a focused browser walkthrough, not complete manual acceptance, a browser timing result, or evidence that an assigned member performed an independent review. No new feature implementation is claimed for this session. The ten-test automated result remains dated 2 November.

### Next checks

Add the actual Task3 submission date when supplied and retain the Moodle confirmation. Rehearse together by 11 November and deliver the first presentation on 12 November. Record the actual feedback afterward. During 13–15 November, each owner performs the assigned module review and acceptance checks, with F2 leading AT-09 browser timing and F4 assisting persistence verification. See `docs/week-2026-11-09.md` for responsibilities and evidence requirements.

The verified GitHub destination is `Tshdnm/bookbridge`, branch `stage-2026-11-02`, with draft pull request #1. Repository publication and Feishu changes should be recorded as completed only after the new saved results are verified. The course-organisation repository has not yet been confirmed as synchronised. No deployment or production integration is claimed.

---

Recorded on 2 November 2026.

The team reported that Task1 and Task2 had been submitted and that no program code had been written before this development session. Task3 had not been written. Existing main contained only the original README, committed on 5 October 2026.

The new work starts on the actual development date. The development stages below are implementation milestones, not claims of work in previous calendar weeks.

## Implementation stages

1. **Data and business operations**: SQLite schema, sample catalogue, customer/staff identities, catalogue maintenance, receipts, discovery, atomic reservation rules, queries and completed totals.
2. **Browser workflow and verification**: accessible browser pages, customer/staff operations, validation and empty states, duplicate-submission handling, and isolated acceptance tests.

## Verified automatically

Ten unittest tests passed on 2 November 2026 after fixing non-ASCII CSRF-header handling. A subsequent requirements review found that repeated terminal actions returned success instead of the explicit rejection required by FR-05/06. That behaviour was corrected: repeated cancellation/collection returns a specific conflict error and leaves data unchanged. The existing tests were tightened and all ten passed again (1.901 seconds for the complete suite; this is not a browser-response benchmark).

The checks exercise catalogue validation and search, stock receipts, reservation idempotency, invalid input, owner restrictions, one-time cancellation, saved prices, collection without a second deduction, unlisting, status filtering, completed totals, normal restart persistence, 100 reservation records, and rejection of invalid CSRF headers.

These checks validate the implementation under sample conditions. Browser-level timing, the owners' walkthrough, and acceptance with the assigned customer group remain separate tasks. Do not mark those as passed until they are performed and recorded.

## Browser smoke check

On 2 November, a browser walkthrough created a one-copy reservation for The Quiet Bookshop, opened the page's cancellation confirmation, selected **Keep unchanged** and verified it remained pending, then confirmed cancellation and verified the cancelled record and restored stock. A previously completed two-copy reservation remained visible. This is a focused UI smoke check, not all nine classroom acceptance scenarios or a three-second browser measurement.

## Team review before classroom acceptance

- Each owner runs the corresponding feature, explains its source code and verifies the matching requirements.
- Run AT-01 through AT-09 in the selected demonstration browser and record observed results and evidence.
- Record the demo device/browser and browser-level response times against the three-second target.
- Check the agreed terms and money label with the customer contact.
- Write Task3 using one permitted modelling route and submit its PDF by 12 November 2026 at 23:59, as shown in the course assignment page.
- Update Feishu with actual completion dates, defects and commit links as work happens.

No real bookstore stock, customer data, payment service or existing store software is connected.

The teaching assistant's later clarification allows progress according to the team's own pace and accepts local operation. The current stage is 2-8 November; Task3 is in progress and not submitted. Optional hosting will be evaluated separately. Final readiness is internally targeted for 5 December, pending the official final-project schedule.
