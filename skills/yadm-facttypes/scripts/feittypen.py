"""Feittypen uit een of meer YADM-exports (DEMO Fact Model, JSON) halen.

  python feittypen.py "<export>.json" [meer exports ...] [-o uitvoer.md]

Bundelt de entiteittypen, attribuutsoorten, eigenschapsoorten en productsoorten uit de
Object Fact Diagrams van de exports tot één tabel:

  Feittype | Soort | Waardetype | Afleiding | Bron

Regels (zie ook SKILL.md):
- YADM deelt node-id's tussen diagrammen; elementen worden over de exports samengevoegd.
  Heet hetzelfde element per export anders, dan geldt de naam die het vaakst voorkomt.
- Entiteittype: 'entity_type'-node (naam in de body; een kop 'A' wordt genegeerd), of een
  'attribute'-node of 'entity_type' met een andere kop (kop = naam, body = attribuutregels).
  Een 'set' telt als het entiteittype dat erin staat.
- Attribuutsoort: regel 'naam {waardetype}' in de body -> 'naam van [entiteittype]'.
- Eigenschapsoort: doorgetrokken lijn met ruit in het midden; formulering = middelste label.
  De richting van de lijn (bron -> doel) wijst de eigenaar aan (de bron); aan de doelkant
  hoort 0..1 of 1..1 te staan, anders wordt dat gemeld. Een lijn waarvan een eindpunt in
  geen enkele export voorkomt, wordt alleen gemeld en niet opgenomen.
- Productsoort: 'production_event' (TK-nummer) met een tekstnode als formulering, geplaatst bij
  het entiteittype waarmee het via een lijn verbonden is. Het entiteittype waarin de
  productiegebeurtenis in het diagram staat, is een specialisatie van dat entiteittype.
- Gestippelde lijn (alleen als beide eindpunten in hetzelfde diagram staan, met de namen uit
  dat diagram): handle-derivation 'aggregation' = aggregatie, 'generalisation' = generalisatie,
  gesloten pijl = specialisatie; zonder pijl of derivation naar een aggregaat of generalisatie
  hoort de lijn daarbij.
- Volgorde: elementaire entiteittypen eerst; een entiteittype na de entiteittypen waarnaar zijn
  eigenschapsoorten verwijzen; specialisatie direct na haar ouder; generalisatie en aggregatie
  na hun leden. Attribuut-, eigenschap- en productsoorten direct onder hun entiteittype.
- Een entiteittype dat zelf een specialisatie, generalisatie of aggregatie is, krijgt een *.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict


def regels(s):
    return [r.strip() for r in str(s or "").replace("\r", "").split("\n") if r.strip()]


def plak(rs):
    """Regels samenvoegen; afbreekstreepje aan het regeleinde weg, behalve na een hoofdletterwoord."""
    u = ""
    for r in rs:
        if not u:
            u = r
        elif u.endswith("-") and not any(c.isupper() for c in u.split()[-1][:-1]):
            u = u[:-1] + r
        else:
            u += " " + r
    return u


def schoon(lbl):
    s = re.sub(r"<br\s*/?>", " ", lbl or "").replace("&nbsp;", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return "" if s in ("...", "…") else s


def inhoud(n):
    c = n["data"].get("content") or {}
    return {"body": c} if isinstance(c, str) else c


def et_info(n):
    """(naam, attribuutregels) van een entity_type- of attribute-node."""
    c = inhoud(n)
    h, b = (c.get("header") or "").strip(), c.get("body") or ""
    if n["type"] == "attribute" or (h and h != "A"):
        return plak(regels(h)), regels(b)
    return plak(regels(b)), []


max1 = lambda l: bool(re.fullmatch(r"(\d+\.\.)?[01]", l or ""))


def lees(paden):
    """Feitenmodel uit de exports als dict (zie het einde van deze functie), of None zonder entiteittypen."""
    # ---------- inlezen ----------
    U, VOORKOMENS, E, H = {}, defaultdict(list), [], {}
    for pad in paden:
        with open(pad, encoding="utf-8-sig") as f:
            d = json.load(f)
        kort = d.get("fileName", pad)
        for n in d.get("nodes", []):
            U.setdefault(n["id"], n)
            VOORKOMENS[n["id"]].append((kort, n))
            for v in (n["data"].get("handles") or {}).values():
                if isinstance(v, dict):
                    for h in v.get("handles", []):
                        H[h["id"]] = h.get("derivation")
        E += [(kort, e) for e in d.get("edges", [])]

    kinderen = defaultdict(list)
    for n in U.values():
        if n.get("parentId"):
            kinderen[n["parentId"]].append(n)

    def eigen_naam(n):
        i = n["id"]
        if n["type"] == "set":                         # een set telt als het entiteittype zelf
            return ", ".join(eigen_naam(k) for k in kinderen[i])
        if n["type"] in ("entity_type", "attribute"):
            nm = et_info(n)[0]
            if nm == "A" and kinderen[i]:              # plaatshouder binnen een set
                return ", ".join(eigen_naam(k) for k in kinderen[i])
            return nm
        if n["type"] == "production_event":
            return "".join(regels(inhoud(n).get("body")))
        return n["type"]

    # canonieke naam: meest voorkomende over de exports, bij gelijkspel de eerste
    CANON, opm, conflicten = {}, [], []
    for i, lijst in VOORKOMENS.items():
        namen = [eigen_naam(n) for _, n in lijst]
        tel = Counter(namen)
        CANON[i] = max(namen, key=lambda x: (tel[x], -namen.index(x)))
        if len(tel) > 1 and U[i]["type"] in ("entity_type", "attribute"):
            conflicten.append((CANON[i], {nm: sorted(k for k, n in lijst if eigen_naam(n) == nm) for nm in tel}))
            opm.append(f"Hetzelfde element heet per export anders; gebruikt: {CANON[i]} (ook: " + ", ".join(
                f"{nm} in {', '.join(k for k, n in lijst if eigen_naam(n) == nm)}" for nm in tel if nm != CANON[i]) + ").")
    naam = CANON.get

    def is_plaatshouder(i):
        n = U[i]
        return n["type"] == "entity_type" and et_info(n)[0] == "A" and kinderen[i]

    # ---------- entiteittypen en attribuutsoorten ----------
    ET, kop_a = {}, []
    for i, lijst in VOORKOMENS.items():
        if U[i]["type"] not in ("entity_type", "attribute") or is_plaatshouder(i):
            continue
        e = ET.setdefault(naam(i), {"bron": set(), "attrs": {}, "focus": {}, "dubbel": set()})
        for kort, m in lijst:
            e["bron"].add(kort)
            e["focus"].setdefault(m["data"].get("focus") or "", set()).add(kort)   # in = intern, out = extern
            if m["type"] == "entity_type" and (inhoud(m).get("header") or "").strip() == "A":
                kop_a.append((kort, i, naam(i)))
            gezien = set()
            for r in et_info(m)[1]:
                r = re.sub(r"^-\s*", "", r)
                mm = re.match(r"(.*?)\s*\{(.*)\}\s*$", r)
                a, w = (mm.group(1).strip(), mm.group(2).strip()) if mm else (r, "")
                e["attrs"].setdefault((a, w), set()).add(kort)
                if a.lower() in gezien:
                    e["dubbel"].add(a)
                gezien.add(a.lower())
    if not ET:
        return None

    # ---------- productsoorten ----------
    PK, pk_van = {}, {}                                # (tk, formulering) -> gegevens; node-id -> sleutel
    for i, n in U.items():
        if n["type"] == "production_event":
            tekst = [t for t in kinderen[i] if t["type"] == "text"]
            form = schoon(plak(regels(inhoud(tekst[0]).get("body")))) if tekst else ""
            pk_van[i] = (naam(i), form)
            v = PK.setdefault(pk_van[i], {"bron": set(), "lijn": set(), "ouder": set()})
            v["bron"] |= {k for k, _ in VOORKOMENS[i]}
            par = n.get("parentId")
            if par in U and U[par]["type"] in ("entity_type", "attribute"):
                v["ouder"].add(naam(par))

    # ---------- edges ----------
    PT, PT_LIJNEN, AFL = {}, [], defaultdict(set)
    zwevend, gestippeld, kard_fout = [], [], []
    for kort, e in E:
        D = e.get("data") or {}
        s, t = e["source"], e["target"]
        cd = D.get("cardinality") or {}
        lab = [schoon((cd.get(k) or {}).get("label")) for k in ("startLabel", "middleLabel", "endLabel")]
        if s not in U or t not in U:
            zwevend.append((kort, "eigenschapsoort" if D.get("markerMid") else "overig", lab[1], e["id"]))
            continue
        if U[s]["type"] == "production_event" or U[t]["type"] == "production_event":
            p, o = (s, t) if s in pk_van else (t, s)
            if U[o]["type"] in ("entity_type", "attribute", "set"):
                PK[pk_van[p]]["lijn"].add(naam(o))
            continue
        if D.get("markerMid"):                         # eigenschapsoort
            g = PT.setdefault(lab[1] or f"(geen formulering: {naam(s)} → {naam(t)})",
                              {"bron": set(), "eigenaar": naam(s), "ander": set()})
            g["bron"].add(kort)
            g["ander"].add(naam(t))
            PT_LIJNEN.append({"bron": kort, "van": naam(s), "naar": naam(t), "form": lab[1],
                              "kard_van": lab[0], "kard_naar": lab[2]})
            if not max1(lab[2]):
                kard_fout.append(f"'{lab[1]}' ({naam(s)} → {naam(t)}, {lab[0]} : {lab[2]}, {kort})")
            continue
        if D.get("lineType") == "dashed":
            gestippeld.append((kort, e))

    # gestippelde lijnen: alleen binnen één diagram, met de namen uit dat diagram
    et_namen = set(ET)
    def naam_in(i, kort):
        for k, n in VOORKOMENS[i]:
            if k == kort:
                nm = eigen_naam(n)
                return nm if nm in et_namen else naam(i)
        return naam(i)
    buiten, ongericht, onbepaald = [], [], []
    for kort, e in gestippeld:
        if not all(any(k == kort for k, _ in VOORKOMENS[x]) for x in (e["source"], e["target"])):
            buiten.append(f"{naam(e['source'])} → {naam(e['target'])} ({kort})")
            continue
        s, t = naam_in(e["source"], kort), naam_in(e["target"], kort)
        if s == t:
            continue                                   # tweede blok van hetzelfde entiteittype
        der = H.get(e.get("targetHandle"))
        if der == "aggregation":
            AFL[("aggregatie", t)].add(s)
        elif der == "generalisation":
            AFL[("generalisatie", t)].add(s)
        elif e.get("markerEnd"):
            AFL[("specialisatie", s)].add(t)
        else:
            ongericht.append((kort, s, t))
    for kort, s, t in ongericht:
        if AFL.get(("aggregatie", t)):
            AFL[("aggregatie", t)].add(s)
        elif AFL.get(("generalisatie", t)):
            AFL[("generalisatie", t)].add(s)
        elif t not in AFL.get(("specialisatie", s), set()):
            onbepaald.append((kort, s, t))

    # productsoort bij het gelinkte entiteittype; ouder = specialisatie daarvan
    for (tk, form), v in PK.items():
        kandidaten = sorted(v["lijn"]) or sorted(v["ouder"])
        v["bij"] = kandidaten[0] if kandidaten else None
        for ouder in v["ouder"] - v["lijn"]:
            if v["lijn"] and ouder in ET:
                AFL[("specialisatie", ouder)].add(v["bij"])
                opm.append(f"{ouder} is als specialisatie van {v['bij']} opgenomen "
                           f"(omringt productsoort PK{tk}, die aan {v['bij']} hangt).")

    # ---------- volgorde ----------
    afgeleid = {x for (soort, x), ys in AFL.items() if ys and x in ET}
    ster = lambda nm: nm + ("*" if nm in afgeleid else "")
    deps, spec_kind = defaultdict(set), defaultdict(set)
    for (soort, x), ys in AFL.items():
        deps[x] |= ys
        if soort == "specialisatie":
            for y in ys:
                spec_kind[y].add(x)
    for g in PT.values():
        deps[g["eigenaar"]] |= g["ander"]
    for nm in ET:
        deps[nm] &= set(ET) - {nm}

    volgorde, gedaan = [], set()
    klaar = lambda x: deps[x] <= gedaan
    def plaats(x):
        volgorde.append(x)
        gedaan.add(x)
        verder = True                                  # specialisaties direct erna, zodra ze klaar zijn
        while verder:
            verder = False
            for c in sorted(spec_kind[x]):
                if c not in gedaan and klaar(c):
                    plaats(c)
                    verder = True
    while True:
        ronde = [x for x in sorted(ET) if x not in gedaan and klaar(x)]
        if not ronde:
            break
        for x in ronde:
            if x not in gedaan and klaar(x):
                plaats(x)
    kring = [x for x in sorted(ET) if x not in gedaan]
    volgorde += kring
    if kring:
        opm.append("Afhankelijkheidskring; alfabetisch achteraan geplaatst: " + ", ".join(kring) + ".")

    def afleiding(nm):
        delen = []
        for soort, sep in (("specialisatie", ", "), ("generalisatie", ", "), ("aggregatie", " × ")):
            if AFL.get((soort, nm)):
                delen.append(f"{soort} van " + sep.join(ster(x) for x in sorted(AFL[(soort, nm)])))
        delen += [f"gestippeld naar {ster(t)} (soort onbekend)" for _, s, t in onbepaald if s == nm]
        return "; ".join(delen)

    return {"ET": ET, "PT": PT, "PT_LIJNEN": PT_LIJNEN, "PK": PK, "AFL": AFL, "volgorde": volgorde,
            "afgeleid": afgeleid, "ster": ster, "afleiding": afleiding, "conflicten": conflicten,
            "kop_a": kop_a, "zwevend": zwevend, "kard_fout": kard_fout, "onbepaald": onbepaald,
            "buiten": buiten, "opm": opm}


def verwerk(paden):
    M = lees(paden)
    if M is None:
        return None, ["Geen feitenmodel (entiteittypen) gevonden in de opgegeven exports."]
    ET, PT, PK, ster, afleiding, opm = M["ET"], M["PT"], M["PK"], M["ster"], M["afleiding"], list(M["opm"])
    kard_fout, onbepaald, buiten, zwevend = M["kard_fout"], M["onbepaald"], M["buiten"], M["zwevend"]

    # ---------- tabel ----------
    B = lambda s: ", ".join(sorted(s))
    uit = ["| Feittype | Soort | Waardetype | Afleiding | Bron |", "|---|---|---|---|---|"]
    rij = lambda *c: uit.append("| " + " | ".join(c) + " |")
    for nm in M["volgorde"]:
        e = ET[nm]
        rij(ster(nm), "entiteittype", "", afleiding(nm), B(e["bron"]))
        for (a, w), br in e["attrs"].items():
            rij(f"{a} van [{nm.lower()}]", "attribuutsoort", w, "", B(br))
        for form, g in sorted(PT.items(), key=lambda x: x[0].lower()):
            if g["eigenaar"] == nm:
                rij(form, "eigenschapsoort", "", "", B(g["bron"]))
        for (tk, form), v in sorted(PK.items()):
            if v["bij"] == nm:
                rij(f"{form or '(geen formulering)'} (PK{tk})", "productsoort", "", "", B(v["bron"]))
    for (tk, form), v in sorted(PK.items()):
        if not v["bij"]:
            rij(f"{form} (PK{tk})", "productsoort (zonder entiteittype)", "", "", B(v["bron"]))

    # ---------- opmerkingen ----------
    if kard_fout:
        opm.append("Kardinaliteit niet in lijn met de richting (aan de doelkant hoort 0..1 of 1..1): "
                   + "; ".join(kard_fout) + ".")
    if onbepaald:
        opm.append("Gestippelde lijn zonder herkenbare afleiding: "
                   + "; ".join(f"{s} → {t} ({k})" for k, s, t in onbepaald) + ".")
    if buiten:
        opm.append(f"{len(buiten)} gestippelde lijn(en) naar een element buiten het eigen diagram genegeerd: "
                   + "; ".join(buiten) + ".")
    if zwevend:
        pt_z = sorted({f for _, s, f, _ in zwevend if s == "eigenschapsoort" and f and f not in PT})
        opm.append(f"{len(zwevend)} lijnen met een eindpunt dat in geen enkele export voorkomt; niet opgenomen. "
                   + (f"Eigenschapsoorten die alleen zo voorkomen: {'; '.join(pt_z)}." if pt_z else ""))
    return uit, opm


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("exports", nargs="+", help="YADM-export(s) in JSON")
    p.add_argument("-o", "--output", help="schrijf het resultaat ook naar dit Markdown-bestand")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tabel, opm = verwerk(args.exports)
    tekst = "\n".join((tabel or []) + (["", "### Opmerkingen", ""] + [f"- {o}" for o in opm] if opm else []))
    print(tekst)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tekst + "\n")


if __name__ == "__main__":
    main()
