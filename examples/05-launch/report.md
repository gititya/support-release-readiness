# recommend pause

As of 2026-10-20 11:10 UTC, RR-001 is in active rollout for the authorized 2,000-account v3 cohort. Current help, training, public content, billing guidance, CRM operations, vendor coverage and staffing are evidenced, and ANN-4 met the 72-hour rule with 73 hours of lead. The equal one-hour rollout window recorded 26 contacts per 1,000 accounts versus 10 per 1,000 at baseline: a 2.6 ratio and 32-contact increase. This meets the company's pause condition. Two separate customers also reported matching $49 entries after cancellation acknowledgements, although billing has not determined capture status, settled charges or refund entitlement. Recommend that Mira request a pause; only Jo can authorize it and Dev can execute it. None of those pause actions had occurred at the as-of time. Billing review and customer follow-up remain incomplete.

Release: RR-001 · Snapshot: 05-launch · As of: 2026-10-20T11:10:00Z

The review agent proposes actions; it executed none.

Synthetic demo: source receipts, tests, approvals and customer records are authored examples.

Critical means unsafe guidance, serious customer harm or a supplied pause condition. Major means preparation or follow-up work that still needs attention.

## Critical: The first-hour rollout contact rate reached 2.6 times the equal-window baseline, exceeding the pause condition of at least twice baseline. Two separate supplied cases also contain matching reports of a $49 entry after a cancellation acknowledgement. These signals support a conservative pause recommendation but do not prove product causality or that either entry became a settled charge.

Continued new exposure could subject more customers to the conditions producing elevated contacts and reported post-cancellation charge concerns while the cause and billing outcomes remain unresolved.

Owner: Mira, Jo, and Dev. Proposed action: Mira should recommend a pause and prepare the escalation record now. Jo should decide whether to authorize stopping new exposure, and, if authorized, Dev should execute it. Preserve the existing cohort and affected-account records; a pause would not repair accounts already affected.

- `inputs/company-rules.md`: The first hour is limited to 2,000 exposed accounts. Compare contact rates per 1,000 exposed accounts over equal one-hour windows. Recommend a pause if the rate is at least twice the baseline, or if two separate customers have matching reports of an unexpected charge after confirmed cancellation. These are conservative fictional policy thresholds, not proof of statistical significance or causality.

- `inputs/company-rules.md`: The agent can recommend and prepare an escalation draft. It cannot authorize or execute a pause. A pause stops new exposure; it does not roll back a deployed fix or repair already affected accounts.

- `inputs/launch-signals.csv`: 2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,matched_baseline,2000,12,8,0,20

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

- `inputs/launch-customer-cases.json`:     {"id": "C-101", "received_at": "2026-10-20T10:40:00Z", "utterance": "It said my renewal was turned off, but I can see a new $49 charge. Can you check what happened?", "support_record": "Cancellation acknowledgement CAN-101 at 10:15 UTC. Invoice shows a $49 entry at 10:30. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"},

- `inputs/launch-customer-cases.json`:     {"id": "C-102", "received_at": "2026-10-20T10:50:00Z", "utterance": "I turned it off and got the confirmation. Why is there another $49 on my account?", "support_record": "Cancellation acknowledgement CAN-102 at 10:20 UTC. Invoice shows a $49 entry at 10:35. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"}

- `inputs/launch-customer-cases.json`:   "operator_note": "Mira has not recommended a pause yet. Jo has not authorized a pause and Dev has not executed one at this as-of time. All 52 contacts are counted once in the CSV. The two cases are included in its eight post-cancellation-charge contacts."

## Major: Customer follow-up is incomplete. C-101 and C-102 are recorded only as billing review requested, with capture status not yet reviewed. No billing outcome, customer response or confirmed recovery is supplied. The rollout window contains eight post_cancel_charge contacts, but detailed records are supplied for only two of them.

Customers may remain uncertain whether the displayed entries settled, whether cancellation operated correctly and what case-specific billing action, if any, will follow. Other potentially affected customers may not receive tracked follow-up.

