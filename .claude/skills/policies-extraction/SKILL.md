---
name: policies-extraction
description: Extracts the human-control rules written in agent skill files (autonomy limits, clarification rules, approval gates, validation, escalation) into one numbered JSON file per skill, read from a working folder the user gives and sorted into one `JSONS/` folder per software engineering topic, with its source (repo, path, author, mechanism) and, per category and overall, a fixed-format quantitative conclusion plus a plain-language qualitative one. Use when asked to extract, code or annotate policies from SKILL.md files.
---

# Policies extraction

Research question: How do developers specify autonomy limits, clarification rules, approval gates, validation, and escalation in agent skills?

The output is research data, compared across runs and against human coders. Ground rules:
- The same file must always give the same output.
- Apply the rules literally, from the words on the page only.
- No inference, no outside knowledge.
- If a statement does not clearly pass a test, leave it out.
- Only `conclusion_qualitative` is free wording. Everything else must be identical across runs. 
- Compare the output to the source files to check for errors after JSON is generated. If you find any, fix them, tell human and re-run.

## Input

Expect the user to give a working folder:

- It holds the skill files to process (every `.md` inside, including subfolders).
- The JSON output goes to `JSONS/` at the repo root (see Output).
- If no folder is given, ask the user for one before doing anything.

What to read:

- Files under `Mechanisms/Mechanisms_<mechanism>/Found/<file_sha>.md` have an `index.json` next to them with their source fields.
- If a file cannot be read, stop and tell the user.

## Procedure

Go through each file from first line to last:

1. Split it into statements: one sentence, list item, table row, or heading. Skip fenced code blocks.
2. Keep only statements that instruct the agent. Skip:
   - descriptions of what the skill does
   - output examples
   - instructions aimed at the human
3. Assign each kept statement to at most one category (tests below) and fill its fields.
4. Keep at most the first 10 per category, in document order.
5. Detect the SWE topics (see Topics below).

Front matter:

- Only `allowed-tools` (or `tools`) counts, as one `autonomy_limits` statement.
- Skip every other front matter line.

## Categories

Apply the tests in order. The first one that passes wins. If none passes, the statement is not extracted.

| Order | Category | Passes if the statement |
| --- | --- | --- |
| 1 | `escalation` | names something going wrong (failure, error, conflict, blocked/stuck, unexpected result, repeated failed attempts) and says to stop, abort, undo, roll back, or report to the human |
| 2 | `approval_gates` | requires a human's permission, confirmation, approval or sign-off before an action, or forbids the action without one |
| 3 | `clarification_rules` | says to ask the human for information, or forbids guessing/assuming when information is missing or ambiguous |
| 4 | `validation` | says to check work or a result (tests, lint, build, typecheck, verify, review, show evidence), or sets a done condition |
| 5 | `autonomy_limits` | forbids or restricts an action on the environment (files, repos, commands, tools, external systems, data), or says to proceed without asking |

Boundary rules:

- Missing or ambiguous info → `clarification_rules`, not escalation.
- Asking for info → `clarification_rules`. Asking for permission → `approval_gates`.
- Rules about the content or style of the output are not autonomy limits:
  - "Never push to main" → passes
  - "Never use inline styles" → does not

Examples:

- "If the migration fails, stop and report the error" → `escalation`
- "Wait for explicit approval before `git push --force`" → `approval_gates`
- "If the branch is unclear, ask the user" → `clarification_rules`
- "Run the tests before marking complete" → `validation`
- "Never modify files outside `src/`" → `autonomy_limits`
- "Use descriptive variable names" → not extracted

## Fields

Each extracted statement has four fields.

**`quote`**:

- The exact text, without list or heading markers.
- Cut to the first 200 characters.

**`strength`** (whole words, case-insensitive, checked in this order):

1. `"mandatory"` if it has: must, never, always, do not, don't, cannot, can't, required, mandatory, shall, only
2. else `"advisory"` if it has: should, prefer, consider, try, may, might, could, recommended, ideally, optional, optionally, if possible, where possible, when appropriate

**`conditional`** (whole words, case-insensitive):

- `true` if it has: if, when, whenever, unless, until, in case
- else `false`


## Topics

Records which software engineering topics the skill touches, and in which categories its rules mention them.

How to match a keyword:

- Whole words or phrases, case-insensitive.
- A keyword ending in `*` matches any word that starts with it (`deploy*` → deploy, deployed, deployment).
- A keyword can match more than one topic (e.g. "unit tests" hits both Unit Test and Testing).

