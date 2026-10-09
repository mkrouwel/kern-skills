"""Verwijzingsgraaf van definities: randen extraheren, kringen zoeken, Mermaid tekenen.

Twee stappen:

  python graaf.py extract begrippen.csv -o randen.csv
      Zoekt per definitie welke andere termen (en synoniemen) erin voorkomen en
      schrijft kandidaat-randen. Dit is een heuristiek: controleer en corrigeer
      randen.csv daarna handmatig (verbuigingen, valse treffers, genus, ontbrekende
      begrippen toevoegen).

  python graaf.py analyse randen.csv [--begrippen begrippen.csv] -o graaf.md
      Zoekt alle kringen (ook langer dan twee stappen) en schrijft een rapport
      met een Mermaid-diagram.

begrippen.csv: de begrippenlijst zelf (formaat: zie README). Gebruikt worden
'term' en 'definitie', en voor het herkennen van termen ook 'synoniemen' en
'acroniem' (meerdere waarden gescheiden door '|'). Andere kolommen worden
genegeerd. Scheidingsteken ';' of ',' wordt automatisch herkend.

randen.csv: kolommen 'bron;doel;soort;fragment'. soort is 'genus', 'gebruikt',
'opsomming' (element van een extensionele definitie 'X of Y'; geen genus) of
'zelf' (de term staat in zijn eigen definitie). Een doel dat geen begrip in de
lijst is, wordt als ontbrekend begrip getekend.

Termen mogen variabelen bevatten, bijvoorbeeld 'politieke vereniging op [dag]'.
De kern ('politieke vereniging') wordt dan in definities herkend; de variabele
zelf ('dag') wordt herkend als hij als begrip in de lijst staat.
"""

import argparse
import csv
import re
import sys
from collections import defaultdict

KLINKERS = "aeiou"
MAX_KRINGEN = 500


def lees_csv(pad):
    with open(pad, newline="", encoding="utf-8-sig") as f:
        tekst = f.read()
    try:
        dialect = csv.Sniffer().sniff(tekst.splitlines()[0], delimiters=";,\t")
    except csv.Error:
        dialect = csv.excel
    rijen = list(csv.DictReader(tekst.splitlines(), dialect=dialect))
    # extra velden (rij met meer velden dan kolommen) komen onder sleutel None als lijst; negeren
    return [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k is not None} for r in rijen]


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


# kolomnamen van de begrippenlijst (kleine letters) met toegestane varianten
KOLOMMEN = {
    "term": ["term", "begrip"],
    "definitie": ["definitie"],
    "synoniemen": ["synoniemen", "synoniem"],
    "acroniem": ["acroniem", "acro", "afkorting"],
}


def veld(rij, naam):
    for k in KOLOMMEN[naam]:
        if rij.get(k):
            return rij[k]
    return ""


def meerdere(waarde):
    """Meerdere waarden in één cel, gescheiden door '|' (of ',')."""
    return [w.strip() for w in re.split(r"[|,]", waarde) if w.strip()]


def lees_begrippen(pad):
    """Begrippenlijst inlezen; alleen term, definitie en synoniemen (incl. acroniemen) zijn nodig."""
    rijen = lees_csv(pad)
    if not rijen or not any(k in rijen[0] for k in KOLOMMEN["term"]) or "definitie" not in rijen[0]:
        sys.exit(f"{pad} moet ten minste de kolommen 'term' en 'definitie' hebben")
    uit = []
    for r in rijen:
        term = veld(r, "term")
        if term:
            uit.append({"term": term, "definitie": veld(r, "definitie"),
                        "synoniemen": meerdere(veld(r, "synoniemen")) + meerdere(veld(r, "acroniem"))})
    return uit