Owner: Sam and Mira. Proposed action: Sam should complete case-specific billing review for C-101 and C-102 without promising a refund outcome, and the support owner should deliver and record each result. Mira should reconcile the eight post_cancel_charge contacts, identify any other affected customers, and close each feedback loop only after customer confirmation or record an unresolved customer and named follow-up owner.

- `inputs/company-rules.md`: For a defect, record engineering status, deployment evidence, affected customers and their responses separately. Do not mark customer impact resolved solely because a fix deployed or a ticket was marked duplicate. Mira can close the feedback loop after each affected customer's outcome is confirmed, or explicitly document an unresolved customer and follow-up owner.

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

- `inputs/launch-customer-cases.json`:     {"id": "C-101", "received_at": "2026-10-20T10:40:00Z", "utterance": "It said my renewal was turned off, but I can see a new $49 charge. Can you check what happened?", "support_record": "Cancellation acknowledgement CAN-101 at 10:15 UTC. Invoice shows a $49 entry at 10:30. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"},

- `inputs/launch-customer-cases.json`:     {"id": "C-102", "received_at": "2026-10-20T10:50:00Z", "utterance": "I turned it off and got the confirmation. Why is there another $49 on my account?", "support_record": "Cancellation acknowledgement CAN-102 at 10:20 UTC. Invoice shows a $49 entry at 10:35. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"}

- `inputs/launch-customer-cases.json`:   "operator_note": "Mira has not recommended a pause yet. Jo has not authorized a pause and Dev has not executed one at this as-of time. All 52 contacts are counted once in the CSV. The two cases are included in its eight post-cancellation-charge contacts."

- `inputs/launch-preparation-v3.md`: S3 help and training, approved by Ren and Nia Oct 17, 08:00 UTC: Manage Plan → Cancel subscription → review → Turn off renewal → await billing acknowledgement. Paid access continues to term end. The cohort receives a mandatory billing notice three days before renewal, even with the old reminder toggle off; marketing preferences remain separate. Refunds require Sam's review. Sam approved KB-17's unchanged safe billing-escalation guidance and Jo reaffirmed the limited-cohort acceptance Oct 17.

## Observations

Product v3 is the current approved behavior. It applies to the same limited cohort and replaces v2. The customer-visible flow uses Turn off renewal after review, waits for billing acknowledgement, keeps paid access through term end and sends a mandatory billing notice three days before renewal despite the old reminder toggle.

- `inputs/product-v3.md`: Owner: Jo. Approved: 2026-10-15 17:00 UTC. Applies to the same cohort; replaces v2 before exposure. No customers have been exposed yet.

- `inputs/product-v3.md`: The confirmation button now says Turn off renewal. The review screen and billing acknowledgement requirements remain. Optional seven-day reminders are replaced, for this cohort only, with a mandatory billing notice three days before renewal. Feature Settings' reminder toggle no longer suppresses this billing notice; the screen must explain the exception. Marketing-message preferences remain separate. Paid access and case-by-case refund policy are unchanged.

The current S3 preparation matches v3, retains Sam-approved billing escalation and case-by-case refund review, and replaces S2 for exposure.

- `inputs/launch-preparation-v3.md`: Recorded: 2026-10-20 09:30 UTC. Owners: Jo, Mira, Nia, Ren, Alex and Lee. Current behavior: product v3. Replaces S2 and O2 for exposure.

- `inputs/launch-preparation-v3.md`: S3 help and training, approved by Ren and Nia Oct 17, 08:00 UTC: Manage Plan → Cancel subscription → review → Turn off renewal → await billing acknowledgement. Paid access continues to term end. The cohort receives a mandatory billing notice three days before renewal, even with the old reminder toggle off; marketing preferences remain separate. Refunds require Sam's review. Sam approved KB-17's unchanged safe billing-escalation guidance and Jo reaffirmed the limited-cohort acceptance Oct 17.

Public S3 content was published to the cohort. TR-3 covered all assigned internal and vendor agents, who passed the updated exercise and had access to S3 and KB-17; Lee acknowledged vendor coverage and access.

