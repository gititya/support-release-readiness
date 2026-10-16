# Evaluation: what was tested

Software tests check file handling, arithmetic and failure behavior. Model evaluations check whether recommendations match the support work required by an authored case. Passing software tests does not establish useful recommendations.

Run software checks with `python3 -m unittest discover -s tests -v`. They cover file boundaries, changed fingerprints, quotations, separate histories, calculations, timeouts and unexpected tool events. Publication repairs add cases for omitted telemetry, unequal windows, zero baselines and critical work displayed first. They make no paid model calls.

## Completed comparison

On October 11, 2026, gpt-5.6-sol at high reasoning reviewed six stages twice per version: 24 reviews. The generic checklist and specialized process received the same documents and their own prior history. Only the specialized process received helper outputs. The expected key was withheld. Four separate anonymous calls using the same model scored the outputs; the implementing agent reviewed disagreements against sources.

| Measure | Specialized version | Checklist |
| --- | ---: | ---: |
| Expected critical risks identified | 10/10 | 10/10 |
| Expected major risks identified | 24/24 | 24/24 |
| Expected phases | 12/12 | 11/12 |
| Required calculations reported | 35/36 | 34/36 |
| Required state distinctions | 28/28 | 26/28 |

**Identified correctly** means the report explains the expected gap, customer/operational consequence and supported owner action with current evidence. It does not mean every sentence or priority is correct or a real launch was verified.

Both identified the authored problems. The specialized version avoided some unnecessary preparation work but found no additional risks. It understated some unsafe guidance as major and omitted the 32-contact increase once. The publication revision repairs those weaknesses; it does not rewrite the earlier score.

An earlier run stopped after 13 reviews because copied quotations did not match current sources. Both versions now select passage IDs and the controller inserts exact quotes. All 24 in the completed run passed on their first attempt. Correct quotation cannot prove correct reasoning.

## Unchanged comparison decision rule

For a future comparison, freeze inputs, key, prompts, instructions, code and settings before calls. Use two six-stage sequences per version, at most two structural/citation attempts per review and preserved rejected outputs. A failed slot stays failed while later slots continue. Invalid inputs or changed frozen files stop the run. Grade generated interpretation, not source quotes alone.

- **Keep:** every critical risk in each sequence, at least 90% major-risk recall, all phases, required calculations and state distinctions, no invented completion or unsupported block. Major-risk recall must exceed the checklist by at least ten percentage points in each sequence.
- **Use only sometimes:** safety/phase requirements pass but the recall threshold or improvement margin does not; use reviewed outputs and inspect failures before widening use.
- **Drop:** invented completion/authority, missed critical risk, incorrectly clearing late-change preparation or missing the launch pause recommendation.

The compared version did not pass keep: recall tied and one calculation was omitted. Drop did not trigger. The result supports occasional reviewed use. The publication revision has targeted repair verification, not a new full comparison.

`python3 run_experiment.py --output evidence/my-comparison` runs 24 slots and four scoring passes with at most two concurrent calls. It consumes model allowance. Automatic scores are provisional; inspect sources and distinguish sensible extra questions from mandatory unsupported blocks.

## Evidence and disagreements

[Declaration](comparison-2026-10-11/DECLARATION.md), [automatic score](comparison-2026-10-11/summary.json), [all 24 reports](comparison-2026-10-11/reports/README.md) and [source adjudication](comparison-2026-10-11/adjudication.json) record the results. The report text is unchanged and collected in one file. Full structured responses, frozen code, fingerprints and runtime logs remain preserved in the local archive.

The scorer falsely called a verified manifest timestamp invented; its payload lacked that metadata. Future scoring now receives it, and source review removed the false accusation. It also flagged 26 checklist blocks; source review confirmed six report flags across three reviews. Other test/monitoring/capacity proposals were not established as mandatory blocks. Absence from the expected key alone was not a false alarm. Automatic judgments remain unchanged.

[Repair plan](repair-verification-plan.md) and [repair results](repair-results.md) describe current examples. Expectations precede those model calls. Controller arithmetic is labelled as tool output.

This is a familiar authored B2C development case. The same author wrote sources and expectations; scoring used the same model and source review used the implementing agent. No unseen-release, enterprise, real customer, contact reduction or production-readiness result is established.