def varianten(term):
    """Term plus eenvoudige Nederlandse meervouds- en genitiefvormen van het laatste woord."""
    woorden = norm(term).split(" ")
    w = woorden[-1]
    vormen = {w, w + "s", w + "'s", w + "n", w + "en"}
    if len(w) > 2 and w[-1] not in KLINKERS:
        vormen.add(w + w[-1] + "en")  # bus -> bussen
    if len(w) > 3 and w[-2] == w[-3] and w[-2] in KLINKERS and w[-1] not in KLINKERS:
        vormen.add(w[:-2] + w[-1] + "en")  # zaak -> zaken
    if w.endswith("f"):
        vormen.add(w[:-1] + "ven")  # bedrijf -> bedrijven
    if w.endswith("s"):
        vormen.add(w[:-1] + "zen")  # huis -> huizen
    return {" ".join(woorden[:-1] + [v]) for v in vormen}


VERBINDINGSWOORDEN = {"op", "van", "t.o.v.", "per", "in", "bij", "voor", "tijdens", "met"}
SCHEIDERS = {"of", "en/of", "dan", "wel", "en"}


def kern(term):
    """Term zonder kwalificatie tussen haakjes en zonder variabelen [..] (met hun verbindingswoorden)."""
    t = re.sub(r"\s*\([^)]*\)\s*$", "", term)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    woorden = t.split()
    while woorden and woorden[-1].lower() in VERBINDINGSWOORDEN:
        woorden.pop()
    return " ".join(woorden).strip()


def is_opsomming(definitie, bezet, n_treffers):
    """Extensionele definitie: alleen termen, gescheiden door 'of', 'en/of', 'dan wel' of komma's.

    Variabelen [..] en verbindingswoorden tussen de termen worden genegeerd.
    """
    if n_treffers < 2:
        return False
    rest = "".join(" " if bezet[i] else c for i, c in enumerate(definitie))
    rest = re.sub(r"\[[^\]]*\]", " ", rest).strip().rstrip(".")
    woorden = re.findall(r"[\w/.]+", rest.replace(",", " , "))
    if not any(w in ("of", "en/of", "dan") for w in woorden):
        return False
    return all(w in SCHEIDERS | VERBINDINGSWOORDEN or w == "," for w in woorden)


def extract(args):
    begrippen = lees_begrippen(args.begrippen)

    # (vorm, term) gesorteerd op lengte: langste treffer wint ("strafbaar feit" voor "feit").
    # Daarnaast de kern van de term, als die uniek is:
    # - zonder kwalificatie tussen haakjes: "landelijke politieke partij (op moment)"
    #   (niet bij "openbaar lichaam (gw)" naast "openbaar lichaam (wpp)")
    # - zonder variabelen en de verbindingswoorden ervoor: "laatstgehouden verkiezing van
    #   [vertegenwoordigend orgaan] op [dag]" -> "laatstgehouden verkiezing"
    kale_telling = defaultdict(int)
    for b in begrippen:
        kale_telling[norm(kern(b["term"]))] += 1

    vormen = []
    for b in begrippen:
        namen = [b["term"]] + b["synoniemen"]
        k = kern(b["term"])
        if norm(k) != norm(b["term"]) and kale_telling[norm(k)] == 1:
            namen.append(k)
        for naam in namen:
            for v in varianten(naam):
                vormen.append((v, b["term"]))
    vormen.sort(key=lambda x: -len(x[0]))

    randen = []
    for b in begrippen:
        definitie = norm(b["definitie"])
        bezet = [False] * len(definitie)
        treffers = []
        for vorm, doel in vormen:
            for m in re.finditer(r"(?<!\w)" + re.escape(vorm) + r"(?!\w)", definitie):
                if any(bezet[m.start():m.end()]):
                    continue
                bezet[m.start():m.end()] = [True] * (m.end() - m.start())
                treffers.append((m.start(), doel, m.group(0)))
        treffers.sort()
        opsomming = is_opsomming(definitie, bezet, len(treffers))
        gezien = set()
        for i, (pos, doel, fragment) in enumerate(treffers):
            if doel in gezien:
                continue
            gezien.add(doel)
            if norm(doel) == norm(b["term"]):
                soort = "zelf"
            elif opsomming:
                soort = "opsomming"  # extensionele definitie: geen genus
            elif i == 0 and len(definitie[:pos].split()) <= 2:
                soort = "genus"  # eerste treffer vooraan in de definitie
            else:
                soort = "gebruikt"
            randen.append({"bron": b["term"], "doel": doel, "soort": soort, "fragment": fragment})

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["bron", "doel", "soort", "fragment"], delimiter=";")
        w.writeheader()
        w.writerows(randen)
    print(f"{len(randen)} kandidaat-randen voor {len(begrippen)} begrippen geschreven naar {args.output}")

    # KERN-STR-01: variabelen gebonden (in term én definitie) en getypeerd (term uit de lijst)
    var = lambda s: {norm(v) for v in re.findall(r"\[([^\]]+)\]", s)}
    bekend = {norm(b["term"]) for b in begrippen} | {norm(kern(b["term"])) for b in begrippen}
    for b in begrippen:
        vt, vd = var(b["term"]), var(b["definitie"])
        if vt != vd:
            print(f"KERN-STR-01: '{b['term']}': variabelen in term {sorted(vt)} ≠ in definitie {sorted(vd)}")
        for v in sorted((vt | vd) - bekend):
            print(f"KERN-STR-01 (controleer): '{b['term']}': variabele [{v}] is geen term uit de lijst (B1-woord?)")
    print("Controleer de randen handmatig voordat je 'analyse' draait.")


