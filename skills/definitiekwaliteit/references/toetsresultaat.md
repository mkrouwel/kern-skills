# Toetsresultaat: JSON en rapport

De toetsing levert twee bestanden op:

1. `toetsing-<naam>.json` — de bron van waarheid: per begrip en per regel een oordeel, bevinding en voorstel.
2. `rapport-<naam>.md` — het rapport, volledig in tabellen, gemaakt uit de JSON.

Werkbestanden blijven in de scratchpad en worden niet meegeleverd: `begrippenlijst.csv` (als die nodig was), `randen.csv` en de uitvoer van `graaf.py analyse`. Een `.drawio`-bestand van de graaf lever je alleen mee als de gebruiker erom vraagt.

## JSON

```json
{
  "lijst": {
    "naam": "Begrippenlijst Wpp",
    "domein": "Wpp (Kamerstuk 36 742, bijgewerkt t/m nr. 20), tenzij anders vermeld",
    "datum": "2026-10-09",
    "bronnen_gecontroleerd": ["Wpp art. 1, 27, 54 …", "Kieswet E 15–E 20, G 1–G 3 …"],
    "bronnen_niet_gecontroleerd": ["Kieswet Q 6", "Kieswet I 17"]
  },
  "regelset": {
    "astra": "regels-astra.csv",
    "aanvullend": "regels-aanvullend.csv",
    "regels": ["CON-01", "CON-02", "…", "KERN-STR-01"]
  },
  "lijstbevindingen": [
    {
      "regel": "KERN-CON-02",
      "oordeel": "fout",
      "bevinding": "Het domein van de lijst is niet vastgelegd.",
      "voorstel": "Leg vast: 'Wpp (36 742, bijgewerkt t/m nr. 20), tenzij anders vermeld'."
    }
  ],
  "begrippen": [
    {
      "term": "centraal stembureau",
      "definitie": "orgaan verantwoordelijk voor uitvoering, controle en officiële vaststelling van de uitslag van een verkiezing",
      "grondslag": "Kieswet E15, G, H, I, P",
      "beoordelingen": {
        "CON-01": { "oordeel": "n.v.t." },
        "ESS-03": {
          "oordeel": "fout",
          "bevinding": "'van een verkiezing' maakt elke verkiezing een eigen instantie; volgens Kieswet E 15 is er één centraal stembureau per vertegenwoordigend orgaan.",
          "voorstel": "'voor de verkiezingen van de leden van één vertegenwoordigend orgaan'"
        },
        "KERN-CON-03": {
          "oordeel": "voldoet",
          "bevinding": "Kieswet E 15: 'Er is voor de verkiezing van elk vertegenwoordigend orgaan een centraal stembureau.'"
        }
      },
      "voorstel": {
        "definitie": "orgaan dat voor de verkiezingen van de leden van één vertegenwoordigend orgaan het register van aanduidingen bijhoudt en de verkiezingsuitslag vaststelt",
        "grondslag": "Kieswet E 15, E 16–E 20, G 1–G 3; hoofdstuk P [te verifiëren]",
        "voorbeelden": ["het centraal stembureau voor de verkiezing van de leden van de gemeenteraad van Utrecht"],
        "tegenvoorbeelden": ["het hoofdstembureau voor kieskring Utrecht (telt op, stelt geen uitslag vast)"],
        "synoniemen": ["CSB (acroniem)"],
        "toelichting": "Eén lichaam kan voor meerdere organen als centraal stembureau optreden (E 16: Kiesraad)."
      }
    }
  ],
  "aanvullende_termen": [
    {
      "term": "aanduiding",
      "definitie": "benaming waarmee een politieke groepering op de kandidatenlijst wordt vermeld",
      "genus": "benaming",
      "reden": "Gebruikt in blanco lijst, registratie en politieke vereniging (KERN-SAM-02).",
      "grondslag": "Kieswet G 1 lid 1"
    }
  ],
  "graaf": {
    "voor": { "kringen": ["verkiezing → vertegenwoordigend orgaan → verkiezing"], "zelfverwijzingen": ["kieskring"], "ontbrekend": ["orgaan"], "mermaid": "flowchart TB …" },
    "na":   { "kringen": [], "zelfverwijzingen": [], "ontbrekend": [], "mermaid": "flowchart TB …" }
  }
}
```

