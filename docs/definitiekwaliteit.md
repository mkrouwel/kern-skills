# `definitiekwaliteit` — definition quality check

Skill folder: [`skills/definitiekwaliteit`](../skills/definitiekwaliteit)

Checks a glossary (terms with definitions, references, examples and counterexamples) against quality rules for definitions, and proposes improvements. The skill and its rules are in Dutch.

## Input: the glossary

A CSV file (UTF-8, separator `;` or `,`), a Markdown table, or a table pasted into the conversation. One row per term. Column names are case-insensitive; the alternatives in brackets are also accepted.

| Column | Required | Content |
|---|---|---|
| `term` (`begrip`) | yes | The term, singular. A context qualifier goes in brackets at the end: `algemeen bestuur (wpp)`. Variables go in square brackets: `politieke vereniging op [dag]`. |
| `definitie` | yes | One sentence, without article and without "is", so that it can replace the term in a sentence: `orgaan dat …` |
| `acroniem` (`acro`, `afkorting`) | no | Abbreviation(s) of the term |
| `synoniemen` (`synoniem`) | no | Other terms for the same concept |
| `grondslag` (`bron`, `referentie`) | no | Source and exact location, including the version: `Wpp art. 1 (Kamerstuk 36 742, bijgewerkt t/m nr. 20)` |
| `voorbeelden` (`voorbeeld(en)`) | no | Instances that fall under the definition — concrete cases, not counts. For time-dependent terms, include the day. |
| `tegenvoorbeelden` (`tegenvoorbeeld(en)`) | no | Cases that fall just outside the definition |
| `toelichting` (`toelichting of opmerking`, `opmerkingen`) | no | Explanation that does not belong in the definition |
| `context` (`domein`) | no | Context of the term, if it differs from the list as a whole |

- **Multiple values in one cell** (synonyms, examples): separate with `|`. A comma also works for synonyms and abbreviations.
- **Line breaks and separators inside a cell:** enclose the cell in double quotes.
- **Other columns** (e.g. reviewer comments) are read as context but not assessed.
- **List-wide information:** give the domain and the version of the sources when you ask for the check, e.g. "Wpp (Kamerstuk 36 742, bijgewerkt t/m nr. 20), unless stated otherwise".

## What it produces
- `toetsing-<name>.json`: per term and per rule a verdict, finding and proposal, plus a combined proposal per term (definition, reference, examples, counterexamples, synonyms) and proposals for missing terms
- `rapport-<name>.md`: a report in table form, generated from the JSON, including the reference graph of the definitions before and after applying the proposals (cycles of any length, missing terms, levels from elementary at the bottom to composite at the top)
- on request: a layered `.drawio` file of the graph
- the format is described in [`toetsresultaat.md`](../skills/definitiekwaliteit/references/toetsresultaat.md)

## Rules
- [`regels-astra.csv`](../skills/definitiekwaliteit/references/regels-astra.csv): the ASTRA rules for definition quality ([astraonline.nl](https://www.astraonline.nl/index.php/Regels_voor_definitiekwaliteit)), unprefixed IDs
- [`regels-aanvullend.csv`](../skills/definitiekwaliteit/references/regels-aanvullend.csv): additional rules with prefix `KERN-` and their own numbering, so they stay stable when ASTRA changes. Sources include ISO 1087/704, the OOPS! pitfall catalogue and De Haan, Krouwel & Proper (2026), *Formal Definitions of Core Concepts in Enterprise Ontology*. Examples: references must be checked against the actual source text, examples and counterexamples must be congruent with the definition, and time-dependent concepts get a `[dag]` variable.
- [`toetsing.md`](../skills/definitiekwaliteit/references/toetsing.md): check question, signals and examples per rule

## Graph script (used by the skill)

The skill uses [`graaf.py`](../skills/definitiekwaliteit/scripts/graaf.py) to build the reference graph: which term's definition uses which other term. You do not need to run it yourself; the skill puts the results in the report. To run it standalone on a glossary in the format above:

```
python -I skills/definitiekwaliteit/scripts/graaf.py extract begrippenlijst.csv -o randen.csv
python -I skills/definitiekwaliteit/scripts/graaf.py analyse randen.csv --begrippen begrippenlijst.csv -o graaf.md
```

1. **`extract`** proposes the edges and writes them to `randen.csv`. Each edge has a type:
   - `genus`: the broader concept
   - `gebruikt`: a term used in the distinguishing part
   - `opsomming`: an element of an enumeration ("X or Y")
   - `zelf`: a self-reference

   Review `randen.csv` by hand before the next step.
2. **`analyse`** reports cycles of any length, self-references, terms that are used but not defined, and the levels (elementary at the bottom, composite at the top). The output is a Mermaid diagram.
   - Add `--drawio graaf.drawio` for a layered file that opens in draw.io.
   - Add `--alleen-genus` to show only the taxonomy.

No dependencies beyond the Python standard library.
