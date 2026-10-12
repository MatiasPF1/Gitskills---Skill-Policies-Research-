# GitSkills mining

Notebooks and helpers for exploring the sample of the **GitSkills** dataset (agent skills, i.e. `SKILL.md` files, from GitHub) and for finding skills that tell an agent when to stop, ask, or wait for a human.

## Setup

```
pip install pandas notebook
```

Download the sample database (about 290 MB, not in this repository) from [giuseppedestefanis/gitskills-sample](https://github.com/giuseppedestefanis/gitskills-sample) and place it at `SQL_Lite_Source/agent_skills_sample.db`.

Run each notebook from its own folder, since the helpers are imported through a relative path.

## Layout

| Folder | Contents |
| --- | --- |
| [HelperFunctions/](HelperFunctions/) | all the logic, one module per topic |
| [Mining_Explore_Notebooks/](Mining_Explore_Notebooks/) | one notebook per table: column types and numeric stats. `3_artifacts` adds filenames, front matter, locations (RQ 2a) and copies (RQ 3a) |
| [Questions_notebook/](Questions_notebook/) | RQ 1a adoption: repos by language, stars, age, activity and first skill commit |
| [Mechanisms/](Mechanisms/) | one folder per human-control mechanism: a notebook and the skills it saved in `Found/` |

Notebooks only import the helpers and call one function per cell.

## The database

| Table | Rows | One row is |
| --- | ---: | --- |
| `mining_runs` | 7 | a search run that discovered files |
| `repos` | 11,841 | a GitHub repository |
| `artifacts` | 29,786 | a skill file found in a repository |
| `artifact_siblings` | 47,829 | a file or folder next to a skill file |

- **Representatives:** identical files share a `file_sha`, and only one per content (`dedup_primary = 1`) has its text, front matter and folder contents.
- **Skill-file rule:** a file counts as a skill if it is named exactly `SKILL.md`, has valid front matter, or sits in a skills folder. This is `SKILL_FILE` in [Adoption.py](HelperFunctions/HelperFunctions_Adoption/Adoption.py).

## Human-control mechanisms

| Mechanism | What the skill tells the agent |
| --- | --- |
| Scope boundary | what it must leave alone |
| Clarification trigger | when to ask instead of guessing |
| Approval gate | when to wait for a human yes |
| Planning transparency | to show its plan before acting |
| Validation requirement | to check its work before finishing |
| Escalation / rollback | to stop or undo instead of pushing on |

Each mechanism has a keyword set in [Mechanisms.py](HelperFunctions/HelperFunctions_Mechanisms/Mechanisms.py). Its notebook saves the 15 representative skills containing the most different keywords to `Found/<file_sha>.md`.

This picks skills worth reading; it does not measure how common a mechanism is. Matching is by plain substring, and ties are broken by `file_sha`.

## Limits of the data

- Text-based results describe distinct contents, not all files.
- Commit history covers only part of the files, so date-based counts are not a random sample.
- Copies outside the sample are not seen, so reuse is a lower bound.

## Source

Destefanis, Graziotin, Vaccargiu, Ortu. *GitSkills: A Dataset of Agent Skills on GitHub*. MSR '27. arXiv:2608.10906. Full dataset: doi [10.5281/zenodo.21875637](https://doi.org/10.5281/zenodo.21875637).
