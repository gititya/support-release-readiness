# Coverage and company use

The assistant reviews preparation for a specific release and time. It returns a readiness recommendation, customer consequences, evidence, proposed owner actions, resolved/reopened findings and unknowns.

| Area | Input examples | Review question |
| --- | --- | --- |
| Planning/design | Grooming notes, product decisions | What is undecided? Can the experience prevent support contacts? |
| Customer friction | Supplied support themes or ticket findings | What should product, engineering or design address? Is the evidence measured or illustrative? |
| Training | Revision, lessons, attendance and exercises | Are agents learning the current flow? Is training complete? |
| Public help | Draft/published revisions and audience | Can exposed customers reach accurate help? |
| Internal help/known issues | Safe handling, workarounds, approvals, escalation | Can agents handle known issues without unsafe promises? |
| Vendors | Roster, current guidance access, lead acknowledgement | Can assigned vendor agents serve this release? |
| Staffing | Contact range, average handling time, reserve, accepted coverage | What handling load follows from the assumptions? Is coverage committed? |
| CRM | Reasons, mappings, form deployment and tests | Can internal/vendor agents categorize contacts consistently? |
| Infrastructure | Routing/telephony tests or a scoped no-change assessment | Does this release need technical support changes? |
| Notices | Revision, recipients, receipts, acknowledgement | Is the notice timely and current? Did support/vendors receive it? |
| Rollout | Equal-window contacts, exposed accounts, categories, reports | Does the supplied pause rule require escalation? Who recommends, authorizes and executes? |
| Follow-up | Defect, deployment, remedy, customer reply, feedback | Is the customer recovered, or only the engineering issue fixed? |

The company policy supplies the rules. The demo requires a product announcement at least 72 hours before launch: three calendar days, not a universal industry standard. Missing material is an unknown or an unmet requirement, not proof of customer harm.

## Would a company build it this way?

A local command and skill are a reasonable prototype for one person's document-review workflow. OpenAI supports repository-scoped skills for teams and separate application runtimes for custom tools, storage and approvals. These establish available approaches, not what most companies choose. [Skills](https://learn.chatgpt.com/docs/build-skills), [agent runtime options](https://developers.openai.com/api/docs/guides/agents).

This choice keeps the first question small: does connecting release evidence produce useful support work? A company could use approved documents and an approved model account. A shared service would need a chosen interface, user identity, document permissions, retention, audit history and approved system connections. Those capabilities are future work. An AI recommendation does not approve a launch or customer action.

## B2C and enterprise

The software accepts company rules and release evidence. The tested case is B2C. Enterprise tests would need contracts, entitlements, administrators, supported versions, account/cohort scope and customer-specific notice obligations. This repository does not claim those cases have been tested.
