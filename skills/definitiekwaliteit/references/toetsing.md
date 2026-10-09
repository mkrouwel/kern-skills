# Toetsing per regel

Per regel: de toetsvraag, signalen die op een schending wijzen, en een voorbeeld.

- Regels zonder prefix komen uit ASTRA (`regels-astra.csv`).
- Regels met prefix `KERN-` zijn aanvullingen (`regels-aanvullend.csv`). Ze hebben een eigen nummering, zodat wijzigingen in de ASTRA-set ze niet raken.

Niveau geeft aan waar de regel getoetst wordt:
- **D**: per definitie, los van de rest van de lijst
- **L**: over de hele lijst (vergelijken van definities)
- **B**: alleen met de bron erbij

## Context

### CON-01 Eigen definitie voor elke context — L
- **Toetsvraag:** Komt dezelfde term meer dan eens voor met betekenissen die niet te harmoniseren zijn, en is bij elk voorkomen de context vermeld?
- **Signalen:** dubbele term zonder contextkolom; één definitie die met "of" twee betekenissen afdekt; een gekwalificeerde term ("(wpp)") zonder de ongekwalificeerde tegenhanger.
- **Voorbeeld:** "zaak" (strafzaak) vs. "zaak" (roerend goed): twee definities, elk met de context erbij.

### CON-02 Baseren op authentieke bron — B
- **Toetsvraag:** Is er een authentieke bron (wet, basisregistratie, standaard) en is de definitie daarop gebaseerd?
- **Signalen:** geen bronvermelding; een eigen formulering terwijl een wettelijke definitie bestaat.
- Zonder brongegevens: geef als oordeel `niet toetsbaar` en noem welke bron voor de hand ligt.

### KERN-CON-01 Traceerbaar naar vindplaats — D/B
- **Toetsvraag:** Kun je de vindplaats (versie, artikel, lid, pagina, zin) van de definitie terugvinden?
- **Signalen:** alleen een documentnaam of hoofdstuk; bij een wetsvoorstel geen kamerstuknummer; helemaal geen bron.

### KERN-CON-02 Domein expliciet afgebakend — L
- **Toetsvraag:** Is benoemd voor welk domein of welke context de lijst, of deze definitie, geldt?
- Het volstaat als dit één keer voor de hele lijst is vastgelegd. Rapporteer het dan als één bevinding voor de lijst.

### KERN-CON-03 Referentie inhoudelijk correct — B
- **Toetsvraag:** Klopt de referentie *inhoudelijk*? Controleer drie dingen:
  1. **Bestaat** de bron, en bestaat de genoemde vindplaats (artikel, lid, pagina)?
  2. **Is het de geldende versie?** Is de wet, regeling of norm niet vervangen of vernummerd?
  3. **Ondersteunt** de tekst op die vindplaats de definitie? Dat kan letterlijk zijn, of een getrouwe afleiding. Een definitie die ruimer of enger is dan de bron, of een ander kenmerk bevat, voldoet niet.
- **Werkwijze:** lees de bron. Gebruik een meegeleverd bestand, of haal de bron op (bijv. wetten.overheid.nl voor wetgeving). Citeer in de bevinding de relevante brontekst, zodat de gebruiker het oordeel kan nagaan.
- **Baseer het oordeel alleen op letterlijke brontekst.** Een samenvattende fetch-tool kan wetsartikelen verkeerd citeren of verwisselen. Download bij wetgeving de volledige tekst (bijv. `https://wetten.overheid.nl/<BWBR-id>`) en haal het artikel er zelf uit. Lees een PDF (zoals een Kamerstuk) pagina voor pagina.
- **Let op de versie.** Bij wetsvoorstellen (Kamerstukken) verschillen de artikelnummers per versie (nr. 2, nota van wijziging, Stb.). Klopt een artikelnummer niet, ga dan na of een andere versie bedoeld is, en vraag om kamerstuk en nummer.
- **Definieert de bron de term wel?** Een wet kan een begrip beschrijven zonder de term te definiëren (bv. "kandidatenlijst waarboven geen aanduiding is geplaatst" in de Kieswet, zonder de term "blanco lijst"). Vermeld dat; het is geen fout.
- **Kun je de bron niet raadplegen?** Geef `niet toetsbaar` en zeg wat je wel kon vaststellen (bijv. "artikelnummer bestaat niet in de huidige versie van de wet"). Geef nooit `voldoet` op basis van alleen de plausibiliteit van de verwijzing.
- **Signalen:** verwijzing naar een vervallen wet; een artikelnummer zonder lid bij een artikel met meerdere leden; een bron die het begrip wel noemt maar niet definieert; een definitie die een kenmerk uit de bron mist of toevoegt.