def sterke_componenten(knopen, buren):
    """Tarjan: lijst van sterk samenhangende componenten."""
    index, laag, op_stapel, stapel, comps = {}, {}, set(), [], []
    teller = [0]

    def bezoek(v):
        index[v] = laag[v] = teller[0]
        teller[0] += 1
        stapel.append(v)
        op_stapel.add(v)
        for w in buren[v]:
            if w not in index:
                bezoek(w)
                laag[v] = min(laag[v], laag[w])
            elif w in op_stapel:
                laag[v] = min(laag[v], index[w])
        if laag[v] == index[v]:
            comp = []
            while True:
                w = stapel.pop()
                op_stapel.discard(w)
                comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    sys.setrecursionlimit(max(1000, 10 * len(knopen)))
    for v in knopen:
        if v not in index:
            bezoek(v)
    return comps


def kringen(comp, buren):
    """Alle elementaire kringen binnen één component (elke kring één keer)."""
    volgorde = {v: i for i, v in enumerate(sorted(comp))}
    gevonden = []
    for start in sorted(comp):
        pad = [start]

        def dfs(v):
            if len(gevonden) >= MAX_KRINGEN:
                return
            for w in buren[v]:
                if w not in volgorde or volgorde[w] < volgorde[start]:
                    continue
                if w == start:
                    if len(pad) > 1:  # zelfverwijzingen worden apart gerapporteerd
                        gevonden.append(pad + [start])
                elif w not in pad:
                    pad.append(w)
                    dfs(w)
                    pad.pop()

        dfs(start)
    return gevonden


def mermaid_label(s):
    return s.replace('"', "#quot;")


