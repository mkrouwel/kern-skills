---
name: definitiekwaliteit
description: Toetst een begrippenlijst (termen met definities, referenties, voorbeelden) aan regels voor definitiekwaliteit, gebaseerd op de ASTRA-regels plus aanvullende regels uit ISO 1087/704 en Formal Concept Analysis. Geeft per begrip een oordeel per regel, stelt verbeterde definities, referenties, (tegen)voorbeelden, synoniemen en ontbrekende begrippen voor, en tekent de verwijzingsgraaf in Mermaid om kringen op te sporen. Gebruik dit bij een begrippenlijst, glossarium, woordenlijst of set definities die gecontroleerd, gereviewd of verbeterd moet worden, ook als de gebruiker het niet "toetsen" noemt (bijv. "kijk eens naar deze definities", "zijn deze begrippen goed gedefinieerd?").
---

# Definitiekwaliteit toetsen

Toets een begrippenlijst aan de regels in `references/`. Geef per begrip een oordeel per regel, en stel daarna verbeteringen voor. Herschrijf de lijst zelf niet zonder dat het gevraagd is: lever voorstellen.

## Regels

- `references/regels-astra.csv`: de ASTRA-regels voor definitiekwaliteit (bron: astraonline.nl). Inhoud ongewijzigd overgenomen; ids zonder prefix.
- `references/regels-aanvullend.csv`: aanvullende regels met prefix `KERN-` en eigen nummering, zodat wijzigingen in ASTRA ze niet raken. Kolom `Verhouding tot ASTRA` zegt wat de regel toevoegt. Kolom `Status` = `voorstel` betekent dat de regel nog niet is vastgesteld; vermeld dat in het rapport.
- Overlapt een KERN-regel na een ASTRA-update met een ASTRA-regel, laat dan de KERN-regel vervallen en leg dat vast in de omzettabel onderaan `toetsing.md`.
- `references/toetsing.md`: per regel de toetsvraag, signalen en voorbeelden. Lees dit voordat je toetst.
- `references/toetsresultaat.md`: het formaat van de JSON en van het rapport. Lees dit voordat je stap 3 begint.

`verplicht` maakt een schending een **fout**; `aanbevolen` maakt het een **aandachtspunt**.

## Werkwijze

### 1. Lijst inlezen
Invoer is een CSV (UTF-8, scheidingsteken `;` of `,`), een Markdown-tabel of een tabel in tekst, met één rij per begrip. Een Excel-bestand laat je de gebruiker als CSV exporteren. Kolomnamen zijn niet hoofdlettergevoelig; tussen haakjes staan toegestane varianten.

| Kolom | Verplicht | Inhoud |
|---|---|---|
| `term` (`begrip`) | ja | enkelvoud; contextkwalificatie tussen ronde haken aan het eind (`algemeen bestuur (wpp)`); variabelen tussen vierkante haken (`politieke vereniging op [dag]`) |
| `definitie` | ja | één zin, zonder lidwoord en zonder "is" |
| `acroniem` (`acro`, `afkorting`) | nee | afkorting(en) van de term |
| `synoniemen` (`synoniem`) | nee | andere termen voor hetzelfde begrip |
| `grondslag` (`bron`, `referentie`) | nee | bron en vindplaats, inclusief versie |
| `voorbeelden` (`voorbeeld(en)`) | nee | instanties; bij tijdsafhankelijke begrippen met de dag |
| `tegenvoorbeelden` (`tegenvoorbeeld(en)`) | nee | gevallen die er net buiten vallen |
| `toelichting` (`toelichting of opmerking`, `opmerkingen`) | nee | uitleg die niet in de definitie hoort |
| `context` (`domein`) | nee | context van de term, als die afwijkt van de lijst |

- **Meerdere waarden in één cel** worden gescheiden door `|`. Bij synoniemen en acroniemen mag ook een komma.
- **Andere kolommen** (bijv. opmerkingen van reviewers) lees je als context mee, maar toets je niet.
- **Lijstbrede gegevens** (domein, bronversie) geeft de gebruiker bij de vraag. Ontbreken ze, vraag er dan naar, of meld het als bevinding onder KERN-CON-02.

Vraag alleen door als term of definitie niet te herkennen is. Ontbreekt een optionele kolom, toets dan wat kan, en meld één keer voor de hele lijst welke regels daardoor `niet toetsbaar` zijn.

**Werkbestand voor stap 2:**
- Is de invoer een CSV in dit formaat, dan leest `graaf.py` die direct.
- Anders schrijf je de lijst als `begrippenlijst.csv` in de scratchpad, met ten minste `term;definitie`, plus `synoniemen` en `acroniem` als ze er zijn.