**Afspraken:**
- **Alle regels per begrip:** `beoordelingen` bevat elke regel uit `regelset.regels` voor elk begrip, ook `voldoet` en `n.v.t.`. Dan is te zien dat een regel getoetst is.
- **Toelichting alleen waar nodig:**
  - `bevinding` en `voorstel` mogen ontbreken bij `voldoet` en `n.v.t.`
  - bij `voldoet` op een bronregel (CON-02, KERN-CON-03) staat de geciteerde brontekst in `bevinding`
- **Waarden voor `oordeel`:** `voldoet`, `fout`, `aandachtspunt`, `twijfel`, `niet toetsbaar`, `n.v.t.` Een schending van een verplichte regel is `fout`, van een aanbevolen regel `aandachtspunt`.
- **Lijstbrede regels:** regels die voor de hele lijst gelden (bv. KERN-CON-02) staan in `lijstbevindingen`, en per begrip als `n.v.t.`
- **`voorstel` per begrip** is het samengevoegde voorstel dat alle bevindingen van dat begrip tegelijk oplost. Velden die niet veranderen laat je weg.
- **Niet zelf gecontroleerd:** markeer alles wat je niet in de bron hebt gecontroleerd met `[te verifiëren]`.
- **`graaf.voor` en `graaf.na`:** `voor` is de graaf van de huidige lijst. `na` is de graaf met alle voorgestelde definities en aanvullende termen. Mermaid-code als string.

## Rapport

Het rapport bestaat uit tabellen, met alleen korte koppen en zo nodig één inleidende zin per sectie. Schrijf geen voorstellen als lopende tekst: alles wat een voorstel is, staat in een tabel.

### 1. Samenvatting

| | |
|---|---|
| Begrippen | 44 |
| Regels | 50 (36 ASTRA, 14 KERN) |
| Fouten / aandachtspunten / twijfel / niet toetsbaar | 72 / 42 / 43 / 5 |
| Referenties (KERN-CON-03) kloppen / wijken af / twijfel / niet gecontroleerd | 22 / 11 / 5 / 5 |
| Kringen voor → na voorstellen | 4 → 0 |
| Ontbrekende begrippen voor → na | 9 → 0 |

Daaronder een tabel met de vaakst geschonden regels (Regel · Naam · Aantal · Voorbeeldbegrippen).

### 2. Bevindingen voor de hele lijst

| Regel | Oordeel | Bevinding | Voorstel |
|---|---|---|---|

### 3. Overzicht per begrip

Eén regel per begrip, gesorteerd op aantal fouten:

| Begrip | Fouten | Aandachtsp. | Twijfel | Niet toetsbaar |
|---|---|---|---|---|

### 4. Bevindingen per begrip

Per begrip een kop en één tabel met alle regels die niet `voldoet` of `n.v.t.` zijn:

| Regel | Oordeel | Bevinding | Voorstel |
|---|---|---|---|

Begrippen zonder bevindingen staan niet in deze sectie (zie het overzicht in §3).

### 5. Voorstellen per begrip

Eén tabel, één rij per begrip met een voorstel. Laat cellen leeg waar niets verandert.

| Begrip | Huidige definitie | Voorgestelde definitie | Grondslag | Voorbeelden | Tegenvoorbeelden | Synoniemen | Toelichting |
|---|---|---|---|---|---|---|---|

### 6. Aanvullende termen

| Term | Definitie | Genus | Reden | Grondslag |
|---|---|---|---|---|

### 7. Verwijzingsgraaf vóór en na

Een tabel met de kringen, zelfverwijzingen en ontbrekende begrippen, voor en na:

| | Vóór | Na |
|---|---|---|
| Kringen | verkiezing → vertegenwoordigend orgaan → verkiezing; … | — |
| Zelfverwijzingen | kieskring | — |
| Ontbrekende begrippen | orgaan, aanduiding, … | — |

Daaronder twee Mermaid-diagrammen: *Vóór* (huidige lijst) en *Na* (met voorstellen en aanvullende termen). Bij meer dan ongeveer 40 begrippen toon je van *Vóór* alleen het deel met kringen en ontbrekende begrippen, en van *Na* alleen de taxonomie (`--alleen-genus`).

### 8. Verantwoording

| Bronnen gecontroleerd | Bronnen niet gecontroleerd |
|---|---|