- `inputs/launch-preparation-v3.md`: PUB-3 Oct 17, 08:30 UTC confirms public S3 content published to the cohort. TR-3 Oct 18 covers all INT-2 and VND-2 agents; all passed the updated button/notice exercise and can open S3 and KB-17. Lee acknowledges vendor coverage and access Oct 18, 11:30 UTC. The S2 content is retained as history and is not used for this cohort.

Alex recorded that the existing CRM reason/form checks and routing still apply because v3 changed no contact reason, field or route. Lee reconfirmed the staffing package, named first-hour roster and 10 agent-hours of reserve plus additional coverage.

- `inputs/launch-preparation-v3.md`: Alex confirmed C-13 reason/form tests and R-11 routing still apply: v3 changes no contact reason, form field or routing. No new telephony work needed. Lee reconfirmed CAP-2 and the same named first-hour staffing roster for Oct 20. Reserve plus additional coverage remains 10 agent-hours; assumptions and queue-wait uncertainty unchanged.

- `inputs/company-rules.md`: CRM contact reasons must be available on internal and vendor case forms, with old reasons mapped to new ones. Staffing requires stated volume assumptions, an AHT assumption (average handling time), reserve coverage and vendor acceptance. A planning estimate is not a demand forecast. If no infrastructure changes are needed, an owner can record a scoped no-change assessment rather than inventing work.

Jo authorized only the 2,000-account exposure and Dev started it at 2026-10-20 10:00 UTC. The evidence does not authorize wider exposure.

- `inputs/launch-preparation-v3.md`: Mira recommended support ready for the 2,000-account rollout Oct 19. Jo authorized that exposure Oct 20, 09:00 UTC, record GO-3. Dev executed exposure start Oct 20, 10:00 UTC, record EXP-3. Do not infer permission to widen beyond this cohort. Jo still owns pause authorization; Dev executes it.

The observed contact increase is a rollout signal, not proof of causality. All 52 contacts were counted once, and the two detailed cases are included within the eight post_cancel_charge contacts rather than added to them.

- `inputs/company-rules.md`: The first hour is limited to 2,000 exposed accounts. Compare contact rates per 1,000 exposed accounts over equal one-hour windows. Recommend a pause if the rate is at least twice the baseline, or if two separate customers have matching reports of an unexpected charge after confirmed cancellation. These are conservative fictional policy thresholds, not proof of statistical significance or causality.

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

- `inputs/launch-customer-cases.json`:   "operator_note": "Mira has not recommended a pause yet. Jo has not authorized a pause and Dev has not executed one at this as-of time. All 52 contacts are counted once in the CSV. The two cases are included in its eight post-cancellation-charge contacts."

The two customer reports establish cancellation acknowledgements followed by visible $49 invoice entries and requested billing reviews. They do not establish settled captures, refund entitlement or confirmed customer recovery.

- `inputs/launch-customer-cases.json`:     {"id": "C-101", "received_at": "2026-10-20T10:40:00Z", "utterance": "It said my renewal was turned off, but I can see a new $49 charge. Can you check what happened?", "support_record": "Cancellation acknowledgement CAN-101 at 10:15 UTC. Invoice shows a $49 entry at 10:30. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"},

- `inputs/launch-customer-cases.json`:     {"id": "C-102", "received_at": "2026-10-20T10:50:00Z", "utterance": "I turned it off and got the confirmation. Why is there another $49 on my account?", "support_record": "Cancellation acknowledgement CAN-102 at 10:20 UTC. Invoice shows a $49 entry at 10:35. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"}

- `inputs/product-v2.md`: On slow responses the invoice page can display a stale renewal date for up to ten minutes after confirmed cancellation. Dev's simulated test T-17 confirms this display issue; it does not establish that a specific customer's charge is valid. Support must confirm the billing cancellation record, explain the display delay and escalate any actual post-cancellation charge to Sam. Refreshing the page is not a guarantee that billing is correct.

At the as-of time, Mira had not recommended a pause, Jo had not authorized one and Dev had not executed one. Recommendation, authorization and execution remain separate authority states.

