# Support Release Readiness

A local AI assistant for the support lead preparing a product launch. It reads release plans and support preparation records, identifies work that still needs an owner, and revisits that work when the product changes.

This project comes from the release-readiness work I did in B2C support: joining planning and design reviews, feeding customer friction back into the product, coordinating training and content, preparing vendors and operations, watching a rollout and closing customer feedback after fixes.

## What it does

Suppose the product now requires billing confirmation before cancellation completes. Training still says clicking the button completes cancellation, and the vendor launch notice is only a draft. The assistant should identify the incorrect guidance, ask the named owners to revise training and content, and distinguish a draft notice from one agents received.

It also identifies what can remain complete. A changed button label does not automatically create new CRM or telephony work. A deployed fix does not automatically close an affected customer's case.

| Support work | What it reviews |
| --- | --- |
| Planning and design | Open decisions, customer friction and product changes that could prevent contacts |
| Agent enablement | Training revision, completion, roster coverage and access |
| Help and known issues | Public/internal guidance, publication, safe handling, escalation and approvals |
| Vendors and staffing | Vendor readiness, volume/AHT assumptions, reserve and accepted coverage |
| Support operations | CRM reasons/mappings on internal/vendor forms, routing and scoped infrastructure assessments |
| Communications | Current revision/audience, three-day product notice, support/vendor delivery and acknowledgement |
| Launch monitoring | Comparable contact rates, categories, customer reports and supplied pause rules |
| Customer follow-up | Engineering fix, deployment, remedy, customer confirmation and product feedback |

[Scope and company use](docs/SCOPE.md) explains coverage. The first demo is a **fictional B2C cancellation and renewal release**. All people, receipts, metrics, approvals and customer cases are authored examples. Enterprise-specific contracts, administrators and version coverage remain untested.

## Try it

Read the [six saved examples](examples/README.md) first; no account or model call is needed. [Read the skill](skills/support-release-readiness/SKILL.md) for the operating process and [the tools](docs/ARCHITECTURE.md) for how it runs.

Local runs require Python 3.11 or newer and an installed, signed-in Codex CLI. There are no Python packages to install. From the repository folder:

```sh
python3 -m readiness prepare inputs/snapshots/04-late-change.json
python3 -m readiness review inputs/snapshots/04-late-change.json --output evidence/my-review
python3 -m readiness capacity --contacts 60 --aht 10 --reserve-hours 4
python3 -m unittest discover -s tests -v
```

`prepare` validates documents and prints date/rate calculations without a model. `review` writes `report.md` and `report.json`; use a new output folder each time. Capacity gives 600 handling minutes, 10 agent-hours and six hours above the reserve; it predicts neither demand nor waiting time.

The tested account used `gpt-5.6-sol` with high reasoning. Use `--model MODEL_NAME` for an alternative supported by your CLI/account. [Supplying a company release](docs/ARCHITECTURE.md#supply-your-own-release) explains document selection and prior-review history.

**Data handling:** selected documents go to the model service through your Codex login and consume model allowance. Outputs contain document copies and model responses. Check company policy and keep those outputs private before using company material. The demo contains synthetic data only.

## What was learned

A completed comparison used the same model to review six stages twice with this process and twice with a generic checklist: **24 reviews**. Both identified all authored critical and major risks. The specialized version handled phases and unchanged work better, but did not demonstrate better risk detection and omitted one required calculation. It did not meet the declared keep rule.

The publication revision adds clear priority rules and appends the helper's contact comparison directly. The earlier comparison remains a result of its saved version. [Evaluation, original reports and repairs](docs/EVALUATION.md) distinguish software tests, model evaluations and remaining uncertainty.

## Boundaries

This is an on-demand document-review prototype using a local Python command and Codex. It has no shared company app or live Jira, Salesforce, Slack or telephony connection. A support lead reviews proposals and owns approvals and external actions.

Only explicitly selected inputs reach the reviewer. Paths, fingerprints and exact current quotations are checked. Task tools and outside-file access are restricted; unexpected tool events reject a report. Those controls do not prove that every recommendation is correct. [Security and data handling](SECURITY.md) describes the boundary.

One familiar fictional release does not establish reliability on unseen releases, enterprise readiness or fewer customer contacts. This portfolio project demonstrates the support operating process, its implementation and an honest comparison.

Part of [Evidence-first Support](https://github.com/gititya/evidence-first-support).
