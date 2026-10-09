# kern-skills
KERN: Kennis, Essentie, Regels, Naamgeving

English: Knowledge, Essence, Rules, Notions

This repository is work-in-progress and contains skill files to:
- build an (enterprise) ontology (transactions, processes, facts, rules, term and definitions) from input text
- validate an (enterprise) ontology against some pre-defined quality criteria and check its internal consistency

## Skills

| Skill | Description | Documentation |
|---|---|---|
| [`definitiekwaliteit`](skills/definitiekwaliteit) | Checks a glossary (terms, definitions, references, examples) against the ASTRA rules for definition quality plus additional KERN rules, and proposes improved definitions, references, examples and missing terms. Includes a reference graph of the definitions to find cycles and undefined terms. In Dutch. | [docs/definitiekwaliteit.md](docs/definitiekwaliteit.md) |

Detailed documentation per skill is in the [`docs`](docs) folder.