def gelaagde_ordening(knopen, randen, comp_van, ordening=None):
    """Gelaagde (Sugiyama-achtige) ordening.

    Niveau 0 = elementaire begrippen (verwijzen nergens naar); een begrip staat één niveau
    boven het hoogste begrip waarnaar het verwijst. Begrippen in dezelfde kring krijgen
    hetzelfde niveau. Randen over meer niveaus krijgen hulpknopen; de volgorde binnen een
    niveau wordt met de barycentermethode gekozen om kruisende lijnen te beperken.

    `ordening`: deelverzameling randen waarop de volgorde wordt geoptimaliseerd (bv. alleen genus);
    de niveaus worden altijd op alle randen berekend, zodat elke pijl naar beneden wijst.

    Geeft (niveau per knoop, lagen van boven naar beneden, hulppunten per rand, kruisingen).
    """
    # niveaus op de condensatie (kringen samengevoegd)
    comp_buren = defaultdict(set)
    for b, d in randen:
        if comp_van[b] != comp_van[d]:
            comp_buren[comp_van[b]].add(comp_van[d])
    comp_niveau = {}

    def niveau_van(c):
        if c not in comp_niveau:
            comp_niveau[c] = 0
            comp_niveau[c] = 1 + max((niveau_van(d) for d in comp_buren[c]), default=-1)
        return comp_niveau[c]

    niveau = {v: niveau_van(comp_van[v]) for v in knopen}
    hoogste = max(niveau.values(), default=0)

    # hulpknopen voor randen over meer dan één niveau
    lagen = defaultdict(list)
    for v in knopen:
        lagen[niveau[v]].append(v)
    boven = defaultdict(list)   # knoop -> knopen één niveau hoger die ernaar wijzen
    onder = defaultdict(list)   # knoop -> knopen één niveau lager
    keten = {}
    for (b, d) in (randen if ordening is None else ordening):
        if b == d or niveau[b] == niveau[d]:
            continue
        hoog, laag = (b, d) if niveau[b] > niveau[d] else (d, b)
        vorige = hoog
        hulp = []
        for n in range(niveau[hoog] - 1, niveau[laag], -1):
            h = ("hulp", b, d, n)
            lagen[n].append(h)
            hulp.append(h)
            onder[vorige].append(h)
            boven[h].append(vorige)
            vorige = h
        onder[vorige].append(laag)
        boven[laag].append(vorige)
        keten[(b, d)] = hulp

    volgorde = [sorted(lagen[n], key=str) for n in range(hoogste, -1, -1)]  # bovenste laag eerst

    def kruisingen(lg):
        totaal = 0
        for i in range(len(lg) - 1):
            pos = {v: k for k, v in enumerate(lg[i + 1])}
            lijnen = [(a, pos[w]) for a, v in enumerate(lg[i]) for w in onder[v] if w in pos]
            for x in range(len(lijnen)):
                for y in range(x + 1, len(lijnen)):
                    if (lijnen[x][0] - lijnen[y][0]) * (lijnen[x][1] - lijnen[y][1]) < 0:
                        totaal += 1
        return totaal

    def sorteer(laag, ref, buren_van):
        pos = {v: k for k, v in enumerate(ref)}
        def sleutel(v):
            p = [pos[w] for w in buren_van[v] if w in pos]
            return sum(p) / len(p) if p else laag.index(v)
        return sorted(laag, key=sleutel)

    def kruis_rond(lg, i):
        """Kruisingen tussen laag i en de lagen erboven en eronder."""
        deel = lg[max(0, i - 1):i + 2]
        return kruisingen(deel)

    def transponeer(lg):
        """Wissel buren binnen een laag zolang dat kruisingen vermindert."""
        verbeterd = True
        while verbeterd:
            verbeterd = False
            for i in range(len(lg)):
                for j in range(len(lg[i]) - 1):
                    voor = kruis_rond(lg, i)
                    lg[i][j], lg[i][j + 1] = lg[i][j + 1], lg[i][j]
                    if kruis_rond(lg, i) < voor:
                        verbeterd = True
                    else:
                        lg[i][j], lg[i][j + 1] = lg[i][j + 1], lg[i][j]

    beste, beste_k = [list(l) for l in volgorde], kruisingen(volgorde)
    for _ in range(12):
        for i in range(1, len(volgorde)):                      # van boven naar beneden
            volgorde[i] = sorteer(volgorde[i], volgorde[i - 1], boven)
        for i in range(len(volgorde) - 2, -1, -1):             # van beneden naar boven
            volgorde[i] = sorteer(volgorde[i], volgorde[i + 1], onder)
        k = kruisingen(volgorde)
        if k < beste_k:
            beste, beste_k = [list(l) for l in volgorde], k
    transponeer(beste)
    return niveau, beste, keten, kruisingen(beste)