- `inputs/company-rules.md`: Product lead Jo approves customer behavior. Billing lead Sam approves refund and billing guidance. Engineering lead Dev supplies technical tests and fixes. Support readiness lead Mira recommends support readiness and rollout pauses. Release owner Jo authorizes launches and pauses. Engineering on-call Dev executes rollout changes. Vendor manager Lee confirms staffing and vendor access. Training owner Nia confirms training coverage; content owner Ren owns public and internal help; support operations owner Alex owns CRM and routing.

- `inputs/company-rules.md`: The agent can recommend and prepare an escalation draft. It cannot authorize or execute a pause. A pause stops new exposure; it does not roll back a deployed fix or repair already affected accounts.

- `inputs/launch-customer-cases.json`:   "operator_note": "Mira has not recommended a pause yet. Jo has not authorized a pause and Dev has not executed one at this as-of time. All 52 contacts are counted once in the CSV. The two cases are included in its eight post-cancellation-charge contacts."

## Transitions

RR-001-PRE-001 — resolved: S3 now reflects the v3 button label and mandatory three-day billing notice, and TR-3 covered all assigned internal and vendor agents using the updated exercise.

- `inputs/launch-preparation-v3.md`: S3 help and training, approved by Ren and Nia Oct 17, 08:00 UTC: Manage Plan → Cancel subscription → review → Turn off renewal → await billing acknowledgement. Paid access continues to term end. The cohort receives a mandatory billing notice three days before renewal, even with the old reminder toggle off; marketing preferences remain separate. Refunds require Sam's review. Sam approved KB-17's unchanged safe billing-escalation guidance and Jo reaffirmed the limited-cohort acceptance Oct 17.

- `inputs/launch-preparation-v3.md`: PUB-3 Oct 17, 08:30 UTC confirms public S3 content published to the cohort. TR-3 Oct 18 covers all INT-2 and VND-2 agents; all passed the updated button/notice exercise and can open S3 and KB-17. Lee acknowledges vendor coverage and access Oct 18, 11:30 UTC. The S2 content is retained as history and is not used for this cohort.

RR-001-PRE-002 — resolved: PUB-3 confirms publication of current S3 content to the cohort.

- `inputs/launch-preparation-v3.md`: PUB-3 Oct 17, 08:30 UTC confirms public S3 content published to the cohort. TR-3 Oct 18 covers all INT-2 and VND-2 agents; all passed the updated button/notice exercise and can open S3 and KB-17. Lee acknowledges vendor coverage and access Oct 18, 11:30 UTC. The S2 content is retained as history and is not used for this cohort.

RR-001-PRE-004 — resolved: SUP-4 reached internal and vendor support, Lee acknowledged the revised notice and roster, and TR-3 confirms current training and access.

- `inputs/launch-preparation-v3.md`: Jo moved launch to Oct 20, 10:00 UTC on Oct 15, 18:30 UTC. ANN-4 v3 product announcement sent Oct 17, 09:00 UTC; receipt MAIL-ANN-4 confirms product, engineering and internal support leads. SUP-4 v3 support notice sent Oct 17, 12:00 UTC to internal and vendor support; receipt MAIL-SUP-4 covers both. Vendor lead Lee acknowledged the revised notice and complete roster coverage Oct 18, 11:30 UTC.

- `inputs/launch-preparation-v3.md`: PUB-3 Oct 17, 08:30 UTC confirms public S3 content published to the cohort. TR-3 Oct 18 covers all INT-2 and VND-2 agents; all passed the updated button/notice exercise and can open S3 and KB-17. Lee acknowledges vendor coverage and access Oct 18, 11:30 UTC. The S2 content is retained as history and is not used for this cohort.

RR-001-PRE-006 — resolved: Jo moved the target to 2026-10-20 10:00 UTC and ANN-4 was sent at 2026-10-17 09:00 UTC, providing 73 hours of lead and meeting the 72-hour minimum.

- `inputs/company-rules.md`: Product must send the internal announcement at least 72 hours before launch, naming the behavior revision and audience. Mira adapts it into a support notice. Internal and vendor agents need the current notice, training, internal guidance and access before serving exposed customers. Sending and acknowledgement are distinct. Vendor coverage requires a roster and a named lead's acknowledgement, including acknowledgement of late notice changes.

