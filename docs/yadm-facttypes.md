# `yadm-facttypes` — fact types from YADM exports

Skill folder: [`skills/yadm-facttypes`](../skills/yadm-facttypes)

Reads one or more YADM exports of a DEMO fact model (Object Fact Diagrams, JSON) and bundles all fact types into one table. The skill and its output are in Dutch.

## Input

One or more JSON exports from YADM, in React Flow format (`nodes` and `edges`). YADM shares elements between diagrams, so pass all exports that together form the fact model in one run; the script merges them. Exports without fact model elements are reported.

## What it produces

| Feittype | Soort | Waardetype | Afleiding | Bron |
|---|---|---|---|---|
| BANKREKENING | entiteittype | | | subsidie-FM-vereniging |
| Rekeningnummer van [bankrekening] | attribuutsoort | IBAN | | subsidie-FM-vereniging |
| PG x {JAAR}* | entiteittype | | aggregatie van JAAR* × POLITIEKE GROEPERING* | subsidie FM |

- **Feittype:** entity type, attribute type (`name van [entity type]`), property type (its formulation) or product kind (formulation plus `(PKnn)`).
- **Soort:** entiteittype, attribuutsoort, eigenschapsoort or productsoort.
- **Waardetype:** value type, for attribute types only.
- **Afleiding:** for entity types only: specialisation, generalisation or aggregation of other entity types. Derived entity types are marked with `*`.
- **Bron:** the export(s) the fact type appears in.

**Order:**
- Elementary entity types come first.
- An entity type comes after the entity types its property types refer to.
- A specialisation comes right after its parent.
- Generalisations and aggregations come after their members.
- Attribute types, property types and product kinds are listed under their entity type. A property type sits under its owner, the source of the line.

**Notes:**
- **Name conflicts:** the same element has a different name in different exports.
- **Specialisations derived from product kinds:** an entity type that surrounds a product kind is treated as a specialisation of the entity type the product kind is linked to.
- **Cardinality against the line direction:** the target side should be 0..1 or 1..1.
- **Dashed lines:** lines whose kind is unclear, or that go outside their own diagram.
- **Dangling lines:** lines with a missing end point. They are reported only, never included in the table.
- **Dependency cycles.**

## Script

```
python -I skills/yadm-facttypes/scripts/feittypen.py "<export>.json" [more exports …] [-o table.md]
```

No dependencies beyond the Python standard library.

### How the export is read

| Element in the export | Meaning |
|---|---|
| `entity_type` with header `A` or no header | entity type; name = body (the meaning of `A` is unknown and ignored) |
| `entity_type` with another header, or `attribute` | entity type; header = name, body lines `name {VALUETYPE}` = attribute types |
| `set` | counts as the entity type inside it |
| solid edge with a diamond (`markerMid`) | property type; formulation = middle label; source = owner |
| `production_event` (body = TK number) with a `text` child | product kind; text = formulation |
| edge between a `production_event` and an entity type | the product kind belongs to that entity type |
| dashed edge with handle `derivation` `aggregation` / `generalisation` | aggregation / generalisation |
| dashed edge with a closed arrow | specialisation |
| dashed edge without an arrow to an aggregate or generalisation | member of that aggregation or generalisation |
