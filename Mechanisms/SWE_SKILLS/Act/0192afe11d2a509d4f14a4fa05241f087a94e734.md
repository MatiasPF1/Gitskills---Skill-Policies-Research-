---
name: check-tasks
description: "Discover open tasks assigned to the agent across all projects in the current workspace. Checks GitHub PRs (via gh CLI) and project backlogs for tasks mentioning the agent's name or persona. Notifies the user and asks for direction if nothing is found. Use when the user says 'check your tasks', 'what should I work on', 'check tasks', 'what's next', or similar task-discovery phrases."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [workflow, agent-management, task-tracking, workspace]
---

# /check-tasks — Discover Open Tasks for the Current Agent

## Overview

This skill discovers open tasks assigned to the current agent across all projects in the workspace. It checks GitHub Pull Requests (open, mentioning the agent) and project backlogs. If no tasks are found, it notifies the user and asks for direction.

This skill is **agent-agnostic** — any agent persona can use it: Griffin (senior programmer), Angel (core programmer), Jack (UI developer), Imp (QA/tester), Capy (game designer), Hag (senior game designer), Elk (producer), Fairy (art director), Levi (sound designer), Brute (prototyper), Dino (marketer), Kavu (senior art director).

## When to Use

- User says "check your tasks", "what should I work on", "check tasks", "what's next"
- Agent is idle and needs to discover pending work
- Start of a work session to orient on outstanding items
- User wants a status summary across all projects

## Workflow

### 1. Determine Agent Identity

Extract your agent persona name from your system prompt or identity. This is typically at the start: "You are **X**, a ...". Common examples: Griffin, Angel, Jack, Imp, Capy, Hag, Elk, Fairy, Levi.

Also note any alternate forms of your name that might appear in PR mentions or task assignments (e.g., "@griffin", "Griffin", "[Griffin]").

### 2. Pull Latest Changes

For each project with a git remote, sync with the remote before checking tasks:

```bash
git pull --ff-only
```

Use `--ff-only` to avoid merge conflicts. If the pull fails (no remote connectivity, uncommitted changes, diverged branches), note the failure and proceed with the local state — do not block task discovery on a failed pull.

### 3. Discover Projects in the Workspace

Scan the active workspace directory for projects. A project is a directory that meets at least ONE of:
- Contains a `.git/` directory
- Has an `AGENTS.md` file
- Has a `.agents/` directory

For each discovered project, record:
- Project name (directory name or extracted from remote URL)
- Path to the project root
- Git remote URL (if any) — run `git remote get-url origin` inside the project

### 4. Check GitHub Pull Requests (gh CLI)

For each project that has a git remote:

**Determine if `gh` is available:**
Run `which gh` or use the known path. If `gh` is not installed or not authenticated, skip PR checks for that project (do not fail — report it as "no PR access").

**Fetch open PRs mentioning the agent:**
Run inside the project directory:
```bash
gh pr list --search "mentions:AGENT_NAME state:open" --json number,title,url,createdAt,author --jq '.[] | "#\(.number) \(.title) (by \(.author.login), \(.createdAt))"'
```

If the agent has a one-word name, also try a second search using just the name as a search term (some repos may not use `@mentions`):
```bash
gh pr list --search "AGENT_NAME in:title,body state:open" --json number,title,url,createdAt,author --jq '.[] | "#\(.number) \(.title) (by \(.author.login), \(.createdAt))"'
```

Deduplicate results across both searches.

### 5. Check Project Backlogs (Optional)

If the project follows agentic workflows with `.docs/backlog*.md` files, check the most recent backlog for tasks assigned to the agent persona.

Look for:
- `.docs/backlog.md` (unversioned, current)
- `.docs/backlog-YYYY-MM-DD.md` (most recent dated)

Search for task lines mentioning the agent persona, typically in format:
- `[Persona]` prefix (e.g., `[Angel]`, `[Griffin]`)
- `@Persona` mention within the task description

### 6. Report Findings

Present a structured summary:

```
## Tasks Found for @AgentName

### Project: [project-name]
- GitHub PRs:
  - #123: Title (by author, date) — URL
  - (or "No open PRs found")
- Backlog tasks:
  - Task description (from backlog)
  - (or "No backlog checked" / "No tasks in backlog")

### Project: [another-project]
  ...
```

### 7. When Tasks Are Found — Execute, Don't Ask

When tasks are found that clearly match the agent's known role (e.g., @Griffin reviewing a milestone PR, @Imp writing tests for @Angel's code), **proceed to execute the task immediately**. Do not ask the user "want me to do this?" — the `/check-tasks` invocation is the authorization to discover and act on assigned work. The user is asking "what should I work on" so they can stop managing you.

For PR reviews specifically: **submit the review directly to the PR** using `gh pr review`. Never deliver a review only in chat. The PR is the source of truth. See `references/gh-pr-review-patterns.md` for submission commands and pitfalls.

Context for execution:
- Load any relevant gamedev skills first (e.g., `milestone`, `daily`, prototype review patterns) to understand what the task is about
- Pull the PR diff and any related design documents before reviewing
- Submit via `gh pr review --comment` (or `--approve` if the agent has a distinct GitHub identity from the PR author)

### 8. Handle Empty Results

If **no tasks are found across any project**, respond with:

> "I checked all projects in this workspace and found no open PRs or backlog tasks assigned to me (@AgentName). What would you like me to work on?"

Then offer specific options based on project context:
- "I can review the current milestone and suggest next steps"
- "I can check if there are unassigned tasks I should pick up"
- "I can report on the current project state"

Wait for the user's direction — do NOT invent tasks.

## Common Pitfalls

2. **Wrong agent name.** The agent name in the system prompt may not match the GitHub username. Try both the persona name and variations.
3. **Not discovering all projects.** Don't stop at the first project found. Scan the entire workspace for subdirectories that are projects.
4. **PR search too narrow.** Some projects use `@mention` in body, some in title, some don't use mentions at all. Try multiple search strategies.
5. **Making up tasks when nothing is found.** The skill ends with asking the user, not inventing work. The user decides the next action.

## Verification Checklist

- [ ] Agent persona name identified from identity
- [ ] All projects in workspace discovered
- [ ] `gh` availability checked per project
- [ ] Open PRs searched with both mention and title/body strategies
- [ ] Backlog checked where applicable
- [ ] Results deduplicated and structured
- [ ] Empty-results fallback triggered when appropriate (user notified, options offered)
