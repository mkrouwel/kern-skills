# Toetsing per regel

Per regel: de toetsvraag, signalen die op een schending wijzen, en een voorbeeld. Regels met `(A)` komen uit ASTRA, regels met `(V)` zijn aanvullende voorstellen.

Niveau geeft aan waar de regel getoetst wordt:
- **D**: per definitie, los van de rest van de lijst
- **L**: over de hele lijst (vergelijken van definities)
- **B**: alleen met de bron erbij

## Context

### CON-01 Eigen definitie voor elke context (A) — L
- **Toetsvraag:** Komt dezelfde term meer dan eens voor met betekenissen die niet te harmoniseren zijn, en is bij elk voorkomen de context vermeld?
- **Signalen:** dubbele term zonder contextkolom; één definitie die met "of" twee betekenissen afdekt.
- **Voorbeeld:** "zaak" (strafzaak) vs. "zaak" (roerend goed): twee definities, elk met de context erbij.

### CON-02 Baseren op authentieke bron (A) — B
- **Toetsvraag:** Is er een authentieke bron (wet, basisregistratie, standaard) en volgt de definitie die?
- **Signalen:** geen bronvermelding; een eigen formulering terwijl een wettelijke definitie bestaat.
- Zonder brongegevens: geef als oordeel `niet toetsbaar` en noem welke bron voor de hand ligt.

### CON-03 Traceerbaar naar vindplaats (V) — D/B
- **Toetsvraag:** Kun je de vindplaats (artikel, pagina, zin) van de definitie terugvinden?
- **Signalen:** alleen een documentnaam, of helemaal geen bron.

### CON-04 Domein expliciet afgebakend (V) — L
- **Toetsvraag:** Is benoemd voor welk domein of welke context de lijst, of deze definitie, geldt?
- Het volstaat als dit één keer voor de hele lijst is vastgelegd.

### CON-05 Referentie inhoudelijk correct (V) — B
- **Toetsvraag:** Klopt de referentie *inhoudelijk*? Controleer drie dingen:
  1. **Bestaat** de bron, en bestaat de genoemde vindplaats (artikel, lid, pagina)?
  2. **Is het de geldende versie?** Is de wet, regeling of norm niet vervangen of vernummerd?
  3. **Ondersteunt** de tekst op die vindplaats de definitie? Dat kan letterlijk zijn, of een getrouwe afleiding. Een definitie die ruimer of enger is dan de bron, of een ander kenmerk bevat, voldoet niet.
- **Werkwijze:** lees de bron. Gebruik een meegeleverd bestand, of haal de bron op (bijv. wetten.overheid.nl voor wetgeving). Citeer in de bevinding de relevante brontekst, zodat de gebruiker het oordeel kan nagaan.
- **Baseer het oordeel alleen op letterlijke brontekst.** Een samenvattende fetch-tool kan wetsartikelen verkeerd citeren of verwisselen. Download bij wetgeving de volledige tekst (bijv. `https://wetten.overheid.nl/<BWBR-id>`) en haal het artikel er zelf uit. Lees een PDF (zoals een Kamerstuk) pagina voor pagina.
- **Let op de versie.** Bij wetsvoorstellen (Kamerstukken) verschillen de artikelnummers per versie (nr. 2, nota van wijziging, Stb.). Klopt een artikelnummer niet, ga dan na of een andere versie bedoeld is, en vraag om kamerstuk en nummer.
- **Kun je de bron niet raadplegen?** Geef `niet toetsbaar` en zeg wat je wel kon vaststellen (bijv. "artikelnummer bestaat niet in de huidige versie van de wet"). Geef nooit `voldoet` op basis van alleen de plausibiliteit van de verwijzing.
- **Signalen:** verwijzing naar een vervallen wet; een artikelnummer zonder lid bij een artikel met meerdere leden; een bron die het begrip wel noemt maar niet definieert; een definitie die een kenmerk uit de bron mist of toevoegt.

## Essentie van het begrip

### ESS-01 Essentie, niet doel (A) — D
- **Toetsvraag:** Zegt de definitie wat iets *is* of alleen waar het *voor dient*?
- **Signalen:** "om te…", "bedoeld voor…", "ten behoeve van…", "dient voor…" als kern van de definitie.
- **Fout:** "fiets: middel om je te verplaatsen". **Beter:** "fiets: vervoermiddel met twee wielen dat door spierkracht wordt voortbewogen".

### ESS-02 Type of instantie (A) — D
- **Toetsvraag:** Is duidelijk of de term een soort aanduidt of één concreet exemplaar?
- **Signalen:** termen zoals "product", "regeling", "formulier" die zowel de soort als het exemplaar kunnen betekenen.

### ESS-03 Instanties uniek onderscheidbaar (A) — D
- **Toetsvraag:** Kun je met deze definitie twee instanties van elkaar onderscheiden, en is duidelijk wat één instantie is?
- **Signalen:** er valt niet te tellen ("hoeveel X zijn er?" heeft geen antwoord).

