# What I checked

This is the continuing Release Readiness agent, defined in [the PRD](AGENT-PRD.md). It keeps company context, release evidence, owner actions and history between conversations. Open [the agent folder](../agent/START%20HERE.md) to use it. The earlier checklist comparison has not been rerun or rescored.

The implementation is built. Claude's main desktop flow has now been exercised on one Mac, including fresh-chat return and opening the share files. Codex desktop and an unfamiliar support-lead trial remain unverified. These results support a supervised pilot, not a claim that every work laptop is ready to use it.

## Software checks

All 78 offline tests pass on the developer Mac: the original 42 checks, 34 native helper checks and two packaging checks. The added name-directory check covers saved responsibilities, named ownership in the CSV and role corrections. The native checks exercise the actual built-in macOS helper, not a Python replacement. They cover separate release records, source versions and exact passages, completion evidence, affected-work reopening, dates and rates, concurrent saves, interrupted writes, damaged records, preserved manual edits and package replacement. [The October 16 GitHub run](https://github.com/gititya/support-release-readiness/actions/runs/38930234199) ran the earlier 77 successfully; Linux explicitly skipped its 33 native checks.

The rate fixture gives 10 contacts per 1,000 before launch and 26 after launch: a 2.6 ratio, 16 more contacts per 1,000 and 32 more contacts. Date cases distinguish elapsed hours from local calendar/business days, including daylight-saving changes and supplied holidays. Independent standard-library results check the native date and SHA-256 calculations.

The download has one shared agent definition, a Claude import, start instructions, two agent references and the native helper. It contains no company records, test answers, Python runner or developer environment. The root README remains unchanged.

## Model sessions

Each exercise starts a new conversation with a frozen product copy and a private synthetic workspace. The model receives the selected release documents, never the evaluator key. Saved records provide continuity. These are CLI-hosted checks of agent behavior; they do not establish the desktop app's permission experience.

| Case | Observed result |
| --- | --- |
| Planning | Saves company context and asks for unresolved product decisions; final training and staffing remain future preparation |
| Prelaunch | Finds stale guidance, incomplete preparation and missing evidence |
| Corrected preparation | Recommends support ready for the specified cohort while keeping Jo's launch decision separate |
| Late product change | Reopens affected training, guidance and notices; retains accepted CRM, routing and staffing |
| Rollout | Both hosts save a pause recommendation with the exact contact comparison and matching customer reports; human authorization and execution remain separate |
| Customer follow-up | Keeps C-102 open despite a processed refund, because customer confirmation is missing |
| Separate enterprise release | Saves a second release and raises administrator notice, entitlement and tenant rollout questions; this is only a planning check |
| Sharing and reply | Writes a dated brief and CSV action list; records Nia's reply without calling the customer resolved or sending anything |
| Unapproved instructions in a document | Both hosts retain the open case and paused state rather than accepting the attachment as approval |

Codex CLI 0.162.1 used gpt-5.6-sol with high reasoning. Claude Code 2.1.301 used claude-opus-5-5. A run finishing successfully means its saved output can be assessed; it does not prove every recommendation is useful.

Codex completed all ten steps in its lifecycle exercise. Claude completed the first five, failed its original rollout slot, then completed the five remaining steps in the separate recovery run. The lifecycle runs used earlier candidate packages; later changes received the targeted checks below, rather than a new full ten-step replay of the final ZIP.

In the October 16 package, each host also continued the other host's follow-up records in a new conversation. Both preserved C-101's confirmed recovery, kept C-102 unresolved and retained Jo's resume authority. Codex preserved the supported six-case group outcome; Claude closed the earlier unnecessary request for separate case records, keeping its history. The original imported release documents match the fixture text by SHA-256. The implementing agent checked saved outputs against the sources; this is not independent support-lead acceptance.

## Desktop and named-lead checks, October 17

These checks used fictional Cedar Support Demo in Claude Desktop's Code tab, Local, Opus 5.5, Medium, with the existing Auto permission mode. The author operated the app; no independent support lead participated. No new OS/helper permission prompt appeared during the tested operations, so this does not establish prompt counts in other permission modes.

The first attempt attached the product as an extra folder while the main folder remained elsewhere. “Set me up” started generic setup. Selecting the product as the main folder before the first message fixed it. The start guide now gives the actual folder-selector steps.

The agent saved the company and a planning release with Sam's training review, Ren's content review and Alex's operations assessment. A fresh chat from an updated product folder recovered the saved company and release, identified Sam and Ren by name without repeating onboarding, and generated a brief and CSV. The private records stayed outside the replaced product folder.

The directory was then clarified to Sam Patel in training and Sam Lee in Product Operations. Both the actual Claude app and a fresh Codex CLI check asked which Sam should get a new launch-notes action. Neither guessed. After explicit selection, each saved the new open action under Sam Patel and kept the earlier work open. Earlier first-name records remain in history. The Codex check used a separate copy of the desktop-created synthetic state; it is not a Codex desktop pass.

The share-file check found two problems: Claude's preview treated angle brackets in Markdown targets as literal filename characters, and it could not preview the external private folder until that folder was attached to the session. Corrected plain-path links plus a scoped attachment of the company's shared folder opened both the Markdown brief and the CSV table inside Claude. The guide explains that attachment, keeps the agent as the main folder and offers an inline brief if preview is unavailable. It may be needed again in a new chat. The native helper and state schema are unchanged in version 0.2.1.

A fresh Claude CLI conversation with the final package then used the returned absolute paths without angle brackets and supplied the scoped folder-attachment fallback. It retained all four open actions and the named owners. That checks the revised instructions; the actual preview-opening evidence comes from the desktop session above, where the author supplied the repair steps. This is not an independent first-use test of the final guide.

The product also now explicitly keeps unanswered phone/routing scope unknown. The initial onboarding response had assumed no phone change, although its saved profile correctly marked the question unknown. The release and later responses retained Alex's required scoped assessment.

The Mac locked partway through testing. Work paused until the owner unlocked it manually; no unlocking or security bypass was attempted. The computer-control tool separately refused access to Codex itself. That desktop check remains blocked.

## Failures and repairs

The first Codex harness omitted access needed by the system JavaScript interpreter. The agent reported that it could not save; the harness was corrected without installing a runtime or changing machine permissions.

Claude's original rollout turn hit the fixed ten-minute limit before saving its review. Its accepted records and requests survived. The original harness failed to save the timed-out process's partial transcript; that evidence gap is retained and the harness now captures partial output and saved records on timeout. The revised agent saves an urgent rollout recommendation before reconciling earlier preparation, returns only the latest review by default and updates actions without repeating every field. The recovery run is recorded separately from the failed original slot.

An early report described already resolved problems as serious findings despite recommending ready. Findings now mean unresolved work; resolved preparation and pending launch authority go into observations. A ready recommendation cannot retain an unresolved critical or major finding.

Codex also requested separate case records for an unnamed group already described as individually confirmed and resolved. The review policy now preserves that supported group outcome. It continues to track the explicitly unconfirmed named customer. Repair results are recorded separately; the original output stays unchanged.

The first cross-host harness passed a symlink instead of the real workspace path. Both hosts/helper refused it. The corrected harness uses the actual path, including spaces; the original failure is preserved.

Both corrected cross-host turns resumed the other host's prelaunch records, imported Lee's original inbox file directly, saved a current ready-for-support review with no unresolved serious findings, and generated the brief and CSV. Jo's launch authority remained separate. Those turns preceded the final follow-up-policy and workspace-path fixes; final-package follow-up continuation is checked separately.

Opus 5.5 reviewed the PRD and implementation. Its storage findings led to fixes for update-safe workspace location, interrupted saves, stale acceptance, lock recovery, company discovery and preserving manual edits. A review is supporting evidence, not a substitute for running the checks.

The final targeted Opus 5.5 verdict was **Proceed**. It found a nonblocking workspace-path gap for unusual helper invocations and case aliases. The failing reproduction is preserved; the helper now resolves the real script location and existing workspace ancestor before comparing paths, and stops if it cannot identify the product. The expanded native check rejects absolute, tools-relative, case-alias and linked-helper paths into the replaceable download. A first repair exposed macOS's different path normalization for existing versus nonexistent files; that failed run is preserved too.

## Acceptance still needed

- A01, A09 and A18: complete the Codex desktop check and check browser-download quarantine and permission modes beyond the existing Claude Auto session. Claude's main-folder setup, fresh-chat resume, product-folder update and file opening have the bounded evidence above.
- A04 and A15: check unreadable attachments and blocked permissions through those actual apps. Text intake, quote rejection and unavailable-helper behavior already have software or CLI evidence.
- A11, A19 and A20: an unfamiliar support lead completes onboarding, review, return, named-lead work and sharing without developer help, then judges the usefulness on an unfamiliar release. Actual Claude file opening and name clarification were author-operated checks.

No connector, background monitor, shared live database or automatic launch/customer action is included. The active workspace has one writer. Process-interruption checks do not establish power-loss durability. Instructions and quotation checks cannot prove that a passage supports the model's interpretation.
