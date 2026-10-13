---
name: yadm-facttypes
description: Haalt uit een of meer YADM-exports (DEMO Fact Model / Object Fact Diagram in JSON) alle feittypen - entiteittypen, attribuutsoorten (met waardetype), eigenschapsoorten en productsoorten - bundelt ze over de exports en zet ze in één tabel, met per entiteittype de afleiding (specialisatie, generalisatie, aggregatie) en in een volgorde van elementair naar afgeleid. Gebruik dit bij een JSON-export uit YADM met een feitenmodel en bij vragen als "zet de feittypen in een tabel", "welke entiteittypen/eigenschapsoorten staan in dit model", "bundel de fact models".
---

# Feittypen uit YADM-exports

Zet de Object Fact Diagrams uit een of meer YADM-exports om in één tabel met feittypen. Het script doet het mechanische werk; jij controleert de opmerkingen en presenteert de uitkomst.

## Werkwijze

1. **Draai het script** op alle exports die samen het feitenmodel vormen:

   ```
   python -I scripts/feittypen.py "<export>.json" [meer exports …]
   ```

   YADM deelt elementen (node-id's) tussen diagrammen. Geef daarom alle bij elkaar horende exports in één keer op; het script voegt ze samen.

2. **Presenteer de tabel** precies zoals het script die geeft:

   | Feittype | Soort | Waardetype | Afleiding | Bron |
   |---|---|---|---|---|
   | BANKREKENING | entiteittype | | | subsidie-FM-vereniging |
   | Rekeningnummer van [bankrekening] | attribuutsoort | IBAN | | subsidie-FM-vereniging |
   | JAAR* | entiteittype | | specialisatie van PERIODE | subsidie FM, subsidieberekening FM |
   | PG x {JAAR}* | entiteittype | | aggregatie van JAAR* × POLITIEKE GROEPERING* | subsidie FM |

   - **Feittype:** het entiteittype (hoofdletters), de attribuutsoort als `naam van [entiteittype]`, de eigenschapsoort met haar formulering, of de productsoort met formulering en `(PKnn)`.
   - **Soort:** entiteittype, attribuutsoort, eigenschapsoort of productsoort.
   - **Waardetype:** alleen bij attribuutsoorten.
   - **Afleiding:** alleen bij entiteittypen: `specialisatie van`, `generalisatie van` of `aggregatie van`, met verwijzing naar de betrokken entiteittypen.
   - Een `*` achter een entiteittype betekent dat het afgeleid is (specialisatie, generalisatie of aggregatie).
   - **Bron:** de export(s) waarin het feittype staat.

3. **Neem de opmerkingen van het script over** onder de tabel, kort samengevat:
   - **Naamconflicten:** hetzelfde element heet per export anders; de meest voorkomende naam is gebruikt. Vraag de gebruiker welke naam juist is.
   - **Specialisatie via productsoort:** een entiteittype rond een productsoort is opgenomen als specialisatie van het entiteittype waaraan de productsoort hangt.
   - **Kardinaliteit tegen de richting:** de lijn wijst naar een kant zonder 0..1 of 1..1.
   - **Gestippelde lijnen** zonder herkenbare afleiding, of naar een element buiten het eigen diagram (genegeerd).
   - **Zwevende lijnen:** lijnen met een eindpunt dat in geen enkele export voorkomt. Die staan niet in de tabel. Noem het aantal en de eigenschapsoorten die alleen zo voorkomen, en adviseer opruimen in de tool.
   - **Afhankelijkheidskring:** entiteittypen die niet te ordenen waren.

## Interpretatie van de export

| Element in de export | Betekenis |
|---|---|
| `entity_type` met kop `A` of zonder kop | entiteittype; naam = body (de betekenis van de markering `A` is onbekend en wordt genegeerd) |
| `entity_type` met andere kop, of `attribute` | entiteittype; kop = naam, bodyregels `naam {WAARDETYPE}` = attribuutsoorten |
| `set` (met plaatshouder `A` erin) | telt als het entiteittype dat erin staat |
| doorgetrokken edge met ruit (`markerMid`) | eigenschapsoort; formulering = middelste label. De bron van de lijn is de eigenaar; aan de doelkant hoort 0..1 of 1..1 |
| `production_event` (body = TK-nummer) met kind `text` | productsoort `PKnn`; tekst = formulering |
| edge tussen `production_event` en entiteittype | de productsoort hoort bij dat entiteittype |
| `production_event` binnen een entiteittype (`parentId`) | dat entiteittype is een specialisatie van het gelinkte entiteittype |
| gestippelde edge, handle-`derivation` `aggregation` / `generalisation` | aggregatie / generalisatie (doel = het afgeleide entiteittype) |
| gestippelde edge met gesloten pijl | specialisatie (bron = de specialisatie) |
| gestippelde edge zonder pijl naar een aggregaat of generalisatie | hoort bij die aggregatie of generalisatie |

Gestippelde edges tellen alleen als beide eindpunten in hetzelfde diagram staan; de namen uit dat diagram gelden dan.

## Volgorde

- Elementaire entiteittypen eerst, alfabetisch.
- Een entiteittype komt na de entiteittypen waarnaar zijn eigenschapsoorten verwijzen.
- Een specialisatie komt direct na haar ouder; een generalisatie of aggregatie na haar leden.
- Attribuut-, eigenschap- en productsoorten staan direct onder hun entiteittype (de eigenschapsoort onder de eigenaar).

## Uitgangspunten

- Toon de tabel in het gesprek. Schrijf hem alleen naar een bestand als de gebruiker daarom vraagt (`-o <bestand>.md`).
- Neem eigenschapsoorten waarvan een eindpunt ontbreekt nooit op in de tabel; meld ze alleen.
- Wijkt een export af (andere nodetypen, andere markeringen), pas dan het script aan in plaats van de tabel met de hand te corrigeren.
- Verander niets aan de export.