### ESS-04 Toetsbaarheid (A) — D
- **Toetsvraag:** Kan van elk criterium in de definitie objectief worden vastgesteld of het geldt?
- **Signalen:** "voldoende", "redelijk", "belangrijk", "verantwoordelijk", "relevant", "in de regel".

### ESS-05 Voldoende onderscheidend (A) — L
- **Toetsvraag:** Past de definitie ook op een ander begrip in de lijst of het domein?
- **Signalen:** twee definities die (bijna) inwisselbaar zijn; een definitie die alleen uit het genus bestaat.

### ESS-06 Genus en onderscheidend kenmerk (V) — D
- **Toetsvraag:** Begint de definitie met een bovenliggend begrip, gevolgd door wat het begrip daarvan onderscheidt?
- **Signalen:** de definitie begint met "iets dat", "het geheel van", "wanneer", "als"; er ontbreekt een onderscheidend kenmerk.
- Een extensionele definitie (opsomming) is een toegestane uitzondering; dan geldt INT-09.

### ESS-07 Geen tegenstrijdige kenmerken (V) — D/L
- **Toetsvraag:** Sluiten kenmerken in de definitie, of kenmerken die via het genus geërfd worden, elkaar uit?
- **Voorbeeld:** genus "natuurlijk persoon" met als kenmerk "ingeschreven in het Handelsregister als rechtspersoon".

### ESS-08 Voorbeelden en tegenvoorbeelden congruent met definitie (V) — D
- **Toetsvraag:**
  - Voldoet elk gegeven **voorbeeld** aan *alle* kenmerken van de definitie, inclusief die van het genus?
  - Schendt elk gegeven **tegenvoorbeeld** ten minste één kenmerk? Noem welk kenmerk. Een tegenvoorbeeld dat toch aan de definitie voldoet, wijst op een te ruime definitie of een fout tegenvoorbeeld.
  - Is het voorbeeld van het **juiste niveau**? Bij een type hoort een instantie, geen subtype (zie ESS-02). "Personenauto" is een specialisatie van "voertuig", geen voorbeeld van een voertuig. "De auto met kenteken AB-123-C" is wel een voorbeeld.
- **Te ruim/te eng:** bedenk zelf een randgeval. Valt het onder de definitie terwijl dat niet de bedoeling lijkt (te ruim)? Of erbuiten terwijl het er duidelijk bij hoort (te eng)? Vermeld dat het randgeval van jou is.

### ESS-09 Voorbeeld en tegenvoorbeeld aanwezig (V) — D
- **Toetsvraag:** Is er ten minste één voorbeeld? Is er een tegenvoorbeeld als het begrip nauw verwante begrippen heeft (siblings onder hetzelfde genus, of begrippen die in de praktijk verward worden)?
- Een goed tegenvoorbeeld valt er *net* buiten: het deelt het genus maar mist één onderscheidend kenmerk. "Een boom" is geen bruikbaar tegenvoorbeeld van "strafzaak"; "een civiele zaak" wel.
- Ontbreekt de kolom voor (tegen)voorbeelden in de hele lijst, maak dan één opmerking voor de lijst, maar stel per begrip wel voorbeelden voor (zie SKILL.md, stap 4).

## Interne kwaliteit van de definitie

### INT-01 Compacte en begrijpelijke zin (A) — D
- **Toetsvraag:** Is het één zin, op B1-niveau, zonder overbodige woorden?
- **Signalen:** meer dan één zin; meer dan ongeveer 30 woorden; veel bijzinnen; jargon.

### INT-02 Geen beslisregel (A) — D
- **Toetsvraag:** Is de definitie geformuleerd als een regel of procedure?
- **Signalen:** "als… dan…", "indien", "moet", "mag", "wordt beschouwd als", stappen.

### INT-03 Voornaamwoord-verwijzing duidelijk (A) — D
- **Toetsvraag:** Is van elk voornaamwoord (hij, zij, het, die, dat, deze, waarvan, ervan, hun) eenduidig waarnaar het verwijst?

### INT-04 Lidwoord-verwijzing duidelijk (A) — D
- **Toetsvraag:** Is bij elk "de"/"het" duidelijk welk specifiek ding bedoeld is?
- **Signalen:** "de aanvrager", "het besluit" zonder dat eerder in de definitie gezegd is welke aanvrager of welk besluit.

### INT-06 Definitie bevat geen toelichting (A) — D
- **Toetsvraag:** Staat er tekst in die niet nodig is om het begrip af te bakenen: voorbeelden, achtergrond, gebruik, uitzonderingen?
- **Signalen:** "bijvoorbeeld", "zoals", "meestal", "in de praktijk", tekst tussen haakjes, een tweede zin.
- Advies: verplaats de tekst naar een toelichtingsveld.

### INT-07 Alleen toegankelijke afkortingen (A) — D/L
- **Toetsvraag:** Is elke afkorting uitgeschreven of elders in de lijst gedefinieerd?

### INT-08 Positieve formulering (A) — D
- **Toetsvraag:** Bevat de definitie ontkenningen?
- **Signalen:** "niet", "geen", "zonder" (alleen als ontkenning), "behalve", "anders dan", "on-" als ontkenning.

