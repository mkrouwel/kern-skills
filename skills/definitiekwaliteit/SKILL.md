---
name: definitiekwaliteit
description: Toetst een begrippenlijst (termen met definities, referenties, voorbeelden) aan regels voor definitiekwaliteit, gebaseerd op de ASTRA-regels plus aanvullende regels uit ISO 1087/704 en Formal Concept Analysis. Geeft per begrip een oordeel per regel, stelt verbeterde definities, referenties, (tegen)voorbeelden, synoniemen en ontbrekende begrippen voor, en tekent de verwijzingsgraaf in Mermaid om kringen op te sporen. Gebruik dit bij een begrippenlijst, glossarium, woordenlijst of set definities die gecontroleerd, gereviewd of verbeterd moet worden, ook als de gebruiker het niet "toetsen" noemt (bijv. "kijk eens naar deze definities", "zijn deze begrippen goed gedefinieerd?").
---

# Definitiekwaliteit toetsen

Toets een begrippenlijst aan de regels in `references/`. Geef per begrip een oordeel per regel, en stel daarna verbeteringen voor. Herschrijf de lijst zelf niet zonder dat het gevraagd is: lever voorstellen.

## Regels

- `references/regels-astra.csv`: de ASTRA-regels voor definitiekwaliteit (bron: astraonline.nl). Ongewijzigd overgenomen.
- `references/regels-aanvullend.csv`: aanvullende regels. Kolom `Status` = `voorstel` betekent dat de regel nog niet is vastgesteld; vermeld dat in het rapport.
- `references/toetsing.md`: per regel de toetsvraag, signalen en voorbeelden. Lees dit voordat je toetst.

`verplicht` maakt een schending een **fout**; `aanbevolen` maakt het een **aandachtspunt**.

## Werkwijze

### 1. Lijst inlezen
Herken per begrip: term, definitie, en (indien aanwezig) context/domein, toelichting, referentie (bron + vindplaats), voorbeelden, tegenvoorbeelden, synoniemen, bovenliggend begrip. Invoer kan CSV, Excel, Markdown, een tabel in tekst of een document zijn.

Vraag alleen door als term of definitie niet te herkennen is. Ontbreekt een kolom, toets dan wat kan, en meld één keer voor de hele lijst welke regels daardoor `niet toetsbaar` zijn.

Schrijf de lijst naar `begrippen.csv` in de scratchpad, met kolommen `term;definitie;synoniemen` (synoniemen gescheiden door `|`). Dit is de invoer voor stap 2.

### 2. Verwijzingsgraaf opbouwen
Doe dit vóór het toetsen. De lijstregels (SAM-01 t/m SAM-10, ESS-05, CON-01) hangen ervan af.

1. **Kandidaat-randen:** `python -I scripts/graaf.py extract begrippen.csv -o randen.csv`. Het script zoekt in elke definitie naar andere termen en synoniemen, inclusief eenvoudige meervoudsvormen. De eerste treffer vooraan in de definitie markeert het als `genus`.
2. **Randen controleren:** lees `randen.csv` naast de definities en corrigeer het bestand.
   - Voeg toe wat het script mist: verbuigingen en afleidingen ("aangevraagd" → aanvraag, `soort` = `zelf` als het de eigen term is), en vaktermen die geen begrip in de lijst zijn (`doel` = de ontbrekende term).
   - Verwijder valse treffers: een woord dat in een andere betekenis gebruikt wordt.
   - Zet `soort` goed: `genus` alleen voor het bovenliggende begrip.
3. **Analyse:** `python -I scripts/graaf.py analyse randen.csv --begrippen begrippen.csv -o graaf.md`. Dit levert:
   - zelfverwijzingen (INT-11)
   - alle kringen, ook van drie of meer stappen (SAM-05)
   - ontbrekende begrippen (SAM-08)
   - een Mermaid-diagram waarin kringen rood en ontbrekende begrippen gestreept zijn

   Geef `--begrippen` altijd mee; zonder die optie gelden begrippen zonder uitgaande randen als ontbrekend.

Leid uit de randen ook af:
- de **hiërarchie**: begrippen met hetzelfde genus vormen een onderverdeling (SAM-09, SAM-10)
- **gekwalificeerde termen** ("hogesnelheidstrein") en hun hoofdterm ("trein") (SAM-01, SAM-02, SAM-04)

### 3. Toetsen
Toets **elk begrip aan elke regel** uit beide CSV's:
- regels op niveau **D** per definitie
- regels op niveau **L** met de graaf en hiërarchie uit stap 2
- regels op niveau **B** (bron nodig, zoals CON-02 en CON-05) door de bron daadwerkelijk te raadplegen; zie `toetsing.md`

Oordeel per regel: `voldoet`, `fout`, `aandachtspunt`, `twijfel`, `niet toetsbaar` of `n.v.t.` (bijv. INT-09 bij een intensionele definitie). Gebruik `twijfel` als het afhangt van domeinkennis die je niet hebt, en zeg welke kennis. Wees streng maar niet pedant: een woord als "geen" in een eigennaam is geen ontkenning (INT-08).