## Essentie van het begrip

### ESS-01 Essentie, niet doel — D
- **Toetsvraag:** Zegt de definitie wat iets *is* of alleen waar het *voor dient*?
- **Signalen:** "om te…", "bedoeld voor…", "ten behoeve van…", "dient voor…" als kern van de definitie.
- **Fout:** "fiets: middel om je te verplaatsen". **Beter:** "fiets: vervoermiddel met twee wielen dat door spierkracht wordt voortbewogen".

### ESS-02 Type of instantie — D
- **Toetsvraag:** Is duidelijk of de term een soort aanduidt of één concreet exemplaar?
- **Signalen:** termen zoals "product", "regeling", "formulier" die zowel de soort als het exemplaar kunnen betekenen.

### ESS-03 Instanties uniek onderscheidbaar — D
- **Toetsvraag:** Kun je met deze definitie twee instanties van elkaar onderscheiden, en is duidelijk wat één instantie is?
- **Signalen:** er valt niet te tellen ("hoeveel X zijn er?" heeft geen antwoord); onduidelijk of iets per gebeurtenis of doorlopend bestaat (bv. een centraal stembureau per verkiezing of per vertegenwoordigend orgaan).

### ESS-04 Toetsbaarheid — D
- **Toetsvraag:** Kan van elk criterium in de definitie objectief worden vastgesteld of het geldt?
- **Signalen:** "voldoende", "redelijk", "belangrijk", "verantwoordelijk", "relevant", "in de regel".

### ESS-05 Voldoende onderscheidend — L
- **Toetsvraag:** Past de definitie ook op een ander begrip in de lijst of het domein?
- **Signalen:** twee definities die (bijna) inwisselbaar zijn; een definitie die alleen uit het genus bestaat.

### KERN-ESS-01 Geen tegenstrijdige kenmerken — D
- **Toetsvraag:** Sluiten kenmerken binnen de definitie elkaar uit?
- **Voorbeeld:** "(… TK/EP/PS …)" in een definitie waarvan het genus juist niet voor de TK geregistreerd is.
- Strijdigheid met het hoofdbegrip toets je onder SAM-02, met samenstellende begrippen onder SAM-04.

### KERN-ESS-02 Voorbeelden en tegenvoorbeelden congruent met definitie — D
- **Toetsvraag:**
  - Voldoet elk gegeven **voorbeeld** aan *alle* kenmerken van de definitie, inclusief die van het genus?
  - Schendt elk gegeven **tegenvoorbeeld** ten minste één kenmerk? Noem welk kenmerk. Een tegenvoorbeeld dat toch aan de definitie voldoet, wijst op een te ruime definitie of een fout tegenvoorbeeld.
  - Is het voorbeeld van het **juiste niveau**? Bij een type hoort een instantie, geen subtype (zie ESS-02), en geen aantal ("1 per gemeente"). "Personenauto" is een specialisatie van "voertuig", geen voorbeeld. "De auto met kenteken AB-123-C" is wel een voorbeeld.
- **Te ruim/te eng:** bedenk zelf een randgeval. Valt het onder de definitie terwijl dat niet de bedoeling lijkt (te ruim)? Of erbuiten terwijl het er duidelijk bij hoort (te eng)? Vermeld dat het randgeval van jou is.

### KERN-ESS-03 Voorbeeld en tegenvoorbeeld aanwezig — D
- **Toetsvraag:** Is er ten minste één voorbeeld? Is er een tegenvoorbeeld als het begrip nauw verwante begrippen heeft (siblings onder hetzelfde genus, of begrippen die in de praktijk verward worden)?
- Een goed tegenvoorbeeld valt er *net* buiten: het deelt het genus maar mist één onderscheidend kenmerk. "Een boom" is geen bruikbaar tegenvoorbeeld van "strafzaak"; "een civiele zaak" wel.
- Ontbreekt de kolom voor (tegen)voorbeelden in de hele lijst, maak dan één opmerking voor de lijst, maar stel per begrip wel voorbeelden voor (zie SKILL.md, stap 4).

