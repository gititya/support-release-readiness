
Every release cycle for a product has a well defined process through the entire SDLC, identifying dependencies, blockers for the release that are likely being done by a Project/Program Manager or someone from Product Operations. 

The Customer Support functional carries its own unique set of dependent teams as well; it involves engaging: 
1. The Support Delivery team - This might be the core team that is responsible for managing human support agents' feedback, process readiness. Sometimes, this is also the team that manages relationships & delivery from Support vendors
2. Support Technical Operations - The team that is typically responsible for the technical infrastructure & implementation of tools: Telephony, IVR, CRM management & development. 
3. Support Enablement & Operations - Usually the team that defines and manages processes, policies, Quality, conversation design (for chatbots)
4. The Knowledge Management teams - Training, Help Center articles - to ensure that the support reps are trained, knowledge articles for AI agents, human reps and Help center articles. 

While there could be a Project Manager (or sometimes the Enablement lead) who handles coordination & signoff before a product launch, the actual work is managing these dependencies + ensuring that the support team itself is dependent and stays compliant to Product Operations.

I wanted to test whether an agent could help a support lead keep track of this work as the product changes; this is built & tested with fictional releases, teams & customer cases. 

## What the agent does
Release Readiness works through conversation in **Codex or Claude Code on a Mac**. Once you begin setup, it interviews the support lead, learns the company’s launch process and saves the context. You can also add in owner roles/names and external vendors. 

Below are the capabilities of the agent: 

| Capability                        | What it handles                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Onboarding and memory**         | Learns the company, launch rules, teams and named leads; remembers them between chats.                              |
| **Evidence and readiness review** | Reads supplied plans and preparation, identifies gaps, and distinguishes proposals from approved or completed work. |
| **Change assessment**             | Identifies which preparation needs revisiting when product behavior changes; retains unaffected work.               |
| **Owner and action tracking**     | Keeps named owners, statuses, dates, completion evidence and history. Clarifies ambiguous names.                    |
| **Dates and launch signals**      | Calculates announcement deadlines, staffing arithmetic and contact-rate comparisons using supplied data.            |
| **Sharing and follow-up**         | Creates briefs and CSV trackers, records colleague replies, and tracks defects through customer confirmation.       |
Training, content, staffing and CRM are **areas the agent reviews**, rather than separate installed skills.

For each release, it helps with:
- **Planning:** product decisions, affected customers and friction that could lead to contacts.
- **Preparation:** training, help content, known issues, vendors and staffing.
- **Operations:** CRM categories, routing and support infrastructure.
- **Communications:** product announcements, support notifications, delivery and acknowledgement.
- **Launch and follow-up:** supplied contact volumes, defects, fixes and customer confirmation.

It keeps owner actions, dates, supporting records and history between conversations. You can return and ask, “What work is waiting for Sam?” without explaining the company again.



### Existing product release. 
When you're running this agent for an incremental change to an existing product, the agent can also: 
1. Identify areas that were delivered by a dependant support team but could be incomplete. 
2. It can also recognoize what is yet to be completed: a drafted announcement that isn't delivered, a deployed fix that doesnt confirm that the customer's problem is resolved. 


## Try it

You need Codex or Claude Code, local file access and permission to use the selected material with your model account. 

1. Download and unzip the repository.
2. Open its existing **`agent` folder** as the main local project.
3. Follow [START HERE](agent/START HERE.md) and send its starter message.

The agent checks that it loaded, then begins onboarding or finds your saved company context.
[Ideally, this section should be: Give this prompt to claude code/codex] 

Say **Start a release** and provide the product plan, affected customers, proposed launch date and whatever support preparation exists. Incomplete material is fine; missing information stays open.

You can then ask:

> What does support still need before this launch?

> The product plan has changed. Which preparation needs another look?

> Prepare the release brief and action list for the team.

The agent creates: 
1. A dated brief and CSV tracker. 
2. Review and share them through your normal company tools 
3. then bring colleagues’ replies back to update the work

## Boundaries

This isn't a connector into Zendesk or Fin (yet); think of it as the Chief of Staff for Customer Support! 


