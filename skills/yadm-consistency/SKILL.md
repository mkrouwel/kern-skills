---
name: yadm-consistency
description: Controleert de consistentie tussen het Cooperation Structure Diagram (CM/CSD) en het feitenmodel (FM/OFD) in YADM-exports (DEMO-model, JSON) - transactiesoorten tegen productsoorten, variabelen in formuleringen, kardinaliteiten, waardetypen, interne en externe entiteittypen, naamgeving over diagrammen - en optioneel het feitenmodel tegen een begrippenlijst, ook inhoudelijk (specialisaties, generalisaties, aggregaties tegen genus en definities). Gebruik dit bij YADM-exports van een DEMO-model en vragen als "klopt het CM met het FM", "controleer het model", "zijn de feittypen consistent", "past het feitenmodel bij de begrippenlijst".
---

# Consistentie van een YADM-model

Controleert CM en FM tegen elkaar, en het FM tegen een begrippenlijst. Het script doet de mechanische controles; jij beoordeelt de bevindingen inhoudelijk en doet voorstellen.

Deze skill bouwt voort op drie andere skills, die in dezelfde skills-map moeten staan:

- **`yadm-tpt`** leest het CM: transactiesoorten, type O/I/D en informatielinks.
- **`yadm-facttypes`** leest het FM: entiteittypen, eigenschap-, attribuut- en productsoorten, afleidingen en het samenvoegen over diagrammen.
- **`definitiekwaliteit`** leest de begrippenlijst en bepaalt het genus en de opsommingen in de definities. Die skill is alleen nodig met `-b`.

## Werkwijze

1. **Draai het script** op alle exports die samen het model vormen: CM en alle FM-diagrammen in één keer. Voeg de begrippenlijst toe als die er is.

   ```
   python -I scripts/consistentie.py "<CM>.json" "<FM>.json" [meer exports …] [-b begrippen.csv]
   ```

   Het script herkent zelf welke export een CM en welke een FM is. Regels die het niet kan controleren (geen CM, geen FM of geen begrippenlijst), staan met "—" in de samenvatting.

2. **Presenteer de samenvatting** (aantal bevindingen per regel) en de tabel met bevindingen zoals het script die geeft.

3. **Groepeer de bevindingen per oorzaak.** Eén naamverschil kan bij meerdere regels opduiken. Voorbeeld: entiteittype SUBSIDIE-D met variabele `[subsidie]` geeft bevindingen bij CON-05 én CON-07. Noem per oorzaak de oplossing: aanpassen in het model, in de formulering of in de begrippenlijst.

4. **Beoordeel de BEG-bevindingen inhoudelijk.** Het script vergelijkt alleen namen; de inhoud weeg jij:
   - Lees bij elk BEG-02 t/m BEG-05 de betrokken definities in de begrippenlijst.
   - Bepaal of het model of de definitie moet veranderen. Een synoniem of een omschrijving van de ouder kan ook goed zijn. Een voorbeeld: het genus "vereniging" bij INFORMELE VERENIGING, terwijl het FM PRIVAATRECHTELIJK RECHTSPERSOON als ouder heeft. Dan kan VERENIGING een tussenliggend niveau in het FM zijn.
   - Stel bij een wijziging een nieuwe definitie voor volgens de regels van de skill `definitiekwaliteit`:
     - het genus is de ouder in het FM;
     - de differentia onderscheidt van de andere specialisaties;
     - bij een generalisatie: een opsomming van de leden;
     - bij een aggregatie: een verwijzing naar alle componenten.
   - Bij BEG-01: onderscheid een afwijkende schrijfwijze (alleen gelijktrekken) van een ontbrekend begrip (term en definitie voorstellen; het genus volgt uit het FM).
   - Bij BEG-06: geef aan welke begrippen een entiteittype zouden moeten zijn en welke terecht ontbreken, zoals rollen, attribuutwaarden of begrippen buiten de scope.

5. **Meld problemen in de invoer.** Een begrippenlijst met kapotte regels zie je doordat zinnen als "term" in BEG-06 verschijnen. Edges naar ontbrekende nodes en koppen met `A` (CON-15) zijn problemen in de tool en niet in het model; verwijs daarvoor naar de ontwikkelaar van YADM.

