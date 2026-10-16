# RR-001 approved behavior v2

Owner: Jo. Approved: 2026-10-10 10:00 UTC. Launch target: 2026-10-16 10:00 UTC. Replaces proposal v1 for the 2,000-account cohort.

## Customer behavior

Manage Plan → Cancel subscription → review paid-access end date → Confirm cancellation. Show completion only after billing acknowledges it. Keep paid access until term end; stop future renewals after confirmed cancellation. Do not say access ends immediately. A pending request or a click alone is not confirmation.

The cancellation email is a billing receipt and is sent regardless of marketing-message settings. Optional renewal reminders remain controlled by the existing toggle and run seven days before renewal. No price or refund policy changes: Pro is $49/month; refund requests require Sam's billing review with no first-contact promise.

## Known issue KI-17

On slow responses the invoice page can display a stale renewal date for up to ten minutes after confirmed cancellation. Dev's simulated test T-17 confirms this display issue; it does not establish that a specific customer's charge is valid. Support must confirm the billing cancellation record, explain the display delay and escalate any actual post-cancellation charge to Sam. Refreshing the page is not a guarantee that billing is correct.

Jo accepts KI-17 for the limited cohort only if this guidance is available to agents and Sam approves it. Acceptance does not cover unexpected settled charges.
