---
name: arc42-docs
description: Use this skill when the user asks to "create architecture documentation", "document the architecture", "arc42", "initialize arc42", "update architecture docs", discusses architecture documentation, or wants to document system design decisions, quality requirements, deployment views, building blocks, or any of the 12 arc42 sections. Also use when the user mentions ADRs (Architecture Decision Records) in the context of arc42.
version: 2.0.0
---

# Arc42 Architecture Documentation Skill

Guide for using the `arc42-mcp-server` MCP server to create and maintain architecture documentation following the proven [arc42 template](https://arc42.org/). The server provides 6 tools, supports 11 languages and 2 output formats (AsciiDoc, Markdown).

## Prerequisites

The `arc42-mcp-server` MCP server must be configured and running. See [setup instructions](references/setup.md) for installation and configuration.

---

## Workflow: Starting Fresh

1. **Load the guide** → `arc42-workflow-guide` — understand the full arc42 structure and what belongs in each section
2. **Initialize workspace** → `arc42-init` — creates directory structure with all 12 section files, config.yaml, and README
3. **Check status** → `arc42-status` — see current progress, completeness percentage, and which sections need work
4. **Generate template** → `generate-template` — get the detailed structure and guidance for a specific section before writing
5. **Write content** → `update-section` — write or append content to a section
6. **Review content** → `get-section` — read back existing content with metadata (word count, last modified)

## Workflow: Existing Documentation

1. **Check status** → `arc42-status` — assess current state and identify gaps
2. **Read sections** → `get-section` — review what's already documented
3. **Generate template** → `generate-template` — understand expected structure for incomplete sections
4. **Update sections** → `update-section` — fill gaps or improve existing content

---

## Tool Reference

### 1. arc42-workflow-guide

Load the comprehensive arc42 documentation workflow guide. **Always call this first** when starting a new documentation effort — it explains what information belongs in each section.

| Parameter  | Type | Required | Default      | Description                                                                      |
|------------|------|----------|--------------|----------------------------------------------------------------------------------|
| `language` | enum | No       | `"EN"`       | Language code: `EN`, `DE`, `ES`, `FR`, `IT`, `NL`, `PT`, `RU`, `CZ`, `UKR`, `ZH` |
| `format`   | enum | No       | `"asciidoc"` | Output format: `asciidoc` (or `adoc`), `markdown` (or `md`)                      |

**Returns:** Complete workflow guide text with section explanations, available languages, supported formats, and workspace root path.

### 2. arc42-init

Initialize the arc42 documentation workspace. Creates `arc42-docs/` directory with all 12 section files, `config.yaml`, README, and a main documentation file.

| Parameter      | Type    | Required | Default        | Description                                                        |
|----------------|---------|----------|----------------|--------------------------------------------------------------------|
| `projectName`  | string  | **Yes**  | —              | Name of the project being documented                               |
| `language`     | enum    | No       | `"EN"`         | Language code (see above)                                          |
| `format`       | enum    | No       | `"asciidoc"`   | Output format: `asciidoc`/`adoc` or `markdown`/`md`                |
| `force`        | boolean | No       | `false`        | Force re-initialization even if workspace already exists           |
| `targetFolder` | string  | No       | server default | Absolute path to target folder where `arc42-docs/` will be created |

**Returns:** Workspace root path, sections created count, config (including arc42 template reference version, date, and commit SHA).

**Created structure:**

```
<targetFolder>/arc42-docs/
├── README.md
├── arc42-documentation.adoc (or .md)
├── config.yaml
├── sections/
│   ├── 01_introduction_and_goals.adoc (or .md)
│   ├── 02_architecture_constraints.adoc (or .md)
│   └── ... (all 12 sections)
└── images/
```

### 3. arc42-status

Check documentation completion status. Shows per-section progress with word counts, completeness percentages, and overall progress.

| Parameter      | Type   | Required | Default        | Description                                      |
|----------------|--------|----------|----------------|--------------------------------------------------|
| `targetFolder` | string | No       | server default | Absolute path to folder containing `arc42-docs/` |

**Returns:** Project name, initialized state, language and format info, arc42 template reference version, per-section status (exists, word count, completeness 0-100%, last modified), and overall completeness percentage.

### 4. generate-template

Generate a detailed template for a specific section. **Always use this before writing content** — it provides the expected structure, subsections, and guidance for what information to include.

| Parameter  | Type | Required | Default      | Description                                         |
|------------|------|----------|--------------|-----------------------------------------------------|
| `section`  | enum | **Yes**  | —            | Section ID (see section reference below)            |
| `language` | enum | No       | `"EN"`       | Language code                                       |
| `format`   | enum | No       | `"asciidoc"` | Output format: `asciidoc`/`adoc` or `markdown`/`md` |

**Returns:** Complete template content with guidance, section metadata (title, description, order), format details.

### 5. update-section

Write content to a specific section. Format is auto-detected from existing files or `config.yaml`.

| Parameter      | Type   | Required | Default        | Description                                                 |
|----------------|--------|----------|----------------|-------------------------------------------------------------|
| `section`      | enum   | **Yes**  | —              | Section ID (see section reference below)                    |
| `content`      | string | **Yes**  | —              | The content to write to the section                         |
| `mode`         | enum   | No       | `"replace"`    | `"replace"` overwrites, `"append"` adds to existing content |
| `targetFolder` | string | No       | server default | Absolute path to folder containing `arc42-docs/`            |

**Returns:** Section title, file path, detected format, word count, and write mode used.

**Important:** Use `mode: "append"` when adding ADRs (Section 9) or adding incremental content to avoid overwriting existing entries.

### 6. get-section

Read content from a specific section, including metadata.

| Parameter      | Type   | Required | Default        | Description                                      |
|----------------|--------|----------|----------------|--------------------------------------------------|
| `section`      | enum   | **Yes**  | —              | Section ID (see section reference below)         |
| `targetFolder` | string | No       | server default | Absolute path to folder containing `arc42-docs/` |

**Returns:** Section content, language, format, title, description, and file metadata (path, last modified timestamp, word count, file size in bytes).

---

## The 12 Arc42 Sections

| #  | Section ID                    | Name                     | Key Content                                                       |
|----|-------------------------------|--------------------------|-------------------------------------------------------------------|
| 1  | `01_introduction_and_goals`   | Introduction and Goals   | Requirements overview, quality goals, stakeholders                |
| 2  | `02_architecture_constraints` | Architecture Constraints | Technical, organizational, and political constraints              |
| 3  | `03_context_and_scope`        | Context and Scope        | Business context, technical context, external interfaces          |
| 4  | `04_solution_strategy`        | Solution Strategy        | Technology decisions, top-level decomposition, quality approaches |
| 5  | `05_building_block_view`      | Building Block View      | Static decomposition (Level 1, 2, 3) of the system                |
| 6  | `06_runtime_view`             | Runtime View             | Key scenarios, sequence diagrams, process flows                   |
| 7  | `07_deployment_view`          | Deployment View          | Infrastructure, deployment diagrams, node mapping                 |
| 8  | `08_concepts`                 | Cross-cutting Concepts   | Security, persistence, logging, error handling patterns           |
| 9  | `09_architecture_decisions`   | Architecture Decisions   | ADRs with context, decision, status, and consequences             |
| 10 | `10_quality_requirements`     | Quality Requirements     | Quality tree, quality scenarios                                   |
| 11 | `11_technical_risks`          | Risks and Technical Debt | Known risks, technical debt items                                 |
| 12 | `12_glossary`                 | Glossary                 | Domain terms and definitions                                      |

---

## Recommended Documentation Order

Start with the most impactful sections. You do NOT need to document all 12 sections sequentially.

| Priority | Section                                          | Why                                                                   |
|----------|--------------------------------------------------|-----------------------------------------------------------------------|
| 1st      | **Section 1** — Introduction and Goals           | Always start here: establishes scope, quality goals, and stakeholders |
| 2nd      | **Section 3** — Context and Scope                | Define system boundaries and external interfaces early                |
| 3rd      | **Section 4** — Solution Strategy                | Capture key technology and design decisions                           |
| 4th      | **Section 5** — Building Block View              | Document the system's static structure                                |
| 5th      | **Section 9** — Architecture Decisions           | Record important ADRs while decisions are fresh                       |
| Then     | **Section 2** — Constraints                      | Document technical/organizational constraints                         |
| Then     | **Sections 6–8** — Runtime, Deployment, Concepts | Fill in dynamic behavior, infrastructure, cross-cutting concerns      |
| Last     | **Sections 10–12** — Quality, Risks, Glossary    | Complete the documentation                                            |

---

## Behavioral Guidelines

### Before Writing Any Section

1. **Generate the template first** — call `generate-template` for the section to understand the expected structure and subsections
2. **Ask clarifying questions** — never assume project details; ask the user about their specific context, technologies, and decisions
3. **Check existing content** — call `get-section` to see if there's already content to build upon
4. **Respect the configured format** — call `arc42-status` to check whether the project uses AsciiDoc or Markdown, then write content in that format

### Content Quality

- **Document WHY, not just WHAT** — focus on rationale and trade-offs behind decisions
- **Include diagrams** — use Mermaid or PlantUML syntax for context diagrams, building block views, deployment views, and sequence diagrams
- **Be specific** — use concrete technology names, version numbers, and measurable quality attributes
- **Keep sections focused** — each section has a distinct purpose; avoid duplicating information across sections
- **Use proper formatting** — match the output format (AsciiDoc uses `=` headings, admonitions with `NOTE:`, `TIP:`; Markdown uses `#` headings)

### ADR Best Practices (Section 9)

- **Always use `mode: "append"`** when adding new ADRs to avoid overwriting existing ones
- **Always call `get-section` first** to read existing ADRs and determine the next ADR number
- **Follow a consistent ADR structure**: Title with number, Status, Context, Decision, Consequences (positive and negative)

### Using Tool Responses

Every tool response includes:

- `success` — boolean indicating whether the operation succeeded
- `message` — human-readable summary of what happened
- `data` — structured response data (varies by tool)
- `nextSteps` — array of suggested follow-up actions; use these to guide the user on what to do next

---

## Multi-Language Support

11 languages are supported. Set the language during `arc42-init`; it persists in `config.yaml` and applies to all subsequent operations.

| Code | Language | Code  | Language   |
|------|----------|-------|------------|
| `EN` | English  | `PT`  | Portuguese |
| `DE` | German   | `RU`  | Russian    |
| `ES` | Spanish  | `CZ`  | Czech      |
| `FR` | French   | `UKR` | Ukrainian  |
| `IT` | Italian  | `ZH`  | Chinese    |
| `NL` | Dutch    |       |            |

## Multi-Format Support

| Format                 | Aliases            | Extension | Best For                                                                             |
|------------------------|--------------------|-----------|--------------------------------------------------------------------------------------|
| **AsciiDoc** (default) | `asciidoc`, `adoc` | `.adoc`   | Professional docs — supports includes, admonitions, cross-references, TOC generation |
| **Markdown**           | `markdown`, `md`   | `.md`     | Simplicity — widely supported, GitHub/GitLab rendering                               |

Set the format during `arc42-init`. The `update-section` tool auto-detects the format from existing files or `config.yaml`. Format aliases (`md`/`adoc`) are accepted anywhere a format parameter is used.

---

## Examples

See [references/examples.md](references/examples.md) for detailed usage examples covering:

- Starting a new project from scratch
- Documenting a specific section (e.g., deployment view)
- Adding Architecture Decision Records (ADRs) with proper append mode
- Documenting cross-cutting concepts
- Multi-language documentation
- Reviewing and improving existing documentation
- Re-initializing an existing workspace
