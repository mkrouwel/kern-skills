# `yadm-consistency` — consistency of a YADM model

Skill folder: [`skills/yadm-consistency`](../skills/yadm-consistency)

Checks a DEMO model exported from YADM (JSON). It compares the Cooperation Structure Diagram (CM/CSD) with the fact model (FM/OFD) and, optionally, the fact model with a glossary. The glossary check also covers content: specialisations, generalisations and aggregations are compared with the genus and the definitions. The skill and its output are in Dutch.

## Dependencies

This skill builds on three other skills and imports their scripts. Install them in the same skills folder:

| Skill | Used for |
|---|---|
| [`yadm-tpt`](yadm-tpt.md) | reading the CM: transaction kinds, type O/I/D, information links |
| [`yadm-facttypes`](yadm-facttypes.md) | reading the FM: entity types, property, attribute and product kinds, derivations, merging diagrams |
| [`definitiekwaliteit`](definitiekwaliteit.md) | reading the glossary; genus and enumerations in definitions (only with `-b`) |

## Input

- **YADM exports:** all JSON exports that together form the model (the CM and all FM diagrams), in one run. The script detects which export is a CM and which is an FM.
- **Glossary (optional):** a glossary in the format of [`definitiekwaliteit`](definitiekwaliteit.md).

## What it produces

- **Summary:** a table with the number of findings per rule. A rule that could not be checked (no CM, no FM or no glossary) is shown as "—".
- **Findings:** a table `Regel | Element | Bevinding | Bron`.

The model then groups findings by cause and judges the glossary findings on content. It proposes changes to the model, the formulations or the definitions.

## Rules

| Rule | Severity | Description |
|---|---|---|
| CON-01 | fout | Every original transaction kind (O) in the CM has a product kind in the FM |
| CON-02 | fout | Every product kind in the FM belongs to an original transaction kind in the CM |
| CON-03 | fout | One transaction kind has one product kind |
| CON-04 | fout | An information link to TKnn in the CM requires product kind PKnn in the FM |
| CON-05 | fout | A product kind is linked to the entity type that is the variable in its formulation (for an aggregate: its components) |
| CON-06 | waarschuwing | A product kind has one variable (for an aggregate: its components) and ends in "is/zijn + past participle" |
| CON-07 | fout | Both ends of a property type are variables in its formulation |
| CON-08 | fout | The target end (in the direction of the line) is 0..1 or 1..1 |
| CON-09 | waarschuwing | The source end has a cardinality |
| CON-10 | fout | Every attribute type has a value type |
| CON-11 | fout | An attribute type occurs once per entity type, with the same value type in every diagram |
| CON-12 | fout | An entity type in focus (internal, white; `data.focus` = `in`) has at least one product kind. A product kind may be linked to an entity type out of focus |
| CON-13 | waarschuwing | No isolated entity types |
| CON-14 | fout | An element has the same name in every diagram |
| CON-15 | waarschuwing | No edges to missing nodes and no entity types with header "A" (tool problems) |
| BEG-01 | fout | Every entity type has a term in the glossary |
| BEG-02 | fout | Specialisation: the genus of the definition is the parent in the FM |
| BEG-03 | fout | Generalisation: the definition enumerates the members, and an enumerating definition is a generalisation |
| BEG-04 | fout | Aggregation: the definition refers to all components |
| BEG-05 | signaal | The definition of the owner of a property type refers to the other entity type |
| BEG-06 | signaal | Terms without an entity type |

## Script

```
python -I skills/yadm-consistency/scripts/consistentie.py "<CM>.json" "<FM>.json" [more exports …] [-b glossary.csv] [-o report.md]
```

No dependencies beyond the Python standard library and the three skills above.
