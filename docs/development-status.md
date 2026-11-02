# Development status

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