### KERN-ESS-04 Tijdsafhankelijkheid via variabele — D/L
- **Toetsvraag:** Kan dezelfde instantie op de ene dag wel en op een andere dag niet onder het begrip vallen? Zo ja: bevatten term en definitie een variabele [dag]?
- **Signalen dat een begrip tijdsafhankelijk is:** registratie, inschrijving of lidmaatschap dat begint en eindigt; status die volgt uit een gebeurtenis ("na de verkiezing", "laatstgehouden"); "op moment", "betreffende", "dan", "huidig", "actief".
- **Signalen dat het tijdstip verkeerd zit:** een concreet moment of een concrete periode in de definitie ("in het subsidiejaar", "op de peildatum"). Dat hoort in de regel die het begrip gebruikt.
- **Granulariteit:** gebruik [dag]. Jaren en perioden maak je in de regels ("op elke dag van het kalenderjaar", "op de peildatum").
- **Voorbeeld:** "landelijke politieke vereniging op [dag]: politieke vereniging op [dag] waarvan de aanduiding is ingeschreven voor verkiezingen van de leden van de Tweede Kamer, de Eerste Kamer of het Europees Parlement".
- **Doorwerking:** (tegen)voorbeelden vermelden de dag ("VVD — LPV op 1 januari 2026"); disjunctheid (KERN-SAM-03) geldt per dag.

## Interne kwaliteit van de definitie

### INT-01 Compacte en begrijpelijke zin — D
- **Toetsvraag:** Is het één zin, op B1-niveau, zonder overbodige woorden?
- **Signalen:** meer dan één zin; meer dan ongeveer 30 woorden; veel bijzinnen; jargon.

### INT-02 Geen beslisregel — D
- **Toetsvraag:** Is de definitie geformuleerd als een regel of procedure?
- **Signalen:** "als… dan…", "indien", "voor zover", "moet", "mag", "wordt beschouwd als", stappen.

### INT-03 Voornaamwoord-verwijzing duidelijk — D
- **Toetsvraag:** Is van elk voornaamwoord (hij, zij, het, die, dat, deze, waarvan, ervan, hun) eenduidig waarnaar het verwijst?
- **Voorbeeld:** "openbaar lichaam met een grondgebied dat de bevoegdheid heeft" — "dat" kan op beide het-woorden slaan.

### INT-04 Lidwoord-verwijzing duidelijk — D
- **Toetsvraag:** Is bij elk "de"/"het" duidelijk welk specifiek ding bedoeld is?
- **Signalen:** "de aanvrager", "het besluit", "het betreffende …" zonder dat eerder in de definitie gezegd is welke.

### INT-06 Definitie bevat geen toelichting — D
- **Toetsvraag:** Staat er tekst in die niet nodig is om het begrip af te bakenen: voorbeelden, achtergrond, gebruik, uitzonderingen, wetsverwijzingen?
- **Signalen:** "bijvoorbeeld", "zoals", "meestal", "in de praktijk", tekst tussen haakjes, een tweede zin.
- Advies: verplaats de tekst naar een toelichtingsveld of de grondslag.

### INT-07 Alleen toegankelijke afkortingen — D/L
- **Toetsvraag:** Is elke afkorting uitgeschreven of elders in de lijst gedefinieerd? Heeft een afkorting in de lijst maar één betekenis?

### INT-08 Positieve formulering — D
- **Toetsvraag:** Bevat de definitie ontkenningen?
- **Signalen:** "niet", "geen", "zonder" (alleen als ontkenning), "behalve", "anders dan", "on-" als ontkenning.
- Een ontkenning die letterlijk uit de bron komt (bv. "geen leden kent", BW 2:285) is aanvaardbaar; vermeld dat.

### INT-09 Opsomming in extensionele definitie is limitatief — D
- **Toetsvraag:** Als de definitie een opsomming is: is die uitputtend?
- **Signalen:** "onder andere", "zoals", "bijvoorbeeld", "etc.", "en dergelijke", "…".