- `inputs/launch-preparation-v3.md`: Jo moved launch to Oct 20, 10:00 UTC on Oct 15, 18:30 UTC. ANN-4 v3 product announcement sent Oct 17, 09:00 UTC; receipt MAIL-ANN-4 confirms product, engineering and internal support leads. SUP-4 v3 support notice sent Oct 17, 12:00 UTC to internal and vendor support; receipt MAIL-SUP-4 covers both. Vendor lead Lee acknowledged the revised notice and complete roster coverage Oct 18, 11:30 UTC.

RR-001-PRE-003 — resolved: The current record confirms that C-13 form checks and R-11 routing still apply because v3 made no contact-reason, form-field or routing change.

- `inputs/launch-preparation-v3.md`: Alex confirmed C-13 reason/form tests and R-11 routing still apply: v3 changes no contact reason, form field or routing. No new telephony work needed. Lee reconfirmed CAP-2 and the same named first-hour staffing roster for Oct 20. Reserve plus additional coverage remains 10 agent-hours; assumptions and queue-wait uncertainty unchanged.

RR-001-PRE-005 — resolved: Lee reconfirmed CAP-2, the named first-hour roster and 10 agent-hours of reserve plus additional coverage. Queue-wait uncertainty remains but does not undo the accepted staffing record.

- `inputs/launch-preparation-v3.md`: Alex confirmed C-13 reason/form tests and R-11 routing still apply: v3 changes no contact reason, form field or routing. No new telephony work needed. Lee reconfirmed CAP-2 and the same named first-hour staffing roster for Oct 20. Reserve plus additional coverage remains 10 agent-hours; assumptions and queue-wait uncertainty unchanged.

RR-001-PLN-003 — resolved: S3 retains Sam-approved KB-17 safe billing-escalation guidance and Jo's limited-cohort acceptance. The new customer cases require use of that process, not reopening the guidance defect.

- `inputs/launch-preparation-v3.md`: S3 help and training, approved by Ren and Nia Oct 17, 08:00 UTC: Manage Plan → Cancel subscription → review → Turn off renewal → await billing acknowledgement. Paid access continues to term end. The cohort receives a mandatory billing notice three days before renewal, even with the old reminder toggle off; marketing preferences remain separate. Refunds require Sam's review. Sam approved KB-17's unchanged safe billing-escalation guidance and Jo reaffirmed the limited-cohort acceptance Oct 17.

- `inputs/launch-customer-cases.json`:     {"id": "C-101", "received_at": "2026-10-20T10:40:00Z", "utterance": "It said my renewal was turned off, but I can see a new $49 charge. Can you check what happened?", "support_record": "Cancellation acknowledgement CAN-101 at 10:15 UTC. Invoice shows a $49 entry at 10:30. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"},

- `inputs/launch-customer-cases.json`:     {"id": "C-102", "received_at": "2026-10-20T10:50:00Z", "utterance": "I turned it off and got the confirmation. Why is there another $49 on my account?", "support_record": "Cancellation acknowledgement CAN-102 at 10:20 UTC. Invoice shows a $49 entry at 10:35. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"}

## Calculations

Current internal announcement deadline: 2026-10-20 10:00 UTC minus 72 hours = 2026-10-17 10:00 UTC.

- `inputs/company-rules.md`: Product must send the internal announcement at least 72 hours before launch, naming the behavior revision and audience. Mira adapts it into a support notice. Internal and vendor agents need the current notice, training, internal guidance and access before serving exposed customers. Sending and acknowledgement are distinct. Vendor coverage requires a roster and a named lead's acknowledgement, including acknowledgement of late notice changes.

- `inputs/launch-preparation-v3.md`: Jo moved launch to Oct 20, 10:00 UTC on Oct 15, 18:30 UTC. ANN-4 v3 product announcement sent Oct 17, 09:00 UTC; receipt MAIL-ANN-4 confirms product, engineering and internal support leads. SUP-4 v3 support notice sent Oct 17, 12:00 UTC to internal and vendor support; receipt MAIL-SUP-4 covers both. Vendor lead Lee acknowledged the revised notice and complete roster coverage Oct 18, 11:30 UTC.

