---
name: tonelli-git-commit-generator
description: v2. Generates and, after explicit approval, executes high-quality git commits written in Brazilian Portuguese (pt-BR), following Conventional Commits, based on the real diff (not file names). Detects type, scope, and breaking changes automatically, with dedicated support for React, Next.js, Node, and ADVPL/Protheus. Use this skill whenever the user triggers "/commit" or asks to commit in any way: "realize o commit", "faÃ§a o commit", "commite as mudanÃ§as", "crie o commit", "commite pra mim", "gere o commit", or equivalent requests (in Portuguese or English).
---

# Tonelli Git Commit Generator (v2)

Generate the commit message by reading the *actual diff*, not the names of the changed files â€” file names lie about what changed, the diff doesn't. This is a **single-run workflow**, followed in the order below. If any validation step fails, stop, show the error to the user, and cancel â€” do not try to proceed, fix, or work around it on your own.

The workflow, reasoning, and internal instructions are in English. The **generated commit message (subject, body, footer) and everything shown to the user is always in pt-BR** â€” see step 7.

## 1. Validate repository state (abort on failure)

Run (prefer the `rtk` wrapper when available, per the user's global instructions; if `rtk` is not installed or the command fails as unrecognized, fall back to plain `git` without blocking the flow):
```
rtk git status --short --branch
```
Check, in this order, and cancel with a clear message to the user if anything fails:
- Is this a valid git repository?
- Is there an operation in progress (merge, rebase, cherry-pick) currently stuck?
- Are there unresolved conflicts?
- Is there actually any change to commit (staged or in the working tree)? If not, report it and stop.

## 2. Inspect the changes

Work **only with staged files** â€” never analyze or rewrite already-committed history.
```
rtk git diff --staged   # changes that will go into the commit
rtk git diff            # unstaged changes, just to check what would be left out
```
If nothing is staged, tell the user and stop (do not run `git add` yourself unless the user asks).

If there is any modified file **or new/untracked file** that is **not** staged, warn the user that these files will be left out of the commit, list them, and ask `[y]` to continue with only what's staged or `[n]` to cancel. Only proceed to the semantic analysis after this confirmation.

**Security check:** before continuing, check two things â€”
- **Diff content**: keys/tokens, credentials, connection strings, service accounts, or values that look like secrets.
- **Name/path of staged files**: patterns like `.env*`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`, `service-account*.json`, or any file typically used to store secrets, even if the content looks harmless at first glance.

If you find either, **cancel the commit and alert the user** instead of proceeding.

## 3. Read recent history for consistency

```
rtk git log --oneline -10
```
If recent commits already follow the convention (type(scope): description), use them as a style/scope reference to keep the repository consistent. If the history doesn't follow any clear convention, ignore it and follow this skill's rules normally. If the repository has no commits yet (the command fails because there's no HEAD), treat this as expected and just skip this step. Regardless of the language of previous commits, the generated message is **always in pt-BR**.

## 4. Detect the stack and the scope

Don't guess the stack â€” confirm it with concrete signals (`package.json`, `tsconfig.json`, lockfiles, `.prw`/`.tlpp` extensions, typical Protheus folder structure, etc.) before deciding. Read the diff itself, not the file names, to understand what changed.

Determine the scope by looking at both folder **and** content:
- **Monorepo**: prefer the name of the affected package/workspace.
- **Frontend (React/Next.js)**: `frontend`, `ui`, `pages`, `components`, `hooks`, or the specific name of the affected component/route (e.g. `src/components/Button.tsx` â†’ `button` or `ui`).
- **Backend (Node)**: `api`, `backend`, `auth`, `database`, `services`, or the specific name of the affected module (e.g. `src/services/auth.ts` â†’ `auth`).
- **Infra**: `infra`, `docker`, `aws`, `ci`, `build`, or whatever makes the most sense for the change.
- **ADVPL/Protheus**: look for the Protheus module in the path (`sigafat`, `sigacom`, `sigatms`, `sigatmk`, `sigawms`, etc.) combined with the routine/function changed in the code; if no specific module is found, use `protheus`, `advpl`, or `tlpp`.
- These lists are a guide, not a closed list â€” use the most specific and stable name that makes sense for the actual change.
- If the change touches multiple areas with no clear common denominator, **omit the scope** instead of inventing something generic like "general".

## 5. Classify the type (Conventional Commits)

Classify by the **semantics of the change**, never by metadata or file name:
- `feat` â€” new feature or visual interface.
- `fix` â€” bug fix.
- `perf` â€” performance optimization (prefer `perf` over `refactor` when the performance gain is the actual goal of the change).
- `refactor` â€” large restructuring, with no new features, fixes, or performance gain.
- `docs` â€” documentation.
- `style` â€” formatting, spacing, columns â€” no actual code change.
- `test` â€” adding or fixing tests.
- `build` â€” builds, dependencies, packages.
- `ci` â€” CI/CD, pipelines, pipeline configs, pipeline-related Docker.
- `chore` â€” tooling maintenance, config, gitignore, housekeeping.
- `revert` â€” reverting a previous commit.

If the diff mixes unrelated types, warn the user and suggest splitting into more than one commit instead of forcing a generic type â€” prefer atomic commits.

## 6. Detect breaking changes

Look at the diff carefully, not the original author's message:
- Public/exported function signature changed (parameters removed/reordered, return type changed).
- API/endpoint removed or renamed, or response contract changed incompatibly.
- Database schema, required environment variable, or required parameter changed in a way that breaks existing consumers.
- ADVPL: `WSRESTFUL`/`WSMETHOD` signature changed, public function parameter (`U_*`) removed/renamed, table structure changed incompatibly.

If you detect a breaking change, add `!` right after the type/scope (e.g. `feat(api)!: ...`) and include a `BREAKING CHANGE: <explanation in pt-BR>` footer.

## 7. Build the message (always in pt-BR)

Everything in pt-BR. **Code identifiers (function names, variables, files, tables, fields, API routes) stay exactly as they are in the code â€” do not translate them.** Example: `feat(auth): adicionar validaÃ§Ã£o no AuthService.login()`.

- **Subject**: `type(scope)[!]: description` â€” target <50 characters, hard max 70, starts with a lowercase letter, no trailing period, imperative mood, focused on the *effect* of the change (never "ajustes", "melhorias", "correÃ§Ãµes", "update", "fixes", "mudanÃ§as", or anything generic).
- **Body**: include whenever possible, even for a simple hotfix or a small visual tweak â€” explain what changed and why. May be omitted only for truly trivial, self-explanatory changes (e.g. typo, isolated spacing tweak). Wrap lines at ~70 columns.
- **Footer**: only when applicable â€” `BREAKING CHANGE: ...` when there is one.
- **No emoji, gitmoji, or decoration** in subject/body/footer â€” the message must be professional, plain text.
- **Never use `--allow-empty`** or generate an empty commit, unless the user explicitly asks to push an empty commit.

This skill only handles **new commits**. If the user asks to fix, edit, or adjust the last commit (`amend`), that's a different workflow and out of scope for this skill â€” don't confuse the two or try to adapt the steps above for an amend.

## 8. Check the current branch before proposing the commit

If the current branch is `qa`, `master`, or `main` (case-insensitive comparison, e.g. `Main` also counts), tell the user they're about to commit directly to a sensitive branch and ask for explicit confirmation before continuing. Only proceed to the commit proposal if they authorize it; if they refuse, stop the process without generating anything.

## 9. Present the proposal (output format)

Use exactly this format (in pt-BR, as this is user-facing):

```
### Commit sugerido
<subject>

### Corpo sugerido
<body, se houver>

### ConfirmaÃ§Ã£o
Executar este commit?
[y] Sim  [n] NÃ£o
```

## 10. Execute only after explicit confirmation

If the user confirms with "y"/"sim", execute the commit safely:
- Write the full message (subject + body + footer) to a temporary file **outside the repository** (e.g. a scratchpad/system temp folder, never inside the working tree â€” this avoids the file being picked up by a future `git add`), with **explicit UTF-8 encoding** (in PowerShell, `Out-File -Encoding utf8`; in bash, a heredoc/`printf` is already UTF-8) to correctly preserve pt-BR accents.
- Run `git commit -F <path-to-temp-file>` â€” never `-m` with multi-line content or unhandled special characters.
- Delete the temporary file right after, whether the commit succeeds or fails.
- If the commit fails, **stop immediately and report the error to the user**. Don't retry, don't force it (`--no-verify` etc.), don't try to fix the problem yourself.
- If the user answers "n"/"nÃ£o", cancel without executing anything.

## Scope of this skill

This skill exists **only** to generate and, with approval, execute the commit described above. Don't do anything else (don't create branches, don't push, don't edit code, don't resolve conflicts) unless explicitly requested outside this flow.

## Special cases

- **Multiple unrelated staged changes**: point this out to the user before forcing a single message; offer to generate one message per logical group.
- **Merge commits / unresolved conflicts**: already handled in step 1 (aborts before reaching this point).