## Regels

| Regel | Ernst | Omschrijving | Hoe het script controleert |
|---|---|---|---|
| CON-01 | fout | Elke originele transactiesoort (O) in het CM heeft een productsoort in het FM | TK-nummer van elke O-transactiesoort komt als PK-nummer voor; transactiesoorten zonder nummer (`xx`) worden gemeld |
| CON-02 | fout | Elke productsoort hoort bij een originele transactiesoort in het CM | PK-nummer bestaat als TK in het CM, met type O |
| CON-03 | fout | Eén transactiesoort heeft één productsoort | per PK-nummer één formulering |
| CON-04 | fout | Een informatielink naar TKnn veronderstelt PKnn in het FM | informatielinks naar de bank van een transactiesoort |
| CON-05 | fout | Een productsoort hangt aan het entiteittype dat de variabele in de formulering is | naam van het gelinkte entiteittype = variabele; bij een aggregaat de componenten |
| CON-06 | waarschuwing | Productsoort: één variabele (bij een aggregaat de componenten), eindigt op "is/zijn <voltooid deelwoord>" | telling van `[…]` en de vorm van het einde |
| CON-07 | fout | Beide uiteinden van een eigenschapsoort zijn een variabele in de formulering | namen van bron en doel als `[…]` in de formulering; bij hetzelfde entiteittype aan beide kanten twee variabelen. Is de variabele een ouder of generalisatie, dan staat dat erbij |
| CON-08 | fout | Aan de doelkant (richting van de lijn) staat 0..1 of 1..1 | eindlabel van de lijn |
| CON-09 | waarschuwing | Aan de bronkant is de kardinaliteit ingevuld | beginlabel niet leeg of `...` |
| CON-10 | fout | Elke attribuutsoort heeft een waardetype | `{WAARDETYPE}` achter de attribuutsoort |
| CON-11 | fout | Een attribuutsoort komt per entiteittype één keer voor, overal met hetzelfde waardetype | binnen één blok en over de diagrammen |
| CON-12 | fout | Een entiteittype in focus (intern, wit) heeft minstens één productsoort | `data.focus` = `in`; een productsoort aan een entiteittype buiten focus mag wel. Ook gemeld als de focus per diagram verschilt |
| CON-13 | waarschuwing | Geen geïsoleerde entiteittypen | geen eigenschap-, attribuut- of productsoort en geen afleiding |
| CON-14 | fout | Een element heeft in alle diagrammen dezelfde naam | hetzelfde node-id met verschillende namen |
| CON-15 | waarschuwing | Geen edges naar ontbrekende nodes, geen kop `A` | per export; ook edges naar nodes die alleen in een andere export staan |
| BEG-01 | fout | Elk entiteittype heeft een begrip | naam = term, kern van de term (zonder kwalificatie) of synoniem; hoofdletters, spaties en streepjes tellen niet. Een afwijkende schrijfwijze wordt gemeld |
| BEG-02 | fout | Specialisatie: het genus van de definitie is de ouder in het FM | genus volgens `definitiekwaliteit` |
| BEG-03 | fout | Generalisatie: de definitie somt de leden op; een opsommende definitie is een generalisatie | opsomming volgens `definitiekwaliteit`, in beide richtingen |
| BEG-04 | fout | Aggregatie: de definitie verwijst naar alle componenten | alle termen in de definitie |
| BEG-05 | signaal | De definitie van de eigenaar van een eigenschapsoort verwijst naar het andere entiteittype | alle termen in de definitie |
| BEG-06 | signaal | Begrippen zonder entiteittype | begrippen die aan geen entiteittype gekoppeld zijn |

"Fout" is een overtreding van een modelleerregel. "Waarschuwing" is waarschijnlijk een fout of een slordigheid. "Signaal" vraagt om een inhoudelijke afweging.

## Uitgangspunten

- Toon het resultaat in het gesprek. Schrijf het alleen naar een bestand als de gebruiker daarom vraagt (`-o <bestand>.md`).
- Verander niets aan de exports of de begrippenlijst; lever voorstellen.
- Wijkt een export af van wat de zusterskills verwachten, pas dan het script van die skill aan, niet de uitkomst met de hand.