ANN-4 send lead and lateness: From 2026-10-17 09:00 UTC to 2026-10-20 10:00 UTC = 73 hours of lead. ANN-4 was sent 1 hour before the deadline, with 0 hours of lateness.

- `inputs/company-rules.md`: Product must send the internal announcement at least 72 hours before launch, naming the behavior revision and audience. Mira adapts it into a support notice. Internal and vendor agents need the current notice, training, internal guidance and access before serving exposed customers. Sending and acknowledgement are distinct. Vendor coverage requires a roster and a named lead's acknowledgement, including acknowledgement of late notice changes.

- `inputs/launch-preparation-v3.md`: Jo moved launch to Oct 20, 10:00 UTC on Oct 15, 18:30 UTC. ANN-4 v3 product announcement sent Oct 17, 09:00 UTC; receipt MAIL-ANN-4 confirms product, engineering and internal support leads. SUP-4 v3 support notice sent Oct 17, 12:00 UTC to internal and vendor support; receipt MAIL-SUP-4 covers both. Vendor lead Lee acknowledged the revised notice and complete roster coverage Oct 18, 11:30 UTC.

Support-notice and vendor-acknowledgement lead: SUP-4 was sent 70 hours before exposure. Lee acknowledged the revised notice 46 hours 30 minutes before exposure. The stated 72-hour minimum applies to the product internal announcement, while the support notice and vendor acknowledgement must occur before service.

- `inputs/company-rules.md`: Product must send the internal announcement at least 72 hours before launch, naming the behavior revision and audience. Mira adapts it into a support notice. Internal and vendor agents need the current notice, training, internal guidance and access before serving exposed customers. Sending and acknowledgement are distinct. Vendor coverage requires a roster and a named lead's acknowledgement, including acknowledgement of late notice changes.

- `inputs/launch-preparation-v3.md`: Jo moved launch to Oct 20, 10:00 UTC on Oct 15, 18:30 UTC. ANN-4 v3 product announcement sent Oct 17, 09:00 UTC; receipt MAIL-ANN-4 confirms product, engineering and internal support leads. SUP-4 v3 support notice sent Oct 17, 12:00 UTC to internal and vendor support; receipt MAIL-SUP-4 covers both. Vendor lead Lee acknowledged the revised notice and complete roster coverage Oct 18, 11:30 UTC.

Current staffing coverage and reproducible handling load: Reserve plus additional coverage = 10 agent-hours. The current bundle says CAP-2 assumptions are unchanged but does not restate the contact-volume and AHT quantities, so the handling-load multiplication cannot be independently reproduced from current source passages.

- `inputs/company-rules.md`: CRM contact reasons must be available on internal and vendor case forms, with old reasons mapped to new ones. Staffing requires stated volume assumptions, an AHT assumption (average handling time), reserve coverage and vendor acceptance. A planning estimate is not a demand forecast. If no infrastructure changes are needed, an owner can record a scoped no-change assessment rather than inventing work.

- `inputs/launch-preparation-v3.md`: Alex confirmed C-13 reason/form tests and R-11 routing still apply: v3 changes no contact reason, form field or routing. No new telephony work needed. Lee reconfirmed CAP-2 and the same named first-hour staffing roster for Oct 20. Reserve plus additional coverage remains 10 agent-hours; assumptions and queue-wait uncertainty unchanged.

Equal-window baseline contact rate: 20 contacts ÷ 2,000 exposed accounts × 1,000 = 10 contacts per 1,000 accounts in the one-hour baseline window.

- `inputs/launch-signals.csv`: window_start_utc,window_end_utc,cohort,exposed_accounts,cancellation_confirmation,renewal_reminder,post_cancel_charge,total_release_contacts

- `inputs/launch-signals.csv`: 2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,matched_baseline,2000,12,8,0,20

Equal-window rollout contact rate: 52 contacts ÷ 2,000 exposed accounts × 1,000 = 26 contacts per 1,000 accounts in the first rollout hour.

- `inputs/launch-signals.csv`: window_start_utc,window_end_utc,cohort,exposed_accounts,cancellation_confirmation,renewal_reminder,post_cancel_charge,total_release_contacts

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