When a topic counts as found:

- Any of its keywords appears in the front matter `name` or `description`, or anywhere in the body outside fenced code blocks.

What to record for each found topic:

- `topic`: the topic name, exactly as in the table.
- `categories`: every category with at least one extracted statement whose `quote` contains a keyword of that topic.
  - Use the order autonomy_limits, clarification_rules, approval_gates, validation, escalation.
  - Use `[]` when the topic is found but no extracted statement mentions it.

Output rules:

- List the found topics in table order.
- If no topic is found, write `"topics": []`.
- Topics do not change any conclusion.

| Topic | Keywords |
| --- | --- |
| CI/CD | CI/CD, GitHub Actions |
| Deployment | deploy\* |
| Database Migrations | migrat\* |
| Infrastructure as Code | infrastructure as code, terraform |
| Cloud | AWS, Kubernetes, Docker |
| Security | security, vulnerab\* |
| Secrets Management | secret\*, credential\* |
| Git Workflow | git, pull request\* |
| Production Data | production |
| Privacy | privacy, PII |
| Legacy Code | legacy |
| Refactoring | refactor\* |
| Dependency Management | dependenc\* |
| API Design | API |
| Microservices | microservice\* |
| Event Driven | event-driven, event driven |
| Distributed Systems | distributed |
| Debugging | debug\* |
| Incident Response | incident\* |
| Scalability | scalab\* |
| Performance Optimization | performance |
| Unit Test | unit test\* |
| Testing | test\* |
| Documentation | documentation, README\* |
| Frontend | frontend |
| Code Review | code review\* |

## Output

Where and how to write:

- Write into `JSONS/` at the repo root. It already holds one subfolder per SWE topic plus `No-Topic/`, each with a `.gitkeep`.
- Topic folder names are the topic with every character other than letters, digits, `.`, `_`, `-` replaced by `-` (`CI/CD` → `CI-CD`, `Database Migrations` → `Database-Migrations`).
- A skill with no topics goes into `No-Topic/`.
- Never delete the `.gitkeep` files. If a topic folder is missing, create it.
- Skip the `JSONS/` folder when reading input.
- No combined file, no extra keys.
- When done, reply with only:
  - the output folder
  - the number of skill files processed
  - the number of JSON files in each topic folder

One skill can belong to several topic folders:

- Copy its JSON into the folder of every topic in its `topics` list. Just do it, without asking.
- The copies are the same file: same name, same content, byte for byte.
- Example: a skill that talks about git and Docker matches Git Workflow and Cloud, so the same `1_example-skill.json` goes into both `Git-Workflow/` and `Cloud/`.

Example layout:

```
JSONS/
  Git-Workflow/
    1_example-skill.json
    4_release-helper.json
  Cloud/
    1_example-skill.json
  No-Topic/
    2_writing-style.json
```

File names:

- Number the skill files from 1, by path, sorted alphabetically, across the whole working folder. A skill keeps the same number in every topic folder.
- Name each one `<number>_<name>.json`.
- `<name>` is the front matter `name`, or else the file name without its extension.
- Replace every character other than letters, digits, `.`, `_`, `-` with `-`.

Keys, in this order:

```json
{
  "name": "example-skill",
  "mechanism": "Escalate",
  "repo": "example-org/example-repo",
  "path": ".claude/skills/example-skill/SKILL.md",
  "author": { "owner": "example-org", "commit_author": "d0836709438c41b8", "declared": null },
  "file": "Mechanisms/Mechanisms_Escalate/Found/0090752c3455438f9e0e0cc7673bd495cd40ecd2.md",
  "topics": [
    { "topic": "Git Workflow", "categories": ["autonomy_limits", "approval_gates"] },
    { "topic": "Cloud", "categories": [] }
  ],
  "conclusion_quantitative": "example-skill (Escalate) specifies 2 of 5 categories: 1 autonomy limit, 1 approval gate; none for clarification rules, validation rules, escalation rules. Strongest: autonomy limits.",
  "conclusion_qualitative": "example-skill helps the agent prepare and publish code changes. It forbids pushing straight to the main branch and makes the agent get the user's approval before a force-push, which overwrites history. It never tells the agent to ask for missing information, check its work, or what to do when something fails.",
  "autonomy_limits": {
    "conclusion_quantitative": "1 autonomy limit (1 mandatory, 0 advisory; 0 conditional), mostly list.",
    "conclusion_qualitative": "There is one strict rule (worded with \"never\"), it applies at all times, and it is a bullet point. It forbids pushing directly to the main branch (`main` or `master`).",
    "statements": [
      { "quote": "Never push to `main` or `master`.", "strength": "mandatory", "conditional": false, "form": "list" }
    ]
  },
  "clarification_rules": { "conclusion_quantitative": "No clarification rules found.", "conclusion_qualitative": "...", "statements": [] },
  "approval_gates": { "...": "same shape as autonomy_limits" },
  "validation": { "...": "same shape" },
  "escalation": { "...": "same shape" }
}
```

