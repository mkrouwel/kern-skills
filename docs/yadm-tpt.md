# `yadm-tpt` — transaction kinds and MTKs from a YADM export

Skill folder: [`skills/yadm-tpt`](../skills/yadm-tpt)

Reads a YADM export of a DEMO model (JSON) and turns its Cooperation Structure Diagram (CSD) into two tables. The skill and its output are in Dutch.

## Input

One or more JSON exports from YADM, in React Flow format (`nodes` and `edges`). If you also pass the fact model exports, the table gets the product kind of each transaction kind. This uses the script of [`yadm-facttypes`](yadm-facttypes.md), which must be installed in the same skills folder; without it the column is left out with a note. Exports without CSD or fact model elements are reported and skipped.

## What it produces

**Transaction kinds**

| ID | Type | Productsoort | Uitvoerder | Initieert | Raadpleegt |
|---|---|---|---|---|---|
| TK24 | O | [subsidie] is verleend | subsidieverlener | TK01, TK08, TK14 | MTK 15, MTK 19 |

- **ID:** `TK` + the number in the model; `TKxx` when the model has no number yet.
- **Type:** `O` original (red), `I` informational (green), `D` documental (blue).
- **Productsoort:** the formulation of product kind PKnn from the fact models passed in; empty if not found there. Only shown when a fact model is passed.
- **Uitvoerder:** the executing actor role.
- **Initieert:** the transaction kinds this actor role initiates; for a self-activating transaction kind, the kind itself is marked "(zelfactiverend)".
- **Raadpleegt:** the information links of the actor role, as `MTK nn` or `TKnn` (the bank of a transaction kind).

**MTKs**

| ID | Naam |
|---|---|
| 15 | KvK-gegevens |

**Notes:**
- **Assumptions:** a transaction kind without an explicit colour is taken as `O`.
- **Initiators without a row of their own,** such as a composite actor role in the environment.
- **Missing numbers:** transaction kinds and MTKs numbered "xx".
- **Dangling edges:** links to elements that are no longer in the export. They are left out of the tables.
- **Names with a line-break hyphen** that were joined.

## Script

```
python -I skills/yadm-tpt/scripts/tpt.py "<export>.json" [more exports …] [-o tables.md]
```

No dependencies beyond the Python standard library.

### How the export is read

| Element in the export | Meaning |
|---|---|
| `transactor` with children `transaction` and `actor` (via `parentId`) | the actor role executes the transaction kind |
| `self_activation` with the same children | the actor role executes and initiates (self-activating) |
| `composite` | composite actor role (often the environment) |
| `multiple_transaction_kind` | MTK; first line = number, rest = name |
| `solid` edge to a `transaction` | initiator link |
| `dashed` edge between an `actor` and a `multiple_transaction_kind` or `transaction` | information link |
| `transaction.data.color` | `green` = I, `blue` = D, `red` / `default` / none = O |

### Used by other skills

The function `lees()` in `tpt.py` returns the CSD as data, including initiators; [`yadm-consistency`](yadm-consistency.md) uses it. Keep its result stable when changing the script.