### INT-10 Geen ontoegankelijke achtergrondkennis nodig — D
- **Toetsvraag:** Leunt de definitie op interne documenten, werkinstructies of kennis die niet openbaar is?
- **Signalen:** "conform het interne beleid", "volgens werkinstructie X", "cf tabel uit wet".

### KERN-INT-01 Substitueerbaar — D
- **Toetsvraag:** Kun je de term in een zin vervangen door de definitie zonder dat de zin onjuist of ongrammaticaal wordt?
- **Signalen:** begint met "is", "een", "de", "het"; een andere woordsoort dan de term (bijvoorbeeld een werkwoord gedefinieerd met een zelfstandig naamwoord); eindigt met een punt.
- Enkelvoud toets je onder VER-02, starten met een naamwoord onder STR-01.

### KERN-INT-02 Geen restcategorie — D
- **Toetsvraag:** Beschrijft de definitie een restcategorie?
- **Signalen:** "overig", "alle andere", "anders dan de bovenstaande", "rest".
- Dubbelzinnige "en" of "of" toets je onder STR-08 en STR-09.

## Samenhang binnen het domein

### SAM-01 Kwalificatie leidt niet tot afwijking — L
- **Toetsvraag:** Is elk gekwalificeerd begrip ("hogesnelheidstrein") een echte specialisatie van het hoofdbegrip ("trein")? Alles wat onder het gekwalificeerde begrip valt, moet ook onder het hoofdbegrip vallen.
- Een contextkwalificatie ("algemeen bestuur (wpp)") is geen specialisatie maar een andere context: toets die onder CON-01.

### SAM-02 Kwalificatie omvat geen herhaling — L
- **Toetsvraag:** Noemt het gekwalificeerde begrip het hoofdbegrip als genus, en voegt het alleen de onderscheidende kenmerken toe?
- **Signalen:** kenmerken uit de definitie van het hoofdbegrip worden herhaald, of zijn in tegenspraak met het hoofdbegrip.

### SAM-03 Definitieteksten niet nesten — L
- **Toetsvraag:** Komt (een belangrijk deel van) de definitie van begrip A letterlijk of bijna letterlijk terug in de definitie van B?
- Advies: verwijs in B naar term A.

### SAM-04 Begrip-samenstelling strijdt niet met samenstellende begrippen — L
- **Toetsvraag:** Is de betekenis van een samengestelde term ("strafbaar feit") verenigbaar met de definities van de delen ("feit", en wat "strafbaar" betekent)?
- **Voorbeeld:** "centraal stembureau" is volgens de lijst geen soort "stembureau" — leg zo'n bewuste afwijking vast.

### SAM-05 Geen cirkeldefinities — D/L
- **Toetsvraag:**
  - Komt de term zelf, een afleiding of een synoniem ervan in de eigen definitie voor (zelfverwijzing)?
  - Zit er in de graaf "A gebruikt term B in zijn definitie" een kring, ook van drie of meer stappen?
- **Fout:** "aanvraag: verzoek dat wordt aangevraagd". **Toegestaan:** het genus in een samengestelde term ("strafzaak: zaak die…").
- **Werkwijze:** bouw de verwijzingsgraaf met `scripts/graaf.py` (zie SKILL.md, stap 2) en rapporteer elke kring met de volledige keten.
- Niet elke kring is even erg. Twee begrippen die elkaar alleen als "gebruikt begrip" noemen (aanvraag ↔ aanvrager) zijn vaak op te lossen door één kant te definiëren zonder de ander. Een kring via het genus is altijd een fout: dan is de hiërarchie circulair.

### SAM-06 Eén synoniem krijgt voorkeur — L
- **Toetsvraag:** Is bij synoniemen (in de lijst of in de synoniemkolom) aangegeven welke term de voorkeur heeft, en gebruiken de definities die voorkeursterm?
- **Signalen:** een definitie gebruikt een synoniem ("formele vereniging") in plaats van de voorkeursterm ("vereniging met volledige rechtsbevoegdheid").