### 2. Verwijzingsgraaf opbouwen
Doe dit vóór het toetsen. De lijstregels (SAM-01 t/m SAM-08, KERN-SAM-01 t/m KERN-SAM-04, ESS-05, CON-01) hangen ervan af.

1. **Kandidaat-randen:** `python -I scripts/graaf.py extract begrippenlijst.csv -o randen.csv`. Het script:
   - zoekt in elke definitie naar andere termen en synoniemen, inclusief eenvoudige meervoudsvormen
   - herkent ook de *kern* van een term: zonder kwalificatie ("(wpp)") en zonder variabelen ("politieke vereniging op [dag]" → "politieke vereniging"), mits die kern uniek is
   - markeert de eerste treffer vooraan in de definitie als `genus`
   - markeert randen als `opsomming` als de definitie alleen uit termen met "of", "en/of", "dan wel" of komma's bestaat (extensionele definitie: geen genus)
   - meldt schendingen van KERN-STR-01: variabelen die niet in zowel term als definitie staan, of die geen term uit de lijst zijn
2. **Randen controleren:** lees `randen.csv` naast de definities en corrigeer het bestand.
   - Voeg toe wat het script mist: verbuigingen en afleidingen ("aangevraagd" → aanvraag, `soort` = `zelf` als het de eigen term is), en vaktermen die geen begrip in de lijst zijn (`doel` = de ontbrekende term).
   - Verwijder valse treffers: een woord dat in een andere betekenis gebruikt wordt.
   - Zet `soort` goed: `genus` alleen voor het bovenliggende begrip ("is een soort van"); `gebruikt` voor een begrip in het onderscheidende deel; `opsomming` voor de elementen van een extensionele definitie.
3. **Analyse:** `python -I scripts/graaf.py analyse randen.csv --begrippen begrippenlijst.csv -o graaf.md` (werkbestand in de scratchpad; de inhoud gaat naar `graaf.voor` in de JSON en naar het rapport). Dit levert:
   - zelfverwijzingen en alle kringen, ook van drie of meer stappen (SAM-05)
   - ontbrekende begrippen (KERN-SAM-02)
   - een indeling in **niveaus**: niveau 0 = elementair (verwijst naar geen ander begrip in de lijst), hoger = meer samengesteld
   - een Mermaid-diagram van boven (samengesteld) naar beneden (elementair). Kringen zijn rood, ontbrekende begrippen gestreept en elementaire begrippen groen.
   - alleen op verzoek, met `--drawio graaf.drawio`: een `.drawio`-bestand met vaste, gelaagde posities. Het opent direct in draw.io of in de VS Code-extensie Draw.io Integration. Begrippen, genus-pijlen en verwijzingspijlen staan op aparte lagen die je aan en uit kunt zetten.

   Geef `--begrippen` altijd mee; zonder die optie gelden begrippen zonder uitgaande randen als ontbrekend.

   **Layout:** de volgorde binnen een niveau wordt geoptimaliseerd op de genus-pijlen. De taxonomie is meestal een boom en dus zonder kruisingen te tekenen. Verwijzingen naar veelgebruikte begrippen kruisen onvermijdelijk. Met `--alleen-genus` toont het Mermaid-diagram alleen de taxonomie.

   **Genus vs. gebruikt:** bij een extensionele definitie ('X of Y') is er geen genus; `opsomming`- en `gebruikt`-randen worden gestippeld getekend en staan in draw.io op de laag *Gebruikte begrippen*.

Leid uit de randen ook af:
- de **hiërarchie**: begrippen met hetzelfde genus vormen een onderverdeling (KERN-SAM-03, KERN-SAM-04)
- **gekwalificeerde termen** ("hogesnelheidstrein") en hun hoofdterm ("trein") (SAM-01, SAM-02, SAM-04)

### 3. Toetsen
Toets **elk begrip aan elke regel** uit beide CSV's:
- regels op niveau **D** per definitie
- regels op niveau **L** met de graaf en hiërarchie uit stap 2
- regels op niveau **B** (bron nodig, zoals CON-02 en KERN-CON-03) door de bron daadwerkelijk te raadplegen; zie `toetsing.md`

Oordeel per regel: `voldoet`, `fout`, `aandachtspunt`, `twijfel`, `niet toetsbaar` of `n.v.t.` (bijv. INT-09 bij een intensionele definitie).
- Gebruik `twijfel` als het afhangt van domeinkennis die je niet hebt, en zeg welke kennis.
- Wees streng maar niet pedant: een woord als "geen" in een eigennaam is geen ontkenning (INT-08).

Leg elk oordeel vast in `toetsing-<naam>.json` (formaat: `references/toetsresultaat.md`). Geef bij elke schending, twijfel of niet-toetsbaar oordeel een bevinding en een voorstel. Regels die voor de hele lijst gelden (zoals KERN-CON-02) komen in `lijstbevindingen`.