Rollout-to-baseline ratio and absolute increase: 26 ÷ 10 = 2.6 times baseline. The absolute increase is 52 − 20 = 32 contacts, or 16 additional contacts per 1,000 accounts.

- `inputs/launch-signals.csv`: 2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,matched_baseline,2000,12,8,0,20

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

Rate-based pause threshold comparison: Twice baseline is 20 contacts per 1,000 accounts, equivalent to 40 contacts among 2,000 accounts. The rollout recorded 52 contacts, exceeding the threshold by 12 contacts and reaching 2.6 times baseline.

- `inputs/company-rules.md`: The first hour is limited to 2,000 exposed accounts. Compare contact rates per 1,000 exposed accounts over equal one-hour windows. Recommend a pause if the rate is at least twice the baseline, or if two separate customers have matching reports of an unexpected charge after confirmed cancellation. These are conservative fictional policy thresholds, not proof of statistical significance or causality.

- `inputs/launch-signals.csv`: 2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,matched_baseline,2000,12,8,0,20

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

Matching unexpected-charge reports: 2 separate supplied customers reported a $49 entry after recorded cancellation acknowledgements, meeting the count-based pause condition. Capture status remains unreviewed, so this does not establish two settled charges.

- `inputs/company-rules.md`: The first hour is limited to 2,000 exposed accounts. Compare contact rates per 1,000 exposed accounts over equal one-hour windows. Recommend a pause if the rate is at least twice the baseline, or if two separate customers have matching reports of an unexpected charge after confirmed cancellation. These are conservative fictional policy thresholds, not proof of statistical significance or causality.

- `inputs/launch-customer-cases.json`:     {"id": "C-101", "received_at": "2026-10-20T10:40:00Z", "utterance": "It said my renewal was turned off, but I can see a new $49 charge. Can you check what happened?", "support_record": "Cancellation acknowledgement CAN-101 at 10:15 UTC. Invoice shows a $49 entry at 10:30. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"},

- `inputs/launch-customer-cases.json`:     {"id": "C-102", "received_at": "2026-10-20T10:50:00Z", "utterance": "I turned it off and got the confirmation. Why is there another $49 on my account?", "support_record": "Cancellation acknowledgement CAN-102 at 10:20 UTC. Invoice shows a $49 entry at 10:35. Capture status not yet reviewed by billing.", "contact_reason": "post_cancel_charge", "status": "billing review requested"}

Tool calculation: contact comparison (inputs/launch-signals.csv): Equal 1-hour windows. Baseline: 20 contacts / 2000 accounts = 10 per 1,000. Current: 52 contacts / 2000 accounts = 26 per 1,000. Current-to-baseline rate ratio: 2.6. Absolute contact increase: 32. These counts do not establish causality or statistical significance.

- `inputs/launch-signals.csv`: window_start_utc,window_end_utc,cohort,exposed_accounts,cancellation_confirmation,renewal_reminder,post_cancel_charge,total_release_contacts

- `inputs/launch-signals.csv`: 2026-10-19T10:00:00Z,2026-10-19T11:00:00Z,matched_baseline,2000,12,8,0,20

- `inputs/launch-signals.csv`: 2026-10-20T10:00:00Z,2026-10-20T11:00:00Z,RR-001,2000,24,20,8,52

## Unknowns

- The cause of the 2.6-times contact-rate increase is not verified.
- Whether either $49 invoice entry became a settled capture is not verified.
- Refund entitlement or any refund decision for C-101 or C-102 is not verified.
- Billing-review outcomes and customer confirmations for C-101 and C-102 are not supplied.
- Detailed records and outcomes for the other six post_cancel_charge contacts are not supplied; the contact category alone does not prove six additional settled charges.
- No engineering defect determination, fix, deployment or customer-confirmed recovery is supplied.
- A pause recommendation, authorization and execution were all still pending at the as-of time.
- Actual queue age, wait time and staffing utilization during the first rollout hour are not supplied.
- Permission to widen exposure beyond the authorized 2,000-account cohort is not supplied.