def xml_esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def schrijf_drawio(pad, niveau, lagen, keten, uniek, in_kring, ontbrekend, kring_rand):
    """Schrijft een .drawio-bestand (mxGraph-XML) met vaste posities: direct te openen in draw.io."""
    breedte = lambda t: max(110, 7 * len(t) + 24)
    hoogte, dx, dy = 40, 30, 110
    laagbreedte = [sum(breedte(v) if isinstance(v, str) else 20 for v in l) + dx * (len(l) - 1) for l in lagen]
    max_b = max(laagbreedte, default=0)
    pos = {}
    for i, l in enumerate(lagen):
        x = 140 + (max_b - laagbreedte[i]) / 2
        for v in l:
            w = breedte(v) if isinstance(v, str) else 20
            pos[v] = (x, 40 + i * dy, w)
            x += w + dx

    # lagen in draw.io (Beeld > Lagen): begrippen, genus-pijlen en verwijzingspijlen apart aan/uit te zetten
    cellen = ['<mxCell id="0"/>', '<mxCell id="1" value="Begrippen" parent="0"/>',
              '<mxCell id="lg" value="Genus (bovenliggend begrip)" parent="0"/>',
              '<mxCell id="lv" value="Gebruikte begrippen" parent="0"/>']
    hoogste = len(lagen) - 1
    for i in range(len(lagen)):
        cellen.append(f'<mxCell id="niv{i}" value="niveau {hoogste - i}" style="text;html=1;align=left;'
                      f'fontColor=#999999;fontSize=11;" vertex="1" parent="1"><mxGeometry x="10" y="{40 + i * dy + 10}" '
                      f'width="80" height="20" as="geometry"/></mxCell>')
    ids = {}
    for n, v in enumerate(v for l in lagen for v in l if isinstance(v, str)):
        ids[v] = f"n{n}"
        x, y, w = pos[v]
        if v in ontbrekend:
            stijl = "fillColor=#f4f4f4;strokeColor=#888888;dashed=1;fontColor=#555555;"
        elif v in in_kring:
            stijl = "fillColor=#fde2e2;strokeColor=#c0392b;strokeWidth=2;"
        elif niveau[v] == 0:
            stijl = "fillColor=#eef5ee;strokeColor=#5b8a5b;"
        else:
            stijl = "fillColor=#ffffff;strokeColor=#333333;"
        cellen.append(f'<mxCell id="{ids[v]}" value="{xml_esc(v)}" style="rounded=1;whiteSpace=wrap;html=1;{stijl}" '
                      f'vertex="1" parent="1"><mxGeometry x="{x:.0f}" y="{y}" width="{w}" height="{hoogte}" as="geometry"/></mxCell>')
    for n, ((b, d), soort) in enumerate(sorted(uniek.items())):
        if soort == "genus":
            stijl = "strokeColor=#333333;strokeWidth=1.5;"
        else:
            stijl = "strokeColor=#999999;dashed=1;"
        if kring_rand(b, d):
            stijl = "strokeColor=#c0392b;strokeWidth=2;" + ("dashed=1;" if soort != "genus" else "")
        punten = ""
        if keten.get((b, d)):
            pts = "".join(f'<mxPoint x="{pos[h][0] + 10:.0f}" y="{pos[h][1] + hoogte / 2:.0f}"/>' for h in keten[(b, d)])
            punten = f'<Array as="points">{pts}</Array>'
        lus = "edgeStyle=orthogonalEdgeStyle;" if b == d else "edgeStyle=none;"
        laag = "lg" if soort in ("genus", "zelf") else "lv"
        cellen.append(f'<mxCell id="e{n}" style="{lus}rounded=1;html=1;endArrow=block;endSize=6;{stijl}" edge="1" parent="{laag}" '
                      f'source="{ids[b]}" target="{ids[d]}"><mxGeometry relative="1" as="geometry">{punten}</mxGeometry></mxCell>')
    # legenda
    ly = 40 + len(lagen) * dy
    legenda = ("<b>Legenda</b><br>doorgetrokken pijl = genus (bovenliggend begrip)<br>gestippelde pijl = gebruikt begrip"
               "<br>rood = onderdeel van een kring<br>groen = elementair begrip (niveau 0)<br>gestreepte rand = ontbreekt in de lijst")
    cellen.append(f'<mxCell id="legenda" value="{xml_esc(legenda)}" style="text;html=1;align=left;verticalAlign=top;'
                  f'fontSize=11;" vertex="1" parent="1"><mxGeometry x="10" y="{ly}" width="320" height="100" as="geometry"/></mxCell>')
    xml = ('<mxfile host="graaf.py"><diagram name="Verwijzingsgraaf"><mxGraphModel grid="0" page="0">'
           f'<root>{"".join(cellen)}</root></mxGraphModel></diagram></mxfile>')
    with open(pad, "w", encoding="utf-8") as f:
        f.write(xml)