### 4. Voorstellen per begrip
Vul per begrip het veld `voorstel` in de JSON: het samengevoegde voorstel dat alle bevindingen van dat begrip tegelijk oplost. Laat velden weg waar niets verandert.

- **Definitie:** één definitie die alle fouten en aandachtspunten tegelijk oplost. Volg de substitutiebenadering en genus + onderscheidend kenmerk.
- **Grondslag:** een correcte of preciezere vindplaats (CON-02, KERN-CON-01, KERN-CON-03).
  - Stel alleen een referentie voor die je zelf in de bron hebt gecontroleerd. Kon je dat niet, zet er dan `[te verifiëren]` achter.
  - Verzin nooit artikelnummers of paginanummers.
- **Voorbeelden:** 1–3 instanties van het juiste niveau (KERN-ESS-02) die aan de voorgestelde definitie voldoen. Bij tijdsafhankelijke begrippen met de dag erbij.
- **Tegenvoorbeelden:** 1–2 gevallen die er net buiten vallen: hetzelfde genus, maar één onderscheidend kenmerk niet. Noem bij elk welk kenmerk ontbreekt.
- **Synoniemen:** alleen als ze relevant zijn: gebruikt in de lijst of in de bron, of gangbaar in het domein. Geef aan welke term de voorkeursterm is (SAM-06, SAM-08).
- **Toelichting:** tekst die uit de definitie moet (INT-06), of die een keuze verantwoordt.

**Controleer je eigen voorstellen.**
- Toets ze opnieuw aan de regels.
- Bouw de graaf opnieuw met alle voorgestelde definities en aanvullende termen (stap 2 op een `begrippen-voorstel.csv`). Dat levert `graaf.na`.
- Ontstaat een nieuwe kring of een ontbrekend begrip, pas dan het voorstel aan.

### 5. Aanvullende termen
Stel begrippen voor die aan de lijst ontbreken, in `aanvullende_termen` in de JSON:
- **Ontbrekend:** vaktermen die in definities gebruikt worden maar niet gedefinieerd zijn (KERN-SAM-02, uit de graafanalyse).
- **Ontbrekend genus:** een bovenliggend begrip dat meerdere begrippen delen maar dat niet in de lijst staat.
- **Impliciet:** tegenhangers of zusterbegrippen die de definities veronderstellen (KERN-SAM-04), en het gemeenschappelijke genus van begrippen die nu los staan.

Geef per voorgestelde term een conceptdefinitie, het genus, de reden (welke definities hem nodig hebben) en de grondslag. Voeg de termen niet ongevraagd aan de lijst toe.

### 6. Rapport
Maak het rapport `rapport-<naam>.md` uit de JSON, volgens de opbouw in `references/toetsresultaat.md`:
- **Alles in tabellen.** Voorstellen staan alleen in tabellen, nooit nog eens in lopende tekst.
- **Tellingen uit de JSON.** Tel ze daaruit, zodat rapport en JSON niet uiteenlopen.
- **Graaf vóór en na.** Neem de graaf op van vóór en van na het toepassen van de voorstellen.

Lever op: `toetsing-<naam>.json` en `rapport-<naam>.md`.
- **Werkbestanden blijven in de scratchpad:** `begrippenlijst.csv` (als die nodig was), `randen.csv` en de uitvoer van `graaf.py analyse`.
- **Een `.drawio`-bestand** lever je alleen als de gebruiker erom vraagt.

## Uitgangspunten

- Definities volgen de **substitutiebenadering** (ASTRA): zonder lidwoord en zonder "is", zodat de definitie de term 1-op-1 kan vervangen. Bijvoorbeeld "fiets: vervoermiddel dat…".
- Een intensionele definitie = **genus + onderscheidende kenmerken**. Het genus is bij voorkeur zelf een gedefinieerd begrip in de lijst.
- **Tijdsafhankelijke begrippen** krijgen een variabele: "politieke vereniging op [dag]" (KERN-ESS-04). Welke dag geldt (peildatum, elke dag van een kalenderjaar), staat in de regel die het begrip gebruikt, niet in de definitie. Variabelen staan in term én definitie en zijn zelf een term of een B1-woord (KERN-STR-01). (Tegen)voorbeelden noemen de dag: "VVD — landelijke politieke vereniging op 1 januari 2026".
- Toelichting, voorbeelden en achtergrond horen in aparte velden, niet in de definitie.
- Taalniveau B1.
- Beoordeel de definitie zoals ze er staat. Vul geen ontbrekende kennis in die de lezer ook niet heeft (INT-10).
- Een referentie is pas `voldoet` als je de brontekst hebt gezien.
