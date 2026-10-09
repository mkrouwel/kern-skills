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

begrippen.csv: kolommen 'term' en 'definitie', optioneel 'synoniemen'
(gescheiden door '|'). Scheidingsteken ';' of ',' wordt automatisch herkend.

randen.csv: kolommen 'bron;doel;soort;fragment'. soort is 'genus', 'gebruikt'
of 'zelf' (de term staat in zijn eigen definitie). Een doel dat geen begrip in
de lijst is, wordt als ontbrekend begrip getekend.
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


def extract(args):
    begrippen = lees_csv(args.begrippen)
    if not begrippen or "term" not in begrippen[0] or "definitie" not in begrippen[0]:
        sys.exit("begrippen.csv moet de kolommen 'term' en 'definitie' hebben")

    # (vorm, term) gesorteerd op lengte: langste treffer wint ("strafbaar feit" voor "feit")
    # term zonder kwalificatie tussen haakjes ("landelijke politieke partij (op moment)"),
    # alleen als die kale vorm uniek is (dus niet bij "openbaar lichaam (gw)" en "(wpp)")
    kaal = lambda s: re.sub(r"\s*\([^)]*\)\s*$", "", s).strip()
    kale_telling = defaultdict(int)
    for b in begrippen:
        kale_telling[norm(kaal(b["term"]))] += 1

    vormen = []
    for b in begrippen:
        namen = [b["term"]] + [s for s in b.get("synoniemen", "").split("|") if s.strip()]
        k = kaal(b["term"])
        if k != b["term"] and kale_telling[norm(k)] == 1:
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
        gezien = set()
        for i, (pos, doel, fragment) in enumerate(treffers):
            if doel in gezien:
                continue
            gezien.add(doel)
            if norm(doel) == norm(b["term"]):
                soort = "zelf"
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


def analyse(args):
    randen = lees_csv(args.randen)
    begrippen = {r["term"] for r in lees_csv(args.begrippen)} if args.begrippen else {r["bron"] for r in randen}

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
    uit.append(f"- Zelfverwijzingen (INT-11): {len(zelf)}")
    uit.append(f"- Kringen over meerdere begrippen (SAM-05): {len(alle_kringen)}"
               + (f" (afgekapt op {MAX_KRINGEN})" if len(alle_kringen) >= MAX_KRINGEN else ""))
    uit.append(f"- Ontbrekende begrippen (SAM-08): {len(ontbrekend)}\n")

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

    ids = {v: f"n{i}" for i, v in enumerate(knopen)}
    m = ["flowchart LR"]
    for v in knopen:
        m.append(f'  {ids[v]}["{mermaid_label(v)}"]')
    kring_randen = []
    for i, ((b, d), soort) in enumerate(sorted(uniek.items())):
        pijl = "-->|genus|" if soort == "genus" else ("-->|zelf|" if soort == "zelf" else "-.->")
        m.append(f"  {ids[b]} {pijl} {ids[d]}")
        if b == d or (comp_van[b] == comp_van[d] and len(comps[comp_van[b]]) > 1):
            kring_randen.append(str(i))
    m.append("  classDef kring fill:#fde2e2,stroke:#c0392b,stroke-width:2px,color:#000")
    m.append("  classDef ontbreekt fill:#f4f4f4,stroke:#888,stroke-dasharray:5 5,color:#000")
    if in_kring:
        m.append("  class " + ",".join(ids[v] for v in sorted(in_kring)) + " kring")
    if ontbrekend:
        m.append("  class " + ",".join(ids[v] for v in ontbrekend) + " ontbreekt")
    if kring_randen:
        m.append("  linkStyle " + ",".join(kring_randen) + " stroke:#c0392b,stroke-width:2px")

    uit.append("## Diagram\n")
    uit.append("Doorgetrokken pijl = genus, gestippeld = gebruikt begrip, rood = onderdeel van een kring, "
               "gestreepte rand = begrip ontbreekt in de lijst.\n")
    uit.append("```mermaid")
    uit += m
    uit.append("```")

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
    a.set_defaults(func=analyse)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
