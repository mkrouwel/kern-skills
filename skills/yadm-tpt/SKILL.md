---
name: yadm-tpt
description: Haalt uit een YADM-export (DEMO-model in JSON) de transactiesoorten, actorrollen en multiple transaction kinds (MTK's) met hun onderlinge links, en zet die in een tabel - per transactiesoort het type (origineel/informationeel/documenteel), de uitvoerende actorrol, welke transactiesoorten die rol initieert en welke MTK's en transactiesoorten die rol raadpleegt - plus een aparte MTK-lijst. Gebruik dit bij een JSON-export uit YADM of een andere React Flow-gebaseerde DEMO-tool met een Cooperation Structure Diagram (CSD), en bij vragen als "maak een TPT", "welke transactiesoorten/actorrollen staan in dit model", "zet het CSD in een tabel".
---

# Transactiesoorten en MTK's uit een YADM-export

Zet het Cooperation Structure Diagram (CSD) uit een YADM-export om in twee tabellen. Het script doet het mechanische werk; jij controleert de opmerkingen en presenteert de uitkomst.

## Werkwijze

1. **Draai het script** op de export(s):

   ```
   python -I scripts/tpt.py "<export>.json" [meer exports …]
   ```

   Exports zonder CSD-elementen (bijv. een Fact Model) meldt het script en slaat het over.

2. **Presenteer per export de twee tabellen** precies zoals het script ze geeft:

   **Transactiesoorten**

   | ID | Type | Uitvoerder | Initieert | Raadpleegt |
   |---|---|---|---|---|
   | TK24 | O | subsidieverlener | TK01, TK08, TK14 | MTK 15, MTK 19 |

   - **ID:** `TK` + het nummer uit het model. Een transactie zonder nummer heet `TKxx`; in de kolommen Initieert en Raadpleegt staat dan de uitvoerder of naam erbij, bijvoorbeeld `TKxx (boetebetaler)`.
   - **Type:** `O` (origineel, rood), `I` (informationeel, groen) of `D` (documenteel, blauw).
   - **Uitvoerder:** de actorrol in dezelfde transactor of self-activation.
   - **Initieert:** de transactiesoorten waarvoor deze actorrol initiator is. Bij self-activation staat de eigen transactie erbij met "(zelfactiverend)".
   - **Raadpleegt:** de informatielinks van de actorrol, als `MTK nn` (multiple transaction kind) of `TKnn` (de bank van een transactiesoort).

   **MTK's**

   | ID | Naam |
   |---|---|
   | 15 | KvK-gegevens |

3. **Neem de opmerkingen van het script over** onder de tabellen, kort samengevat:
   - **Aanname bij Type:** zonder expliciete kleur is het type O, omdat de standaardkleur van de tool rood is. Noem welke transactiesoorten het betreft, zodat de gebruiker het kan controleren.
   - **Initiatoren zonder eigen rij:** een samengestelde actorrol (omgeving) die een transactiesoort initieert, heeft geen eigen rij. Noem die.
   - **Nog geen nummer:** transactiesoorten en MTK's met "xx".
   - **Zwevende edges:** links naar elementen die niet in de export staan, meestal restanten van verwijderde elementen. Noem het aantal en adviseer opruimen in de tool. Neem ze niet op in de tabellen.
   - **Afbreekstreepjes:** namen waarin een afbreekstreepje aan het eind van een regel is verwerkt. Vraag de gebruiker de schrijfwijze te controleren als een keuze twijfelachtig is.

## Interpretatie van de export

De export is in React Flow-formaat (`nodes` en `edges`). Het script leest:

| Element in de export | Betekenis |
|---|---|
| `transactor` met kinderen `transaction` en `actor` (via `parentId`) | de actorrol is uitvoerder van de transactiesoort |
| `self_activation` met dezelfde kinderen | de actorrol is uitvoerder én initiator (zelfactiverend) |
| `composite` | samengestelde actorrol (vaak de omgeving) |
| `multiple_transaction_kind` | MTK; eerste regel = nummer, rest = naam |
| edge `solid` naar een `transaction` | initiatorlink |
| edge `dashed` tussen een `actor` en een `multiple_transaction_kind` of `transaction` | informatielink (raadplegen) |
| `transaction.data.color` | `green` = I, `blue` = D, `red`/`default`/geen = O |

Wijkt een export af (andere nodetypen, andere kleurwaarden, edges die het script niet interpreteert), dan meldt het script dat in de opmerkingen. Pas in dat geval het script aan in plaats van de tabel met de hand te corrigeren.

## Uitgangspunten

- Toon de tabellen in het gesprek. Schrijf ze alleen naar een bestand als de gebruiker daarom vraagt (`-o <bestand>.md`).
- Verzin geen namen van transactiesoorten: de export bevat alleen nummers. Een naam die de gebruiker opgeeft, mag je toevoegen.
- Verander niets aan de export.