Leg alle oordelen vast in `toetsmatrix.csv` (`;`-gescheiden): één rij per begrip, één kolom per regel-id, cellen met het oordeel. Lever dit bestand altijd mee.

### 4. Voorstellen per begrip
Stel per begrip voor wat nodig is. Laat een onderdeel weg als er niets te verbeteren is.

- **Aangepaste definitie:** één definitie die alle fouten en aandachtspunten tegelijk oplost. Volg de substitutiebenadering en genus + onderscheidend kenmerk.
- **Bijgewerkte referentie:** een correcte of preciezere vindplaats (CON-02, CON-03, CON-05). Stel alleen een referentie voor die je zelf in de bron hebt gecontroleerd. Kon je dat niet, zet er dan `[te verifiëren]` achter. Verzin nooit artikelnummers of paginanummers.
- **Aanvullende voorbeelden:** 1–3 instanties van het juiste niveau (ESS-08) die aan de (aangepaste) definitie voldoen. Kies er bij voorkeur een die het onderscheidende kenmerk zichtbaar maakt.
- **Tegenvoorbeelden:** 1–2 gevallen die er net buiten vallen: hetzelfde genus, maar één onderscheidend kenmerk niet. Noem bij elk welk kenmerk ontbreekt.
- **Synoniemen:** alleen als ze relevant zijn, d.w.z. in de lijst of in de bron gebruikt, of gangbaar in het domein. Geef aan welke term de voorkeursterm is (SAM-07). Noem ook termen die *geen* synoniem zijn maar vaak zo gebruikt worden, als verwarring dreigt.

Toets je eigen voorstellen opnieuw aan de regels. Een aangepaste definitie mag geen nieuwe kring veroorzaken: werk zo nodig `randen.csv` bij en draai de analyse opnieuw.

### 5. Aanvullende termen
Stel begrippen voor die aan de lijst ontbreken:
- **Ontbrekend:** vaktermen die in definities gebruikt worden maar niet gedefinieerd zijn (SAM-08, uit `graaf.md`).
- **Ontbrekend genus:** een bovenliggend begrip dat meerdere begrippen delen maar dat niet in de lijst staat.
- **Impliciet:** tegenhangers of zusterbegrippen die de definities veronderstellen (SAM-10), en het gemeenschappelijke genus van begrippen die nu los staan.

Geef per voorgestelde term een conceptdefinitie, de reden (welke definities hem nodig hebben), en het genus. Markeer alles als `voorstel`. Voeg de termen niet ongevraagd aan de lijst toe.

## Rapport

Lever het rapport in deze volgorde:

1. **Samenvatting:**
   - aantal begrippen, fouten en aandachtspunten
   - de 3–5 regels die het vaakst geschonden worden
   - structurele problemen (kringen, ontbrekende begrippen, synoniemen, referenties die niet kloppen)
2. **Verwijzingsgraaf:** het Mermaid-diagram uit `graaf.md`, de kringen met de volledige keten, en per kring een voorstel om hem te doorbreken. Bij meer dan ongeveer 40 begrippen: toon alleen het deel met kringen en ontbrekende begrippen, en lever het volledige diagram als bestand.
3. **Per begrip:**
   - **Oordelen:** alle regels, compact gegroepeerd, bijv. `voldoet: CON-01, ESS-01, …` · `n.v.t.: INT-09` · `niet toetsbaar: CON-02`.
   - Daaronder een tabel met alle regels die niet `voldoet` of `n.v.t.` zijn:

     | Regel | Oordeel | Bevinding | Voorstel |
     |---|---|---|---|

   - Daarna de voorstellen uit stap 4: aangepaste definitie, referentie, voorbeelden, tegenvoorbeelden, synoniemen.
4. **Aanvullende termen:** tabel met term, conceptdefinitie, genus en reden.
5. **Bestanden:** `toetsmatrix.csv`, `graaf.md`, en bij grote lijsten of op verzoek `bevindingen.csv` met kolommen `Term;Regel;Oordeel;Bevinding;Voorstel`.

## Uitgangspunten

- Definities volgen de **substitutiebenadering** (ASTRA): zonder lidwoord en zonder "is", zodat de definitie de term 1-op-1 kan vervangen. Bijvoorbeeld "fiets: vervoermiddel dat…".
- Een intensionele definitie = **genus + onderscheidende kenmerken**. Het genus is bij voorkeur zelf een gedefinieerd begrip in de lijst.
- Toelichting, voorbeelden en achtergrond horen in aparte velden, niet in de definitie.
- Taalniveau B1.
- Beoordeel de definitie zoals ze er staat. Vul geen ontbrekende kennis in die de lezer ook niet heeft (INT-10).
- Een referentie is pas `voldoet` als je de brontekst hebt gezien.