### SAM-07 Geen betekenisverruiming binnen definitie — L
- **Toetsvraag:** Gebruikt een definitie een ander begrip uit de lijst in een ruimere betekenis dan diens eigen definitie?
- **Voorbeeld:** "telling" gedefinieerd als formeel vastgestelde inventarisatie, maar in "stembureau" gebruikt voor het tellen van stemmen.

### SAM-08 Synoniemen hebben één definitie — L
- **Toetsvraag:** Hebben twee termen in de lijst inhoudelijk dezelfde definitie? Zijn als synoniem opgegeven termen echt gelijkwaardig?
- Advies: één begrip met één definitie; de andere termen als synoniem. Een "synoniem" dat ruimer of enger is (bv. "overheidsorganisatie" bij "openbaar lichaam") is geen synoniem.

### KERN-SAM-01 Eén term, één begrip — L
- **Toetsvraag:** Staat een term binnen één context voor meer dan één begrip? Wordt een term in definities of toelichtingen in een andere betekenis gebruikt dan zijn eigen definitie?
- Verschillende betekenissen over contexten heen vallen onder CON-01; een gebruikt begrip dat wordt opgerekt onder SAM-07.

### KERN-SAM-02 Gebruikte begrippen gedefinieerd of vanzelfsprekend — L
- **Toetsvraag:** Is elk vakbegrip in een definitie zelf gedefinieerd, of algemeen bekend op B1-niveau?
- Rapporteer ontbrekende begrippen één keer, met de definities waarin ze voorkomen (uit `graaf.md`).

### KERN-SAM-03 Onderverdeling disjunct en volledig vastgelegd — L
- **Toetsvraag:** Als meerdere begrippen hetzelfde genus hebben: is vastgelegd of zij elkaar uitsluiten en of zij samen het genus dekken? Klopt dat met de definities?
- Bij tijdsafhankelijke begrippen geldt dit per moment.

### KERN-SAM-04 Geen impliciete begrippen — L
- **Toetsvraag:** Veronderstellen de definities een begrip dat geen term heeft, zoals een gemeenschappelijk genus van meerdere begrippen, of de tegenhanger van een gedefinieerde specialisatie?
- Dit is een advies, geen fout: stel een term voor en markeer die als voorstel.

## Structuur van de definitie

### STR-01 Definitie start met zelfstandig naamwoord — D
- **Toetsvraag:** Begint de definitie met een zelfstandig naamwoord of naamwoordgroep?
- **Signalen:** begint met een werkwoord, "op moment …", "wanneer", "als", "indien", "iets dat".
- Uitzondering: een werkwoord-term wordt gedefinieerd met een werkwoordgroep (zie VER-03).
- **Let op bij variabelen:** "politieke vereniging op [dag] waarvan …" begint met het naamwoord "politieke vereniging"; de variabele hoort bij die naamwoordgroep.

### KERN-STR-01 Variabelen gebonden en getypeerd — D
- **Toetsvraag:**
  - Komt elke variabele `[…]` uit de definitie ook in de term voor, en omgekeerd?
  - Is de naam van elke variabele een term uit de lijst ([vertegenwoordigend orgaan]) of een B1-woord ([dag])?
- **Fout:** term "laatstgehouden verkiezing op [dag]" met in de definitie "… van de leden van [orgaan] …": [orgaan] staat niet in de term.
- **Fout:** "[moment]" en "[dag]" door elkaar in samenhangende begrippen: kies één naam.
- Bij een gekwalificeerde term met variabele wordt de kwalificatie niet herhaald in de variabele.

### STR-02 Kick-off ≠ de term — D
- **Toetsvraag:** Begint de definitie met de te definiëren term zelf?
- **Fout:** "laatstgehouden verkiezing: laatstgehouden verkiezing van …". **Toegestaan:** het hoofdbegrip van een samengestelde term ("strafzaak: zaak die…").

### STR-03 Definitie ≠ synoniem — D
- **Toetsvraag:** Bestaat de definitie alleen uit een synoniem, een volledige naam of een uitgeschreven afkorting?
- **Fout:** "Autoriteit: Nederlandse autoriteit politieke partijen".