def analyse(args):
    randen = lees_csv(args.randen)
    begrippen = {r["term"] for r in lees_begrippen(args.begrippen)} if args.begrippen else {r["bron"] for r in randen}

    # dubbele randen samenvoegen; 'genus' en 'zelf' gaan voor 'gebruikt'
    rang = {"zelf": 0, "genus": 1, "gebruikt": 2}
    uniek = {}
    for r in randen:
        sleutel = (r["bron"], r["doel"])
        soort = r.get("soort") or "gebruikt"
        if sleutel not in uniek or rang.get(soort, 2) < rang.get(uniek[sleutel], 2):
            uniek[sleutel] = soort

    knopen = sorted(begrippen | {d for _, d in uniek} | {b for b, _ in uniek})
    buren = defaultdict(list)
    for (b, d) in uniek:
        buren[b].append(d)

    comps = sterke_componenten(knopen, buren)
    comp_van = {v: i for i, c in enumerate(comps) for v in c}
    zelf = sorted(b for (b, d) in uniek if b == d)
    alle_kringen = []
    for c in comps:
        if len(c) > 1:
            alle_kringen.extend(kringen(c, buren))
    in_kring = {v for c in comps if len(c) > 1 for v in c} | set(zelf)
    ontbrekend = sorted(set(knopen) - begrippen)

    uit = []
    uit.append("# Verwijzingsgraaf\n")
    uit.append(f"- Begrippen: {len(begrippen)}; randen: {len(uniek)}")
    uit.append(f"- Zelfverwijzingen (SAM-05): {len(zelf)}")
    uit.append(f"- Kringen over meerdere begrippen (SAM-05): {len(alle_kringen)}"
               + (f" (afgekapt op {MAX_KRINGEN})" if len(alle_kringen) >= MAX_KRINGEN else ""))
    uit.append(f"- Ontbrekende begrippen (KERN-SAM-02): {len(ontbrekend)}\n")

    if zelf:
        uit.append("## Zelfverwijzingen\n")
        uit += [f"- {t}" for t in zelf]
        uit.append("")
    if alle_kringen:
        uit.append("## Kringen\n")
        for k in sorted(alle_kringen, key=len):
            uit.append(f"- ({len(k) - 1} stappen) " + " → ".join(k))
        uit.append("")
    if ontbrekend:
        uit.append("## Ontbrekende begrippen\n")
        verwijzers = defaultdict(list)
        for (b, d) in uniek:
            if d in ontbrekend:
                verwijzers[d].append(b)
        uit += [f"- {t} (gebruikt in: {', '.join(sorted(verwijzers[t]))})" for t in ontbrekend]
        uit.append("")

    kring_rand = lambda b, d: b == d or (comp_van[b] == comp_van[d] and len(comps[comp_van[b]]) > 1)
    genus_randen = [e for e, s in uniek.items() if s == "genus"]
    niveau, lagen, keten, n_kruis = gelaagde_ordening(knopen, list(uniek), comp_van, ordening=genus_randen or None)
    elementair = sorted(v for v in knopen if niveau[v] == 0 and v not in ontbrekend)

    # Mermaid: van boven (samengesteld) naar beneden (elementair). Knopen worden per laag in de
    # berekende volgorde gedeclareerd; de layout-engine gebruikt die volgorde als startpunt.
    volg = [v for laag in lagen for v in laag if isinstance(v, str)]
    ids = {v: f"n{i}" for i, v in enumerate(volg)}
    m = ["---", "config:", "  layout: elk", "  elk:", "    nodePlacementStrategy: NETWORK_SIMPLEX", "---",
         "flowchart TB"]
    for v in volg:
        m.append(f'  {ids[v]}["{mermaid_label(v)}"]')
    kring_randen = []
    gesorteerd = sorted(uniek.items(), key=lambda x: (volg.index(x[0][0]), volg.index(x[0][1])))
    if args.alleen_genus:
        gesorteerd = [x for x in gesorteerd if x[1] in ("genus", "zelf")]
    for i, ((b, d), soort) in enumerate(gesorteerd):
        pijl = "-->" if soort in ("genus", "zelf") else "-.->"
        m.append(f"  {ids[b]} {pijl} {ids[d]}")
        if kring_rand(b, d):
            kring_randen.append(str(i))
    m.append("  classDef kring fill:#fde2e2,stroke:#c0392b,stroke-width:2px,color:#000")
    m.append("  classDef ontbreekt fill:#f4f4f4,stroke:#888,stroke-dasharray:5 5,color:#000")
    m.append("  classDef elementair fill:#eef5ee,stroke:#5b8a5b,color:#000")
    if elementair:
        m.append("  class " + ",".join(ids[v] for v in elementair if v not in in_kring) + " elementair")
    if in_kring:
        m.append("  class " + ",".join(ids[v] for v in sorted(in_kring)) + " kring")
    if ontbrekend:
        m.append("  class " + ",".join(ids[v] for v in ontbrekend) + " ontbreekt")
    if kring_randen:
        m.append("  linkStyle " + ",".join(kring_randen) + " stroke:#c0392b,stroke-width:2px")

    uit.append("## Niveaus\n")
    uit.append("Niveau 0 = elementair (verwijst naar geen ander begrip in de lijst); hoger = meer samengesteld.\n")
    for i, laag in enumerate(lagen):
        echte = [v for v in laag if isinstance(v, str)]
        uit.append(f"- **niveau {len(lagen) - 1 - i}:** " + ", ".join(echte))
    uit.append(f"\nDe volgorde binnen de niveaus is geoptimaliseerd op de genus-randen (taxonomie); "
               f"resterende kruisingen daarin: {n_kruis}. Verwijzingen naar gebruikte begrippen kruisen vaak, "
               f"omdat enkele begrippen door veel andere worden gebruikt.\n")

    uit.append("## Diagram\n")
    uit.append("Boven = samengestelde begrippen, onder = elementaire begrippen. Doorgetrokken pijl = genus "
               "(bovenliggend begrip), gestippeld = gebruikt begrip, rood = kring, groen = elementair, "
               "gestreepte rand = ontbreekt in de lijst.\n")
    uit.append("```mermaid")
    uit += m
    uit.append("```")
    if args.drawio:
        schrijf_drawio(args.drawio, niveau, lagen, keten, uniek, set(in_kring), set(ontbrekend), kring_rand)
        print(f"draw.io-bestand geschreven naar {args.drawio}")

    tekst = "\n".join(uit) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tekst)
        print(f"Rapport geschreven naar {args.output}: {len(alle_kringen)} kringen, "
              f"{len(zelf)} zelfverwijzingen, {len(ontbrekend)} ontbrekende begrippen")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(tekst)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="stap", required=True)
    e = sub.add_parser("extract", help="kandidaat-randen uit definities halen")
    e.add_argument("begrippen")
    e.add_argument("-o", "--output", default="randen.csv")
    e.set_defaults(func=extract)
    a = sub.add_parser("analyse", help="kringen zoeken en Mermaid-diagram maken")
    a.add_argument("randen")
    a.add_argument("--begrippen", help="begrippenlijst, om ontbrekende begrippen te herkennen")
    a.add_argument("-o", "--output")
    a.add_argument("--drawio", help="schrijf ook een .drawio-bestand met gelaagde layout")
    a.add_argument("--alleen-genus", action="store_true", help="Mermaid-diagram met alleen genus-pijlen (taxonomie)")
    a.set_defaults(func=analyse)
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows-console (cp1252)
    args.func(args)


if __name__ == "__main__":
    main()
