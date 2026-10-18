# Support Release Readiness

A product release involves dependencies and decisions from planning through launch. A Project or Program Manager, or someone in Product Operations, usually coordinates that work.

Customer Support has its own set of dependent teams. Depending on the company, these include:

1. **Support Delivery:** agent feedback, process readiness and, in some companies, vendor relationships and delivery.
2. **Support Technical Operations:** telephony, IVR, CRM management and development, and the implementation of support tools.
3. **Support Enablement & Operations:** processes, policies, quality and conversation design for chatbots.
4. **Knowledge Management:** training, knowledge articles for human and AI agents, and public Help Center content.

A Project Manager or Enablement lead may coordinate sign-off before launch. The work also involves managing dependencies across these teams and keeping support preparation aligned with the overall product release.

I wanted to test whether an agent could help a support lead keep track of this work as the product changes. This is a **portfolio proof of work**, built and tested with fictional releases, teams and customer cases.

## What the agent does

Release Readiness works through conversation in **Codex or Claude Code on a Mac**. During setup, it interviews the support lead, learns the company's launch process and saves the context. You can supply team roles, named owners and external vendors.

| Capability | What it handles |
| --- | --- |
| **Onboarding and memory** | Learns the company, launch rules, teams and named leads; remembers them between chats. |
| **Evidence and readiness review** | Reads supplied plans and preparation, identifies gaps, and distinguishes proposals from approved or completed work. |
| **Change assessment** | Identifies which preparation needs revisiting when product behavior changes; retains unaffected work. |
| **Owner and action tracking** | Keeps named owners, statuses, dates, completion evidence and history. Clarifies ambiguous names. |
| **Dates and launch signals** | Calculates announcement deadlines, staffing arithmetic and contact-rate comparisons using supplied data. |
| **Sharing and follow-up** | Creates briefs and CSV trackers, records colleague replies, and tracks defects through customer confirmation. |

For each release, it helps with:

- **Planning:** product decisions, affected customers and friction that could lead to contacts.
- **Preparation:** training, help content, known issues, vendors and staffing.
- **Operations:** CRM categories, routing and support infrastructure.
- **Communications:** product announcements, support notifications, delivery and acknowledgement.
- **Launch and follow-up:** supplied contact volumes, defects, fixes and customer confirmation.

It keeps owner actions, dates, supporting records and history between conversations. You can return and ask, “What work is waiting for Sam?” without explaining the company again.

### Changes to an existing product

For an incremental release, the agent compares the updated product behavior with the preparation already recorded. It identifies work that is incomplete or needs another review, while retaining completed work that the change does not affect.

A drafted announcement has not been delivered. A deployed fix does not confirm that the customer's problem is resolved. These distinctions stay visible in the release record.

## Try it

You need Codex or Claude Code, local file access and permission to use the selected material with your model account. No Python, Node or terminal setup is needed for the support lead.

1. Download and unzip the repository.
2. Open its existing **`agent` folder** as the main local project. In Codex, make it the primary folder; in Claude Desktop, use the Code tab and select it as the main folder.
3. Paste this starter message:

> Start Release Readiness from this folder. Check that AGENTS.md, OPERATIONS.md, REVIEW.md and tools/records.js are present. If any are missing, stop and tell me to choose the existing downloaded folder. Otherwise follow AGENTS.md and set me up.

The agent checks that it loaded, then begins onboarding or finds your saved company context. [START HERE](agent/START%20HERE.md) has the full setup and file-access steps.

Say **Start a release** and provide the product plan, affected customers, proposed launch date and whatever support preparation exists. Incomplete material is fine; missing information stays open.

You can then ask:

> What does support still need before this launch?

> The product plan has changed. Which preparation needs another look?

> Prepare the release brief and action list for the team.

The agent creates a dated brief and CSV tracker. Review and share them through your normal company tools, then bring colleagues' replies back to update the work. One person updates the private working record at a time.

For a look at the fictional release without running a model, read the [saved examples](examples/README.md). The [verification report](docs/AGENT-VERIFICATION.md) records the agent checks and remaining limits; [evaluation](docs/EVALUATION.md) preserves the earlier checklist comparison.

## Boundaries

The agent helps the support lead coordinate preparation and follow-up. The lead owns launch recommendations, approvals and external actions. The agent does not send messages, book staffing, change customer accounts or pause a rollout.

There are no Zendesk or Fin connections, live shared board or background monitoring. Working records stay locally outside the downloaded product folder; selected material goes through the chosen model account. Company use needs approved material and an approved account.

The fictional scenarios demonstrate the support process and its implementation. They do not establish fewer customer contacts or reliability in a real support operation.

Part of [Evidence-first Support](https://github.com/gititya/evidence-first-support).