### STR-04 Kick-off vervolgen met toespitsing — D
- **Toetsvraag:** Begint de definitie met een bovenliggend begrip (genus), gevolgd door wat het begrip daarvan onderscheidt?
- **Signalen:** er ontbreekt een onderscheidend kenmerk; het genus slaat een niveau over (bv. "vereniging met volledige rechtsbevoegdheid …" waar "politieke vereniging" het naastbovenliggende begrip is).
- Een extensionele definitie (opsomming) is een toegestane uitzondering; dan geldt INT-09.

### STR-05 Definitie ≠ constructie — D
- **Toetsvraag:** Beschrijft de definitie waar het begrip uit is opgebouwd in plaats van wat het is?
- **Signalen:** "bestaat uit …", "samengesteld uit …" als kern van de definitie.
- Een samenstelling mag wel een onderscheidend kenmerk zijn ("orgaan dat is samengesteld uit vertegenwoordigers van …"), zolang het genus zegt wat het is.

### STR-06 Essentie ≠ informatiebehoefte — D
- **Toetsvraag:** Somt de definitie op welke gegevens we over het begrip willen vastleggen in plaats van wat het is?
- **Signalen:** "met naam, adres en …", "waarvan wordt geregistreerd …".

### STR-07 Geen dubbele ontkenning — D
- **Toetsvraag:** Bevat de definitie twee ontkenningen die elkaar (deels) opheffen?
- **Signalen:** "niet zonder", "geen … die niet", "niet ongebruikelijk".

### STR-08 Dubbelzinnige 'en' is verboden — D
- **Toetsvraag:** Is bij "en" duidelijk of beide kenmerken tegelijk moeten gelden, of dat het om twee groepen gaat?
- **Signalen:** "X en Y" waarbij zowel "X ∧ Y" als "X ∪ Y" gelezen kan worden; "en/of".

### STR-09 Dubbelzinnige 'of' is verboden — D
- **Toetsvraag:** Is bij "of" duidelijk of het inclusief of exclusief bedoeld is, en waar de opsomming bij hoort?
- **Signalen:** "X of Y met kenmerk Z" (slaat Z op Y of op beide?); "vereniging … of stichting met registratie".

## Verschijningsvorm

### VER-01 Term in enkelvoud — D
- **Toetsvraag:** Staat de term in het enkelvoud, tenzij het woord alleen als meervoud bestaat?
- **Voorbeeld:** "provinciale staten" bestaat alleen in het meervoud en is dus toegestaan.

### VER-02 Definitie in enkelvoud — D
- **Toetsvraag:** Is de definitie in het enkelvoud geformuleerd?
- **Signalen:** "personen die …", "organen die …" als kern van de definitie.

### VER-03 Werkwoord-term in infinitief — D
- **Toetsvraag:** Is een werkwoord als term in de infinitief (hele werkwoord) gezet?
- Alleen van toepassing op werkwoord-termen; anders `n.v.t.`.

## Oude nummering van de aanvullende regels

Rapporten van vóór oktober 2026 gebruiken de oude nummers. Omzetting:

| Oud | Nieuw | Toelichting |
|---|---|---|
| CON-03 | KERN-CON-01 | |
| CON-04 | KERN-CON-02 | |
| CON-05 | KERN-CON-03 | |
| ESS-06 | vervallen → STR-04 | genus + onderscheidend kenmerk zit in ASTRA STR-04 |
| ESS-07 | KERN-ESS-01 | ingeperkt tot strijdigheid binnen de definitie (rest: SAM-02, SAM-04) |
| ESS-08 | KERN-ESS-02 | |
| ESS-09 | KERN-ESS-03 | |
| INT-11 | vervallen → SAM-05, STR-02, STR-03 | zelfverwijzing valt onder ASTRA SAM-05 |
| INT-12 | KERN-INT-01 | enkelvoud-deel valt onder VER-02 |
| INT-13 | KERN-INT-02 | ingeperkt tot restcategorie; 'en/of' valt onder STR-08/STR-09 |
| SAM-05 (oud) | vervallen → SAM-05 (ASTRA) | zelfde inhoud, nu ASTRA-regel |
| SAM-06 (oud) | KERN-SAM-01 | |
| SAM-07 (oud) | vervallen → SAM-06, SAM-08 (ASTRA) | |
| SAM-08 (oud) | KERN-SAM-02 | |
| SAM-09 (oud) | KERN-SAM-03 | |
| SAM-10 (oud) | KERN-SAM-04 | |
