# kern-skills
KERN: Kennis, Essentie, Regels, Naamgeving

English: Knowledge, Essence, Rules, Notions

This repository is work-in-progress and contains skill files to:
- build an (enterprise) ontology (transactions, processes, facts, rules, term and definitions) from input text
- validate an (enterprise) ontology against some pre-defined quality criteria and check its internal consistency

These skills follow the open Agent Skills standard, so they work in both Claude Code and Google Antigravity without any changes.

## Skills

| Skill | Description | Documentation |
|---|---|---|
| [`definitiekwaliteit`](skills/definitiekwaliteit) | Checks a glossary (terms, definitions, references, examples) against the ASTRA rules for definition quality plus additional KERN rules, and proposes improved definitions, references, examples and missing terms. Includes a reference graph of the definitions to find cycles and undefined terms. In Dutch. | [docs/definitiekwaliteit.md](docs/definitiekwaliteit.md) |

Detailed documentation per skill is in the [`docs`](docs) folder.

## Quick start
 
You can either manually download the required skill files or simply clone this repo:
 
```bash
git clone https://github.com/mkrouwel/kern-skills.git
cd kern-skills
```
 
Then copy the skill folders into the location for your tool (see below). You can install all skills or just the ones you need.
 
### Using with Claude Code
 
Works with the Claude Code CLI, the VS Code and JetBrains extensions, and the Claude desktop app. All of them read skills from the same folders.
 
**Personal install (available in all your projects):**
 
```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```
 
**Project install (available only in one project, shared with anyone who clones it):**
 
```bash
mkdir -p /path/to/your-project/.claude/skills
cp -r skills/* /path/to/your-project/.claude/skills/
```
 
Claude Code picks up new skills automatically. If the `skills` folder didn't exist before you started your session, restart Claude Code once.
 
Docs: https://code.claude.com/docs/en/skills
 
### Using with Google Antigravity
 
**Project install (IDE and CLI):**
 
```bash
mkdir -p /path/to/your-project/.agents/skills
cp -r skills/* /path/to/your-project/.agents/skills/
```
 
**Global install, Antigravity IDE:**
 
```bash
mkdir -p ~/.gemini/config/skills
cp -r skills/* ~/.gemini/config/skills/
```
 
**Global install, Antigravity CLI (`agy`):**
 
```bash
mkdir -p ~/.gemini/antigravity-cli/skills
cp -r skills/* ~/.gemini/antigravity-cli/skills/
```
 
In the IDE, you can confirm the skills are loaded under the **Customizations** menu in the agent side panel.
 
Docs: https://antigravity.google/docs/skills
 
## How to use the skills
 
Just describe your task normally. The agent reads each skill's description and automatically loads the relevant one when it fits your request.
 
In Claude Code you can also call a skill directly by typing `/skill-name`.
