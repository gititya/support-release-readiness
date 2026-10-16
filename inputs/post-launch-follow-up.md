# RR-001 incident and customer follow-up

Recorded: 2026-10-22 11:00 UTC. Owners: Dev, Sam and Mira. Current product: v3.

## Pause, defect and deployment

Mira recommended pause Oct 20, 11:12 UTC. Jo authorized it at 11:15, PAUSE-3. Dev executed it at 11:18, FLAG-3. New exposure stopped at 2,000 accounts; existing exposed accounts remained on v3. The pause did not reverse charges.

Sam's billing review at Oct 20, 13:00 UTC found settled captures for C-101 and C-102 despite confirmed cancellations. Six other post-cancellation-charge contacts were display-only discrepancies, confirmed individually and resolved with KB-17 guidance. Dev identified a cancellation/renewal race condition, BUG-31, distinct from the known display delay KI-17. C-102's linked engineering issue BUG-32 was closed as a duplicate of BUG-31; that closure is not a separate fix or customer resolution.

Fix build 3.1 deployed Oct 21, 09:00 UTC, DEP-31. Test T-31 repeats the timing sequence and confirms no new capture in the simulated regression check. Engineering marks BUG-31 fixed. The rollout remains paused pending Jo's further authorization; deployment is not an approval to resume.

## Affected-customer loop

Sam approved $49 refunds for both affected accounts after reviewing their captures. Ledger records RF-101 and RF-102 show processing completed Oct 21, 10:00 UTC. These records do not prove each customer has seen the returned funds.

Agent Nia contacted C-101 and C-102 Oct 21, 12:00 UTC. C-101 replied Oct 22, 09:00 UTC: “I can see the refund and the account still says renewal is off. That sorts it, thanks.” Support case C-101 closed after this response, and Mira sent the confirmed outcome to Jo and Dev at 09:30 UTC, FEED-101.

C-102 has not replied. Support case C-102 remains open. Nia owns another follow-up on Oct 23 at 12:00 UTC. Mira's product/engineering update FEED-102 at Oct 22, 10:00 UTC says the fix deployed and refund processed, but customer confirmation is outstanding. Do not call both customers resolved.
