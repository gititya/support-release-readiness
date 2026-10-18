# Work with Release Readiness

Release Readiness works with you from product planning through launch and customer follow-up. It remembers your support operation, reviews the material you provide, keeps track of owners and open work, and prepares updates for the release team. Use it in a local Mac session in Codex or Claude Desktop's Code tab. No Python, Node, terminal commands or separate API key are needed.

## Set it up once

1. Download and unzip the product. If you downloaded the GitHub repository, use the `agent` folder inside it. The separate product ZIP contains a folder called **Release Readiness**. Keep its files together in a local folder you can find again.
2. Check the folder in Finder. It must contain **START HERE.md**, **AGENTS.md**, **CLAUDE.md**, **OPERATIONS.md**, **REVIEW.md** and **tools**. Select this existing folder in the app. Creating a new project with the same name does not copy these files into it; a link to a folder in a chat is not an installation.
3. In Codex, attach that existing folder to a local project and make it the **primary** folder before starting a new chat. In the project menu, use **Edit project → Add folder**, then **Make primary** if another folder is primary. Open a new chat in that project. These steps follow the [official OpenAI documentation](https://learn.chatgpt.com/docs/projects). In Claude Desktop, use the **Code** tab, click the current folder name beside **Local**, choose **Open folder…**, and select the product folder before the first message. **Add another folder** only grants extra access; it does not select the main project.
4. Send the starter message below. The agent checks its files and records helper, then says **Release Readiness loaded** before asking about your company or continuing saved work. If it cannot do that, fix the selected folder before providing company material. A blocked helper needs the app's normal permission or help from your company; the agent will not install a replacement or change security settings.

Copy this as your first message. It also catches an empty-folder start:

> Start Release Readiness from this folder. Check that AGENTS.md, OPERATIONS.md, REVIEW.md and tools/records.js are present. If any are missing, stop and tell me to choose the existing downloaded folder. Otherwise follow AGENTS.md and set me up.

The agent asks about your company, support model, timezone, teams, vendors, launch authority and notice rules. Supply what you know; it asks about the rest one question at a time. For example: “Sam owns training; Ren owns help content; Jo authorizes launch. Product announcements need to arrive three days before launch.” It checks what three days means and saves the context after your confirmation. You can later refer to Sam by name or as the training lead. If two people share a name, it asks which one you mean.

Use a company-approved model account and approved material. The selected material goes through that account. Private working records stay outside this download in your local Application Support folder. Your app may request ordinary folder and helper access. Confirm any custom location with the agent; you must provide that location again in a new chat if it is outside the default company folder.

## Work on a release

1. Say **Start a release**. Provide the product plan, who is affected, the proposed launch date and what phase you are in. Add design or planning notes, known issues and any decisions already made. You can start with incomplete material; missing information stays open.
2. Add the preparation you have: training and vendor coverage, public or internal help articles, staffing assumptions, CRM categories and routing changes, support infrastructure, and draft or delivered launch communications. Tell it who owns each area. Text files, CSV and pasted updates work directly; other attachments depend on what your app can read. It asks for a readable extract when needed.
3. Ask **What does support still need before this launch?** It explains gaps, their effect on customers and agents, named owner actions and dates. It distinguishes planning work from final launch preparation. A drafted notice is not a delivered notice, and a colleague's completion report is not verified completion.
4. Return in a new chat in the same project and say **Continue [release name]. What work is waiting for [person]?** Give it changed product plans or colleague replies. It keeps the history, revisits affected work and retains unrelated completed preparation. After launch, provide contact volumes, exposed-user counts, defects, fixes and customer follow-up; it reviews those supplied records when you ask.

## Share the work

Ask **Prepare the release brief and action list for the team**. The agent creates a dated brief and CSV tracker with named owners, stable action IDs and current statuses. Open and review them before sharing through your normal company tools. Source documents and quotes are omitted by default; names and descriptions may still be sensitive. Nothing is sent for you. Ask colleagues to reply with the action ID, update, supporting record and the person accepting the work, then bring that reply back to the agent.

In Claude, previewing these files also needs the company's share folder attached to the current session. The agent gives its path. Use **+ → Add folder**, press **Command-Shift-G** in the Mac picker, paste that path and select it. Send the attachment with your next message. Keep the product folder as the main project. A new chat may need this preview access again even though company context resumes automatically. Ask to see the brief in the conversation if preview is unavailable.

Only one person updates the private working record at a time. Colleagues receive the exported brief and tracker; they do not share a live board. Active records stay local. To update the agent, close the old session, replace this downloaded product folder and keep the separate private working folder. Start a new chat from the updated product and say **Continue my release**.

## What to expect

The agent supports planning, training, help content, vendors, staffing, CRM and routing, launch communications, known issues, supplied launch signals and customer follow-up. It keeps separate releases and named team responsibilities. You still own launch decisions and coordination. It does not send messages, change customer accounts, book staffing, pause a rollout, connect to helpdesks or monitor between conversations.

Claude desktop setup, return and share-file opening, plus a user-operated Codex return, have been checked on one Mac. The empty-folder Codex attempt failed before an explicit recovery loaded the product; the setup steps above address that failure. Other permission modes, managed work laptops, download quarantine and independent first use remain acceptance work. The [verification report in the repository](https://github.com/gititya/support-release-readiness/blob/main/docs/AGENT-VERIFICATION.md) separates those results. This build supports a supervised pilot; those unperformed checks prevent a general production-readiness claim.
