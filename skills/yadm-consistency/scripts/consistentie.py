"""Consistentie tussen het CSD (CM) en het feitenmodel (FM) in YADM-exports controleren,
en optioneel het feitenmodel tegen een begrippenlijst.

  python consistentie.py "<export>.json" [meer exports ...] [-b begrippen.csv] [-o uitvoer.md]

Bouwt voort op de zusterskills (in dezelfde skills-map geïnstalleerd):
- yadm-tpt          (scripts/tpt.py)         leest het CSD: transactiesoorten, type, raadplegen
- yadm-facttypes    (scripts/feittypen.py)   leest het feitenmodel: entiteittypen, eigenschap-,
                                             attribuut- en productsoorten, afleidingen
- definitiekwaliteit (scripts/graaf.py)      leest de begrippenlijst en het genus per definitie
                                             (alleen nodig met -b)

De regels staan in REGELS hieronder en in SKILL.md. Uitvoer: een samenvatting per regel en een
tabel met bevindingen (Regel | Element | Bevinding | Bron).
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]


def importeer(skill, module):
    pad = SKILLS / skill / "scripts"
    if not (pad / f"{module}.py").exists():
        sys.exit(f"Deze skill gebruikt de skill '{skill}' ({pad / module}.py niet gevonden). "
                 f"Installeer die in dezelfde skills-map.")
    sys.path.insert(0, str(pad))
    return __import__(module)


tpt = importeer("yadm-tpt", "tpt")
feittypen = importeer("yadm-facttypes", "feittypen")

# (id, ernst, omschrijving)
REGELS = [
    ("CON-01", "fout", "Elke originele transactiesoort (O) in het CM heeft een productsoort in het FM"),
    ("CON-02", "fout", "Elke productsoort in het FM hoort bij een originele transactiesoort in het CM"),
    ("CON-03", "fout", "Eén transactiesoort heeft één productsoort (één formulering per PK-nummer)"),
    ("CON-04", "fout", "Een informatielink naar TKnn in het CM veronderstelt productsoort PKnn in het FM"),
    ("CON-05", "fout", "Een productsoort hangt aan het entiteittype dat de variabele in de formulering is"),
    ("CON-06", "waarschuwing", "Een productsoort heeft één variabele (bij een aggregaat: de componenten) en eindigt op 'is/zijn <voltooid deelwoord>'"),
    ("CON-07", "fout", "Beide uiteinden van een eigenschapsoort zijn een variabele in de formulering"),
    ("CON-08", "fout", "Aan de doelkant van een eigenschapsoort (richting van de lijn) staat 0..1 of 1..1"),
    ("CON-09", "waarschuwing", "Aan de bronkant van een eigenschapsoort is de kardinaliteit ingevuld"),
    ("CON-10", "fout", "Elke attribuutsoort heeft een waardetype"),
    ("CON-11", "fout", "Een attribuutsoort komt per entiteittype één keer voor, overal met hetzelfde waardetype"),
    ("CON-12", "fout", "Een entiteittype in focus (intern) heeft minstens één productsoort"),
    ("CON-13", "waarschuwing", "Geen geïsoleerde entiteittypen (zonder eigenschap-, attribuut-, productsoort of afleiding)"),
    ("CON-14", "fout", "Een element heeft in alle diagrammen dezelfde naam"),
    ("CON-15", "waarschuwing", "Geen edges naar ontbrekende nodes en geen entiteittypen met kop 'A'"),
    ("BEG-01", "fout", "Elk entiteittype heeft een begrip in de begrippenlijst"),
    ("BEG-02", "fout", "Specialisatie: het genus van de definitie is de ouder in het FM"),
    ("BEG-03", "fout", "Generalisatie: de definitie somt de leden op, en een opsommende definitie is een generalisatie"),
    ("BEG-04", "fout", "Aggregatie: de definitie verwijst naar alle componenten"),
    ("BEG-05", "signaal", "De definitie van de eigenaar van een eigenschapsoort verwijst naar het andere entiteittype"),
    ("BEG-06", "signaal", "Begrippen zonder entiteittype"),
]

norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[-_]", " ", (s or "").lower())).strip()
var = lambda form: [norm(re.sub(r"^set van ", "", v.strip(), flags=re.I)) for v in re.findall(r"\[([^\]]+)\]", form or "")]
nr = lambda s: str(int(s)) if str(s).isdigit() else str(s)


def lees_json(pad):
    with open(pad, encoding="utf-8-sig") as f:
        return json.load(f)


def controleer(paden, begrippenlijst=None):
    B = []                                              # (regel, element, bevinding, bron)
    data = {p: lees_json(p) for p in paden}
    soort = lambda d: {n["type"] for n in d.get("nodes", [])}
    cm_paden = [p for p, d in data.items() if soort(d) & {"transactor", "self_activation", "transaction"}]
    fm_paden = [p for p, d in data.items() if soort(d) & {"entity_type", "attribute"}]
    naam = lambda p: data[p].get("fileName", p)
    niet, overgeslagen = [], set()             # toelichting; regel-id's die niet zijn gecontroleerd

    # ---------- CM ----------
    TK, TK_BRON, RAADPLEEG = {}, defaultdict(set), []   # nr -> type; nr -> exports; (label, rol, export)
    for p in cm_paden:
        M, _ = tpt.lees(p)
        if not M:
            continue
        for i, t in M["tk"].items():
            TK.setdefault(nr(t["nr"]), t["type"])
            TK_BRON[nr(t["nr"])].add(M["bestand"])
        rolnaam = {t["uitvoerder_id"]: t["uitvoerder"] for t in M["tk"].values()}
        for rol, labels in M["raadpleegt"].items():
            RAADPLEEG += [(l, rolnaam.get(rol, "?"), M["bestand"]) for l in labels if l.startswith("TK")]

    # ---------- FM ----------
    F = feittypen.lees(fm_paden) if fm_paden else None
    ET, PK, AFL = (F["ET"], F["PK"], F["AFL"]) if F else ({}, {}, {})
    ster = F["ster"] if F else (lambda x: x)
    br = lambda s: ", ".join(sorted(s))
    pk_nrs = defaultdict(set)
    for (tk, form), v in PK.items():
        pk_nrs[nr(tk)].add(form)

    if not cm_paden:
        niet.append("CON-01 t/m CON-04: geen CM (CSD) in de exports")
        overgeslagen |= {"CON-01", "CON-02", "CON-03", "CON-04"}
    if not F:
        niet.append("CON-01 t/m CON-14 en BEG: geen feitenmodel in de exports")
        overgeslagen |= {r for r, _, _ in REGELS if r != "CON-15"}
    if cm_paden and F:
        for n_, t in sorted(TK.items(), key=lambda x: tpt.sorteer_id(x[0])):
            if not n_.isdigit():
                B.append(("CON-01", f"TK{n_}", "transactiesoort zonder nummer; niet te controleren", br(TK_BRON[n_])))
            elif t == "O" and n_ not in pk_nrs:
                B.append(("CON-01", f"TK{n_}", "geen productsoort PK" + n_ + " in het FM", br(TK_BRON[n_])))
        for (tk, form), v in sorted(PK.items()):
            if nr(tk) not in TK:
                B.append(("CON-02", f"{form} (PK{tk})", f"geen transactiesoort TK{tk} in het CM", br(v["bron"])))
            elif TK[nr(tk)] != "O":
                B.append(("CON-02", f"{form} (PK{tk})", f"TK{tk} is van type {TK[nr(tk)]}, niet O", br(v["bron"])))
        for l, rol, bron in sorted(set(RAADPLEEG)):
            m = re.match(r"TK(\d+)", l)
            if m and nr(m.group(1)) not in pk_nrs:
                B.append(("CON-04", l, f"{rol} raadpleegt de bank van {l}, maar PK{m.group(1)} staat niet in het FM", bron))
    for tk, forms in sorted(pk_nrs.items()):
        if len(forms) > 1:
            B.append(("CON-03", f"PK{tk}", "meerdere formuleringen: " + " / ".join(sorted(forms)),
                      br(set().union(*(PK[(k, f)]["bron"] for (k, f) in PK if nr(k) == tk)))))

    # voorouders (specialisatie -> ouder, lid -> generalisatie) en componenten van aggregaten
    boven = defaultdict(set)
    for (s, x), ys in AFL.items():
        if s == "specialisatie":
            boven[x] |= ys
        elif s == "generalisatie":
            for y in ys:
                boven[y].add(x)
    def voorouders(x, gezien=None):
        gezien = set() if gezien is None else gezien
        for y in boven[x] - gezien:
            gezien.add(y)
            voorouders(y, gezien)
        return gezien
    def hint(x, vs):
        v = [a for a in sorted(voorouders(x)) if norm(a) in vs]
        return f" ([{norm(v[0])}] is een ouder of generalisatie van {x})" if v else ""
    comp = lambda x: sorted(AFL.get(("aggregatie", x), set()))
    fmt = lambda vs: ", ".join(f"[{x}]" for x in vs) or "geen"

    # productsoorten
    for (tk, form), v in sorted(PK.items()):
        el = f"{form or '(geen formulering)'} (PK{tk})"
        vs = var(form)
        doel = sorted(v["lijn"]) or sorted(v["ouder"])
        agg = [x for x in doel if comp(x)]
        if not doel:
            B.append(("CON-05", el, "productsoort hangt aan geen entiteittype", br(v["bron"])))
        elif agg and len(vs) > 1:
            mist = [c for c in comp(agg[0]) if norm(c) not in vs]
            if mist:
                B.append(("CON-05", el, f"hangt aan aggregaat {agg[0]}; component(en) {', '.join(mist)} niet als "
                          f"variabele (variabelen: {fmt(vs)})", br(v["bron"])))
        elif not any(norm(x) in vs for x in doel):
            B.append(("CON-05", el, f"hangt aan {', '.join(doel)}, maar de variabele is {fmt(vs)}"
                      + hint(doel[0], vs), br(v["bron"])))
        n_ok = len(comp(agg[0])) if agg else 1
        if len(vs) != n_ok or not re.search(r"\b(is|zijn)\s+\S+$", form):
            B.append(("CON-06", el, f"{len(vs)} variabele(n), verwacht {n_ok}"
                      if len(vs) != n_ok else "eindigt niet op 'is/zijn <voltooid deelwoord>'", br(v["bron"])))

    # eigenschapsoorten
    gezien = {}
    for l in F["PT_LIJNEN"] if F else []:
        gezien.setdefault((l["form"], l["van"], l["naar"], l["kard_van"], l["kard_naar"]), set()).add(l["bron"])
    for (form, van, naar, kv, kn), bron in sorted(gezien.items(), key=lambda x: (x[0][0].lower(), x[0][1:3])):
        el = form or f"(geen formulering: {van} → {naar})"
        vs = var(form)
        if not form:
            B.append(("CON-07", el, "eigenschapsoort zonder formulering", br(bron)))
        elif form.count("[") != form.count("]"):
            B.append(("CON-07", el, "haken [ ] niet in evenwicht", br(bron)))
        else:
            mist = [x for x in dict.fromkeys((van, naar)) if norm(x) not in vs]
            if van == naar and len(vs) < 2:
                mist = [van]
            if mist:
                B.append(("CON-07", el, f"{' en '.join(mist)} niet als variabele in de formulering "
                          f"(variabelen: {fmt(vs)})" + "".join(hint(x, vs) for x in mist), br(bron)))
        if not feittypen.max1(kn):
            B.append(("CON-08", el, f"{van} → {naar}: doelkant is '{kn or 'leeg'}', verwacht 0..1 of 1..1", br(bron)))
        if not kv:
            B.append(("CON-09", el, f"{van} → {naar}: kardinaliteit aan de bronkant ontbreekt", br(bron)))

    # attribuutsoorten
    for nm, e in sorted(ET.items()):
        per_naam = defaultdict(set)
        for (a, w), bron in e["attrs"].items():
            per_naam[a.lower()].add(w)
            if not w:
                B.append(("CON-10", f"{a} van [{nm.lower()}]", "geen waardetype", br(bron)))
        for a in sorted(e["dubbel"]):
            B.append(("CON-11", f"{a} van [{nm.lower()}]", "komt meer dan één keer voor in hetzelfde blok", br(e["bron"])))
        for a, ws in sorted(per_naam.items()):
            if len(ws - {""}) > 1:
                B.append(("CON-11", f"{a} van [{nm.lower()}]", "verschillende waardetypen: " + ", ".join(sorted(ws - {""})), br(e["bron"])))

    # entiteittypen: focus, isolement
    heeft_pk = defaultdict(set)
    for (tk, form), v in PK.items():
        for x in v["lijn"] | v["ouder"] | ({v["bij"]} if v["bij"] else set()):
            heeft_pk[x].add(f"PK{tk}")
    in_afl = {x for (s, x), ys in AFL.items() if ys} | {y for ys in AFL.values() for y in ys}
    in_pt = {l["van"] for l in F["PT_LIJNEN"]} | {l["naar"] for l in F["PT_LIJNEN"]} if F else set()
    for nm, e in sorted(ET.items()):                    # focus 'in' = intern (wit), 'out' = extern (grijs)
        f = e["focus"]
        if len(f) > 1:
            B.append(("CON-12", ster(nm), "focus verschilt per diagram: " + "; ".join(
                f"{k or 'geen'} ({', '.join(sorted(v))})" for k, v in sorted(f.items())), br(e["bron"])))
        if "in" in f and not heeft_pk[nm]:              # een productsoort aan een extern entiteittype mag wel
            B.append(("CON-12", ster(nm), "in focus (intern) maar geen productsoort", br(e["bron"])))
    for nm, e in sorted(ET.items()):
        if not e["attrs"] and nm not in in_pt and not heeft_pk[nm] and nm not in in_afl:
            B.append(("CON-13", ster(nm), "geen eigenschap-, attribuut- of productsoort en geen afleiding", br(e["bron"])))

    # namen en hygiëne
    for canon, namen in (F["conflicten"] if F else []):
        B.append(("CON-14", canon, "heet ook: " + "; ".join(f"{n} ({', '.join(k)})" for n, k in namen.items() if n != canon),
                  br(set().union(*namen.values()))))
    overal = {n["id"] for d in data.values() for n in d.get("nodes", [])}
    for p, d in data.items():
        ids = {n["id"] for n in d.get("nodes", [])}
        los = [e for e in d.get("edges", []) if e["source"] not in ids or e["target"] not in ids]
        if los:
            elders = sum(1 for e in los if all(x in overal for x in (e["source"], e["target"])))
            B.append(("CON-15", naam(p), f"{len(los)} edges naar ontbrekende nodes"
                      + (f", waarvan {elders} naar nodes in een andere export" if elders else ""), naam(p)))
    for kort, i, nm in (F["kop_a"] if F else []):
        B.append(("CON-15", nm, f"entiteittype met kop 'A' (node {i})", kort))

    # ---------- begrippenlijst ----------
    if begrippenlijst and F:
        graaf = importeer("definitiekwaliteit", "graaf")
        begrippen = graaf.lees_begrippen(begrippenlijst)
        randen = graaf.randen_uit(begrippen)
        index = defaultdict(set)                        # genormaliseerde naam -> termen
        for b in begrippen:
            for n_ in [b["term"], graaf.kern(b["term"])] + b["synoniemen"]:
                index[norm(n_)].add(b["term"])
        term = {nm: index.get(norm(nm), set()) for nm in ET}
        def termen(nms):
            return set().union(*(term.get(x, set()) for x in nms)) if nms else set()
        uit = defaultdict(lambda: defaultdict(set))     # term -> soort -> doelen
        for r in randen:
            uit[r["bron"]][r["soort"]].add(r["doel"])
        bron_lijst = Path(begrippenlijst).name
        for nm in sorted(ET):
            if not term[nm]:
                B.append(("BEG-01", ster(nm), "geen begrip gevonden (op term, kern of synoniem)", bron_lijst))
            else:
                exact = [t for t in term[nm] if t.lower() == nm.lower()]
                if not exact:
                    B.append(("BEG-01", ster(nm), "gekoppeld aan " + ", ".join(sorted(term[nm]))
                              + " (schrijfwijze of kwalificatie verschilt)", bron_lijst))
        for (s, x), ys in sorted(AFL.items()):
            if not ys or x not in ET or not term[x]:
                continue
            tx = sorted(term[x])
            if s == "specialisatie":
                ouders = termen(ys)
                genus = set().union(*(uit[t]["genus"] for t in tx))
                if not ouders:
                    B.append(("BEG-02", ster(x), f"ouder {', '.join(sorted(ys))} heeft geen begrip", bron_lijst))
                elif not genus & ouders:
                    B.append(("BEG-02", ster(x), f"FM: specialisatie van {', '.join(sorted(ys))}; genus in de definitie: "
                              + (", ".join(sorted(genus)) or "niet herkend"), bron_lijst))
            elif s == "generalisatie":
                leden = termen(ys)
                ops = set().union(*(uit[t]["opsomming"] for t in tx))
                if ops != leden:
                    B.append(("BEG-03", ster(x), f"FM: generalisatie van {', '.join(sorted(ys))}; opsomming in de definitie: "
                              + (", ".join(sorted(ops)) or "geen"), bron_lijst))
            elif s == "aggregatie":
                comp = termen(ys)
                alle = set().union(*(set().union(*uit[t].values()) for t in tx))
                mist = sorted(comp - alle)
                if mist or len(comp) < len(ys):
                    B.append(("BEG-04", ster(x), f"FM: aggregatie van {' × '.join(sorted(ys))}; definitie verwijst niet naar "
                              + ", ".join(mist + [y for y in sorted(ys) if not term.get(y)]), bron_lijst))
        gen = {x for (s, x), ys in AFL.items() if s == "generalisatie" and ys}
        for nm in sorted(ET):
            for t in sorted(term[nm]):
                if uit[t]["opsomming"] and nm not in gen:
                    B.append(("BEG-03", ster(nm), f"definitie van '{t}' is een opsomming ("
                              + ", ".join(sorted(uit[t]["opsomming"])) + "), maar het FM heeft geen generalisatie", bron_lijst))
        for l in sorted({(l["van"], l["naar"], l["form"]) for l in F["PT_LIJNEN"]}):
            van, naar, form = l
            if van == naar or not term.get(van) or not term.get(naar):
                continue
            alle = set().union(*(set().union(*uit[t].values()) for t in term[van]))
            if not alle & term[naar]:
                B.append(("BEG-05", form or f"{van} → {naar}", f"definitie van {', '.join(sorted(term[van]))} "
                          f"verwijst niet naar {', '.join(sorted(term[naar]))}", bron_lijst))
        gekoppeld = set().union(*term.values()) if term else set()
        los = [b["term"] for b in begrippen if b["term"] not in gekoppeld]
        if los:
            B.append(("BEG-06", f"{len(los)} begrippen", ", ".join(los), bron_lijst))
    elif begrippenlijst:
        pass                                            # al gemeld: geen feitenmodel
    else:
        niet.append("BEG-01 t/m BEG-06: geen begrippenlijst opgegeven (-b)")
        overgeslagen |= {r for r, _, _ in REGELS if r.startswith("BEG")}
    return B, niet, overgeslagen, [naam(p) for p in cm_paden], [naam(p) for p in fm_paden]


def rapport(B, niet, overgeslagen, cm, fm):
    tel = defaultdict(int)
    for b in B:
        tel[b[0]] += 1
    uit = [f"CM: {', '.join(cm) or '—'}  ", f"FM: {', '.join(fm) or '—'}", "",
           "### Samenvatting", "", "| Regel | Ernst | Omschrijving | Bevindingen |", "|---|---|---|---|"]
    uit += [f"| {i} | {e} | {o} | {'—' if i in overgeslagen else tel[i] or '✓'} |" for i, e, o in REGELS]
    if niet:
        uit += ["", "Niet gecontroleerd: " + "; ".join(niet) + "."]
    uit += ["", "### Bevindingen", "", "| Regel | Element | Bevinding | Bron |", "|---|---|---|---|"]
    volg = {r[0]: k for k, r in enumerate(REGELS)}
    esc = lambda s: str(s).replace("|", "\\|")
    uit += [f"| {r} | {esc(el)} | {esc(bv)} | {esc(bron)} |" for r, el, bv, bron in sorted(B, key=lambda b: volg[b[0]])]
    return uit


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("exports", nargs="+", help="YADM-export(s) in JSON: CM en FM")
    p.add_argument("-b", "--begrippen", help="begrippenlijst (CSV, formaat van de skill definitiekwaliteit)")
    p.add_argument("-o", "--output", help="schrijf het resultaat ook naar dit Markdown-bestand")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tekst = "\n".join(rapport(*controleer(args.exports, args.begrippen)))
    print(tekst)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tekst + "\n")


if __name__ == "__main__":
    main()
