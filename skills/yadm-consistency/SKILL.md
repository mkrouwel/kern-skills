---
name: yadm-consistency
description: Controleert de consistentie tussen het Cooperation Structure Diagram (CM/CSD) en het feitenmodel (FM/OFD) in YADM-exports (DEMO-model, JSON) - transactiesoorten tegen productsoorten, variabelen in formuleringen, kardinaliteiten, waardetypen, interne en externe entiteittypen, naamgeving over diagrammen - en optioneel het feitenmodel tegen een begrippenlijst, ook inhoudelijk (specialisaties, generalisaties, aggregaties tegen genus en definities). Gebruik dit bij YADM-exports van een DEMO-model en vragen als "klopt het CM met het FM", "controleer het model", "zijn de feittypen consistent", "past het feitenmodel bij de begrippenlijst".
---

# Consistentie van een YADM-model

Controleert CM en FM tegen elkaar, en het FM tegen een begrippenlijst. Het script doet de mechanische controles; jij beoordeelt de bevindingen inhoudelijk en doet voorstellen.

Deze skill bouwt voort op drie andere skills, die in dezelfde skills-map moeten staan:

- **`yadm-tpt`** leest het CM: transactiesoorten, type O/I/D, initiatoren en informatielinks.
- **`yadm-facttypes`** leest het FM: entiteittypen, eigenschap-, attribuut- en productsoorten, afleidingen en het samenvoegen over diagrammen.
- **`definitiekwaliteit`** leest de begrippenlijst en bepaalt het genus en de opsommingen in de definities. Die skill is alleen nodig met `-b`.

## Werkwijze

1. **Draai het script** op alle exports die samen het model vormen: CM en alle FM-diagrammen in één keer. Voeg de begrippenlijst toe als die er is.

   ```
   python -I scripts/consistentie.py "<CM>.json" "<FM>.json" [meer exports …] [-b begrippen.csv]
   ```

   Het script herkent zelf welke export een CM en welke een FM is. Regels die het niet kan controleren (geen CM, geen FM of geen begrippenlijst), staan met "—" in de samenvatting.

2. **Presenteer de samenvatting** (aantal bevindingen per regel) en de tabel met bevindingen zoals het script die geeft.

3. **Groepeer de bevindingen per oorzaak.** Eén naamverschil kan bij meerdere regels opduiken. Voorbeeld: entiteittype SUBSIDIE-D met variabele `[subsidie]` geeft bevindingen bij KERN-C-PK01 én KERN-C-ES01. Noem per oorzaak de oplossing: aanpassen in het model, in de formulering of in de begrippenlijst.

4. **Beoordeel de BG-bevindingen inhoudelijk.** Het script vergelijkt alleen namen; de inhoud weeg jij:
   - Lees bij elk BG02 t/m BG05 de betrokken definities in de begrippenlijst.
   - Bepaal of het model of de definitie moet veranderen. Een synoniem of een omschrijving van de ouder kan ook goed zijn. Een voorbeeld: het genus "vereniging" bij INFORMELE VERENIGING, terwijl het FM PRIVAATRECHTELIJK RECHTSPERSOON als ouder heeft. Dan kan VERENIGING een tussenliggend niveau in het FM zijn.
   - Stel bij een wijziging een nieuwe definitie voor volgens de regels van de skill `definitiekwaliteit`:
     - het genus is de ouder in het FM;
     - de differentia onderscheidt van de andere specialisaties;
     - bij een generalisatie: een opsomming van de leden;
     - bij een aggregatie: een verwijzing naar alle componenten.
   - Bij BG01: onderscheid een afwijkende schrijfwijze (alleen gelijktrekken) van een ontbrekend begrip (term en definitie voorstellen; het genus volgt uit het FM).
   - Bij BG06: geef aan welke begrippen een entiteittype zouden moeten zijn en welke terecht ontbreken, zoals rollen, attribuutwaarden of begrippen buiten de scope.

5. **Meld problemen in de invoer.** Een begrippenlijst met kapotte regels zie je doordat zinnen als "term" in BG06 verschijnen. Edges naar ontbrekende nodes en koppen met `A` (TL01, TL02) zijn problemen in de tool en niet in het model; verwijs daarvoor naar de ontwikkelaar van YADM.

## Regels

De regels staan in `references/regels.csv`, met kolommen `Id`, `Categorie`, `Ernst`, `Regel` en `Controle`. De laatste kolom zegt hoe het script de regel controleert. Lees dit bestand voordat je de bevindingen beoordeelt.

De id's hebben de vorm `KERN-C-<categorie><volgnummer>`. `C` staat voor consistentie; de skill `definitiekwaliteit` gebruikt `KERN-D-`, zodat id's over de skills uniek zijn. De categorieën:

| Code | Categorie |
|---|---|
| CM | coöperatiemodel (alleen CM) |
| TK | transactiesoort en productsoort (CM tegen FM) |
| PK | productsoort |
| ES | eigenschapsoort |
| AS | attribuutsoort |
| ET | entiteittype |
| NM | naamgeving over diagrammen |
| TL | export (tool) |
| BG | begrippenlijst |

Ernst: "fout" is een overtreding van een modelleerregel. "Waarschuwing" is waarschijnlijk een fout of een slordigheid. "Signaal" vraagt om een inhoudelijke afweging.

Een nieuwe regel komt in de CSV met een nieuw volgnummer binnen zijn categorie. Een bestaand id krijgt nooit een andere betekenis. De controle zelf staat in `scripts/consistentie.py`; het script stopt met een melding als het een id gebruikt dat niet in de CSV staat.

## Uitgangspunten

- Toon het resultaat in het gesprek. Schrijf het alleen naar een bestand als de gebruiker daarom vraagt (`-o <bestand>.md`).
- Verander niets aan de exports of de begrippenlijst; lever voorstellen.
- Wijkt een export af van wat de zusterskills verwachten, pas dan het script van die skill aan, niet de uitkomst met de hand.
