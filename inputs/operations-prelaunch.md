# Support operations and delivery update O1

Owners: Alex and Lee. Recorded: 2026-10-12 10:00 UTC. Product reference: v2.

## CRM and infrastructure

New reasons: cancellation_confirmation, renewal_reminder, post_cancel_charge. Map old plan_cancel to cancellation_confirmation and preserve historical records. Internal case form updated in staging; test C-11 passes. The vendor form still lists only plan_cancel and billing_other; no deployment date is recorded.

No new phone number or IVR change is needed. Alex reviewed the unchanged email/chat/phone routing for this cohort and recorded test R-11: vendor billing escalations reach Sam's queue in the staging fixture. This scoped no-change assessment is approved by Alex; CRM form work is separate.

## Contact load and staffing

Baseline: 20 release-related contacts per 2,000 exposed accounts per hour. Planning range for first hour: 30–60; average handling time 10 minutes. At the high end this means 600 handling minutes, or 10 agent-hours. Existing reserve: 4 agent-hours, leaving 6 additional agent-hours needed for that hour before any service-level allowance.

Lee requested 6 additional vendor agents for the first hour. Vendor acknowledgement and a named roster are pending. No queue-wait or service-level forecast has been made. This assumes all reserve time is usable for these contacts.

## Communication

Product announcement ANN-1: draft, based on v2; scheduled for Oct 14, 10:00 UTC. Support notice SUP-1: draft, based on ANN-1; planned for Oct 15. No sent receipt or acknowledgement exists at this as-of time.