### INT-09 Opsomming in extensionele definitie is limitatief (A) — D
- **Toetsvraag:** Als de definitie een opsomming is: is die uitputtend?
- **Signalen:** "onder andere", "zoals", "bijvoorbeeld", "etc.", "en dergelijke", "…".

### INT-10 Geen ontoegankelijke achtergrondkennis nodig (A) — D
- **Toetsvraag:** Leunt de definitie op interne documenten, werkinstructies of kennis die niet openbaar is?
- **Signalen:** "conform het interne beleid", "volgens werkinstructie X", "zoals bij ons gebruikelijk".

### INT-11 Niet circulair (V) — D
- **Toetsvraag:** Komt de term zelf, een afleiding of een synoniem ervan in de definitie voor?
- **Fout:** "aanvraag: verzoek dat wordt aangevraagd". **Toegestaan:** het genus in een samengestelde term ("strafzaak: zaak die…").

### INT-12 Substitueerbaar (V) — D
- **Toetsvraag:** Kun je de term in een zin vervangen door de definitie zonder dat de zin onjuist of ongrammaticaal wordt?
- **Signalen:** begint met "is", "een", "de", "het"; een andere woordsoort dan de term (bijvoorbeeld een werkwoord gedefinieerd met een zelfstandig naamwoord); meervoud.

### INT-13 Eén begrip per definitie (V) — D
- **Toetsvraag:** Beschrijft de definitie meer dan één begrip, of een restcategorie?
- **Signalen:** "en/of", "X of Y" als genus, "overig", "alle andere", "anders dan de bovenstaande".

## Samenhang binnen het domein

### SAM-01 Kwalificatie leidt niet tot afwijking (A) — L
- **Toetsvraag:** Is elk gekwalificeerd begrip ("hogesnelheidstrein") een echte specialisatie van het hoofdbegrip ("trein")? Alles wat onder het gekwalificeerde begrip valt, moet ook onder het hoofdbegrip vallen.

### SAM-02 Kwalificatie omvat geen herhaling (A) — L
- **Toetsvraag:** Noemt het gekwalificeerde begrip het hoofdbegrip als genus, en voegt het alleen de onderscheidende kenmerken toe?
- **Signalen:** kenmerken uit de definitie van het hoofdbegrip worden herhaald, of zijn in tegenspraak met het hoofdbegrip.

### SAM-03 Definitieteksten niet nesten (A) — L
- **Toetsvraag:** Komt (een belangrijk deel van) de definitie van begrip A letterlijk of bijna letterlijk terug in de definitie van B?
- Advies: verwijs in B naar term A.

### SAM-04 Begrip-samenstelling strijdt niet met samenstellende begrippen (A) — L
- **Toetsvraag:** Is de betekenis van een samengestelde term ("strafbaar feit") verenigbaar met de definities van de delen ("feit", en wat "strafbaar" betekent)?

### SAM-05 Geen definitiekringen (V) — L
- **Toetsvraag:** Zit er in de graaf "A gebruikt term B in zijn definitie" een kring?
- Werkwijze: bouw de verwijzingsgraaf met `scripts/graaf.py` (zie SKILL.md, stap 2) en rapporteer elke kring met de volledige keten. Het script vindt ook kringen van drie of meer stappen.
- Niet elke kring is even erg. Twee begrippen die elkaar alleen als "gebruikt begrip" noemen (aanvraag ↔ aanvrager) zijn vaak op te lossen door één kant te definiëren zonder de ander. Een kring via het genus is altijd een fout: dan is de hiërarchie circulair.

### SAM-06 Eén term, één begrip (V) — L
- **Toetsvraag:** Wordt een term in de lijst (in definities of toelichtingen) in een andere betekenis gebruikt dan zijn eigen definitie?
- Een term die over contexten heen verschillende betekenissen heeft, valt onder CON-01.

### SAM-07 Eén begrip, één voorkeursterm (V) — L
- **Toetsvraag:** Hebben twee termen in de lijst inhoudelijk dezelfde definitie?
- Advies: kies één voorkeursterm, leg de andere vast als synoniem.

### SAM-08 Gebruikte begrippen gedefinieerd of vanzelfsprekend (V) — L
- **Toetsvraag:** Is elk vakbegrip in een definitie zelf gedefinieerd, of algemeen bekend op B1-niveau?
- Rapporteer ontbrekende begrippen één keer, met de definities waarin ze voorkomen.

### SAM-09 Onderverdeling disjunct en volledig vastgelegd (V) — L
- **Toetsvraag:** Als meerdere begrippen hetzelfde genus hebben: is vastgelegd of zij elkaar uitsluiten en of zij samen het genus dekken? Klopt dat met de definities?

### SAM-10 Geen impliciete begrippen (V) — L
- **Toetsvraag:** Veronderstellen de definities een begrip dat geen term heeft, zoals een gemeenschappelijk genus van meerdere begrippen, of de tegenhanger van een gedefinieerde specialisatie?
- Dit is een advies, geen fout: stel een term voor en markeer die als voorstel.
