# `yadm-consistency` — consistency of a YADM model

Skill folder: [`skills/yadm-consistency`](../skills/yadm-consistency)

Checks a DEMO model exported from YADM (JSON). It compares the Cooperation Structure Diagram (CM/CSD) with the fact model (FM/OFD) and, optionally, the fact model with a glossary. The glossary check also covers content: specialisations, generalisations and aggregations are compared with the genus and the definitions. The skill and its output are in Dutch.

## Dependencies

This skill builds on three other skills and imports their scripts. Install them in the same skills folder:

| Skill | Used for |
|---|---|
| [`yadm-tpt`](yadm-tpt.md) | reading the CM: transaction kinds, type O/I/D, initiators, information links |
| [`yadm-facttypes`](yadm-facttypes.md) | reading the FM: entity types, property, attribute and product kinds, derivations, merging diagrams |
| [`definitiekwaliteit`](definitiekwaliteit.md) | reading the glossary; genus and enumerations in definitions (only with `-b`) |

## Input

- **YADM exports:** all JSON exports that together form the model (the CM and all FM diagrams), in one run. The script detects which export is a CM and which is an FM.
- **Glossary (optional):** a glossary in the format of [`definitiekwaliteit`](definitiekwaliteit.md).
- **BCT (optional):** a bank contact table (*bankcontactentabel*) that lists, per bank of a multiple transaction kind (MTK) or transaction kind (TK), which facts it holds. CSV with `;` or `,`, one fact type per row, column names not case-sensitive:

  | Column | Required | Content |
  |---|---|---|
  | `feittype` | yes | as in the fact extraction of [`yadm-facttypes`](yadm-facttypes.md): `NAME*`, `attribute van [entity type]`, the formulation of a property type, `formulation (PKnn)` |
  | `bank ID` | no | number of the MTK or TK; empty if the fact belongs to no bank |
  | `bank` | no | name of the bank (for an MTK equal to its name in the CM) |
  | `soort`, `waardetype`, `afleiding` | no | as in the fact extraction; compared when filled |
  | `bron FM` | no | the diagrams (fileName) the fact appears in, comma-separated |
  | `Opm tav BCT` or `opmerking` | no | required for a row without a bank: why (e.g. "gedekt door <fact type>", "niet relevant") |

  Abbreviations are allowed: an entity type row `POLITIEKE GROEPERING (PG)` makes `[PG]` elsewhere in the BCT equal to `[politieke groepering]`.

  **Tip:** create the BCT from the fact extraction: `python -I skills/yadm-facttypes/scripts/feittypen.py <FM exports> -b bct.csv` writes a template with every fact type, its type, value type, derivation and source diagrams. Only `bank ID` and `bank` remain to be filled, so the BCT matches the fact model from the start.

## What it produces

- **Summary:** a table with the number of findings per rule. A rule that could not be checked (no CM, no FM or no glossary) is shown as "—".
- **Findings:** a table `Regel | Element | Bevinding | Bron`.

The model then groups findings by cause and judges the glossary findings on content. It proposes changes to the model, the formulations or the definitions.

## Rules

The rules are in [`references/regels.csv`](../skills/yadm-consistency/references/regels.csv) (in Dutch), with columns `Id`, `Categorie`, `Ernst` (severity: fout, waarschuwing, signaal), `Regel` and `Controle` (how the script checks it). The script reads its rule descriptions from this file and stops if it uses an ID that is not in it.

Rule IDs have the form `KERN-C-<category><number>`; `C` stands for consistency. [`definitiekwaliteit`](definitiekwaliteit.md) uses `KERN-D-`, so IDs are unique across the skills. Categories:

| Code | Category | Covers |
|---|---|---|
| CM | coöperatiemodel | the CM itself, for example every transaction kind that is not self-activating has an initiator |
| TK | transactiesoort en productsoort | CM against FM: every original transaction kind has a product kind and vice versa; information links to a transaction bank |
| PK | productsoort | product kinds: linked entity type and formulation |
| ES | eigenschapsoort | property types: variables in the formulation, cardinalities |
| AS | attribuutsoort | attribute types: value types, duplicates |
| ET | entiteittype | entity types: an entity type in focus has a product kind; no isolated entity types |
| NM | naamgeving over diagrammen | entity types, transaction kinds, actor roles, MTKs and product kinds have the same label in every diagram |
| TL | export (tool) | edges to missing nodes and headers "A"; problems in YADM, not in the model |
| BG | begrippenlijst | the fact model against the glossary (only with `-b`) |
| BC | bankcontactentabel | the fact model against the BCT (only with `-t`): every FM fact in the BCT and vice versa; type, value type and derivation; the `bron FM` column; banks that exist in the CM; product kinds in the bank of their own TK; internal facts in a TK bank, external ones in an MTK bank; duplicates; rows without a bank explained |

A new rule gets the next number in its category; an existing ID never changes meaning.

## Script

```
python -I skills/yadm-consistency/scripts/consistentie.py "<CM>.json" "<FM>.json" [more exports …] [-b glossary.csv] [-t bct.csv] [-o report.md]
```

No dependencies beyond the Python standard library and the three skills above.