### Source fields

General rules:

- Copy every value exactly.
- Use `null` for anything missing. Never fill it from elsewhere.
- The `index.json` entry to use is the one whose `file_sha` matches the file name.

Where each field comes from:

- `name`: front matter `name`
- `mechanism`: the part after `Mechanisms_` in the parent folder (`Act`, `Ask`, `Escalate`)
- `repo`, `path`, `author.owner`, `author.commit_author`: the `index.json` entry
- `author.declared`: front matter `author` (top level or under `metadata`)
- `file`: path relative to the repo root, with forward slashes

### Category conclusions

**`conclusion_quantitative`** uses one of two formats:

- Empty: `No <plural label> found.`
- Otherwise: `<count> <label> (<m> mandatory, <a> advisory; <c> conditional), mostly <form>.`

The parts:

- `<label>`: `autonomy limit`, `clarification rule`, `approval gate`, `validation rule`, `escalation rule`. Add `s` when the count is not 1.
- `<count>`: the number of statements, or `10+` at the limit.
- `<m>`, `<a>`, `<c>`: how many are mandatory, advisory, and conditional `true`.
- `<form>`: the most frequent form. On a tie, the first of frontmatter, heading, list, table, prose.

**`conclusion_qualitative`** is 2–4 plain sentences (~100 words max), for a reader who never saw the skill. It should:

1. Give the same numbers in words:
   - how many rules
   - how many strict vs. only suggestions
   - how many situational vs. always on
   - the main form (running text, bullet points, table, heading, front matter)
2. Say concretely what the rules make the agent do or not do, and when:
   - use everyday words
   - explain a technical term the first time it appears
   - put commands, files and tools in backticks
   - with more than four rules, group the similar ones
3. Stay within what the statements (and the sentence or heading right around them) say:
   - no judging
   - no guessing the author's intent
   - no extra rules

If the category is empty, use its fixed sentence:

- `autonomy_limits`: The skill never forbids or restricts any action of the agent on files, commands, tools or other systems, and never tells it to go ahead without asking.
- `clarification_rules`: The skill never tells the agent to ask the user for missing or unclear information, or to avoid guessing.
- `approval_gates`: The skill never tells the agent to get the user's permission or confirmation before doing something.
- `validation`: The skill never tells the agent to check its own work, such as running tests, or says when the work counts as done.
- `escalation`: The skill never tells the agent what to do when something goes wrong, such as stopping or reporting an error to the user.

### Overall conclusion

**`conclusion_quantitative`** uses one of two formats:

- All empty: `<name> (<mechanism>) specifies none of the 5 categories.`
- Otherwise: `<name> (<mechanism>) specifies <k> of 5 categories: <present>; none for <missing>. Strongest: <strongest>.`

The parts:

- `<name>`, `<mechanism>`: write `unknown` when `null`.
- `<k>`: the number of categories with at least one statement.
- `<present>`: `<count> <label>` for each non-empty category, joined by `, `.
- `<missing>`: the plural labels of the empty categories, joined by `, `. Drop `; none for <missing>` if none are empty.
- `<strongest>`: the plural label of the largest category.

Order for `<present>`, `<missing>` and ties in `<strongest>`: autonomy limits, clarification rules, approval gates, validation rules, escalation rules.

**`conclusion_qualitative`** is 3–5 plain sentences (~120 words max), with the same limits as the category ones. It should:

1. Say what the skill is for, from the front matter `description` (else the first heading and its paragraph).
2. Describe how control is shared between agent and human:
   - what the agent may or must not do alone
   - when it asks or waits for approval
   - how it checks its work
   - what it does on failure
   - only non-empty categories, largest first
3. Name the categories it leaves out, if any.

If every category is empty, write two sentences:

- one on what the skill is for
- one saying it gives no rules on acting alone, asking or waiting for the user, checking work, or handling failure
