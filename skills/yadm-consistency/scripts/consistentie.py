"""Consistentie tussen het CSD (CM) en het feitenmodel (FM) in YADM-exports controleren,
en optioneel het feitenmodel tegen een begrippenlijst en tegen een bankcontactentabel (BCT).

  python consistentie.py "<export>.json" [meer exports ...] [-b begrippen.csv] [-t bct.csv] [-o uitvoer.md]

Bouwt voort op de zusterskills (in dezelfde skills-map geïnstalleerd):
- yadm-tpt          (scripts/tpt.py)         leest het CSD: transactiesoorten, type, raadplegen
- yadm-facttypes    (scripts/feittypen.py)   leest het feitenmodel: entiteittypen, eigenschap-,
                                             attribuut- en productsoorten, afleidingen
- definitiekwaliteit (scripts/graaf.py)      leest de begrippenlijst en het genus per definitie
                                             (alleen nodig met -b)

De regels staan in references/regels.csv; de id's in deze code verwijzen daarnaar. Uitvoer: een samenvatting per regel en een
tabel met bevindingen (Regel | Element | Bevinding | Bron).
"""

import argparse
import csv
import io
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

# regels: references/regels.csv (Id, Categorie, Ernst, Regel, Controle)
with open(Path(__file__).resolve().parents[1] / "references" / "regels.csv", newline="", encoding="utf-8-sig") as f:
    REGELS = [(r["Id"], r["Ernst"], r["Regel"]) for r in csv.DictReader(f)]

norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[-_{}]", " ", (s or "").lower())).strip()
var = lambda form: [norm(re.sub(r"^set van ", "", v.strip(), flags=re.I)) for v in re.findall(r"\[([^\]]+)\]", form or "")]
nr = lambda s: str(int(s)) if str(s).isdigit() else str(s)


def lees_json(pad):
    with open(pad, encoding="utf-8-sig") as f:
        return json.load(f)


# ---------- BCT (bankcontactentabel) ----------
# kolomnamen (kleine letters) met toegestane varianten; zie docs/yadm-consistency.md
BCT_KOLOM = {"bank": ["bank id", "bank-id", "bankid"], "banknaam": ["bank"], "feittype": ["feittype"],
             "soort": ["soort"], "waardetype": ["waardetype"], "afleiding": ["afleiding"], "bron": ["bron fm", "bron"]}


def lees_bct(pad):
    with open(pad, newline="", encoding="utf-8-sig") as f:
        tekst = f.read()
    kop = tekst.splitlines()[0] if tekst else ""
    rijen = list(csv.DictReader(io.StringIO(tekst), delimiter=";" if kop.count(";") >= kop.count(",") else ","))
    kol = {k.strip().lower(): k for k in (rijen[0].keys() if rijen else []) if k}
    if "feittype" not in kol:
        sys.exit(f"{pad} moet ten minste de kolom 'feittype' hebben")
    def pak(r, naam):
        k = next((kol[k] for k in BCT_KOLOM[naam] if k in kol), None)
        return (r.get(k) or "").strip() if k else ""
    opm = next((kol[k] for k in kol if k.startswith("opm") and "bct" in k), kol.get("opmerking"))
    return [{**{n: pak(r, n) for n in BCT_KOLOM}, "opmerking": (r.get(opm) or "").strip() if opm else "", "regel": i + 2}
            for i, r in enumerate(rijen) if pak(r, "feittype")]


def bct_sleutel(f, afk):
    """Vergelijkingssleutel voor een feittype: zonder hoofdletters, '*', '(PKnn)', accolades en lidwoord vooraan;
    afkortingen tussen [] uitgeschreven."""
    s = f.lower().replace("*", "")
    s = re.sub(r"\s*\(pk\d+\)\s*$", "", s)
    s = re.sub(r"\[([^\]]*)\]", lambda m: "[" + afk.get(m.group(1).strip(), m.group(1).strip()) + "]", s)
    s = re.sub(r"\s*\([a-z]{1,5}\)\s*$", "", s)        # afkortingsdefinitie achter een entiteittype: 'X (PG)'
    s = re.sub(r"[-_{}]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(de|het) ", "", s)


def fm_feiten(F, afk):
    """Alle feittypen uit het FM: sleutel -> feittype, soort, waardetype, afleiding, bron, eigenaar, pk."""
    uit = {}
    def zet(f, soort, w, afl, bron, eig, pk=None):
        k = bct_sleutel(f, afk)
        if k in uit:                                    # zelfde feit met andere schrijfwijze per export
            uit[k]["bron"] |= set(bron)
        else:
            uit[k] = {"feittype": f, "soort": soort, "waardetype": w, "afleiding": afl, "bron": set(bron), "eigenaar": eig, "pk": pk}
    for nm, e in F["ET"].items():
        zet(F["ster"](nm), "entiteittype", "", F["afleiding"](nm), e["bron"], nm)
        for (a, w), br in e["attrs"].items():
            zet(f"{a} van [{nm.lower()}]", "attribuutsoort", w, "", br, nm)
    for form, g in F["PT"].items():
        zet(form, "eigenschapsoort", "", "", g["bron"], g["eigenaar"])
    for (tk, form), v in F["PK"].items():
        zet(f"{form} (PK{tk})", "productsoort", "", "", v["bron"], v.get("bij"), nr(tk))
    return uit


def bct_controle(pad, F, TK, MTKS):
    """KERN-C-BC01 t/m BC08. TK: nr -> type; MTKS: nr -> naam (leeg zonder CM)."""
    B = []
    rijen = lees_bct(pad)
    bron_bct = Path(pad).name
    plek = lambda r: f"{bron_bct} r{r['regel']}"
    afk = {}
    for r in rijen:                                     # 'POLITIEKE GROEPERING (PG)' definieert [pg]
        m = re.search(r"\(([A-Za-z]{1,5})\)\s*$", r["feittype"])
        if m and r["soort"].lower() in ("", "entiteittype"):
            afk[m.group(1).lower()] = bct_sleutel(r["feittype"], {})
    fm = fm_feiten(F, afk)
    zachte = lambda s: re.sub(r"\s+", "", (s or "").lower().replace("*", ""))
    gezien = defaultdict(list)
    for r in rijen:
        gezien[bct_sleutel(r["feittype"], afk)].append(r)
    for k, rs in gezien.items():
        if len(rs) > 1:
            B.append(("KERN-C-BC07", rs[0]["feittype"], "staat " + str(len(rs)) + " keer in de BCT (regels "
                      + ", ".join(str(r["regel"]) for r in rs) + ")", bron_bct))
    for k, v in sorted(fm.items(), key=lambda x: x[1]["feittype"].lower()):
        if k not in gezien:
            B.append(("KERN-C-BC01", v["feittype"], f"{v['soort']} staat niet in de BCT", ", ".join(sorted(v["bron"]))))
    for k, rs in gezien.items():
        r = rs[0]
        v = fm.get(k)
        if not v:
            dicht = __import__("difflib").get_close_matches(k, list(fm), n=1, cutoff=0.75)
            B.append(("KERN-C-BC02", r["feittype"], "staat niet in het FM"
                      + (f"; lijkt op '{fm[dicht[0]]['feittype']}'" if dicht else ""), plek(r)))
            continue
        if r["soort"] and r["soort"].lower() != v["soort"]:
            B.append(("KERN-C-BC03", r["feittype"], f"soort '{r['soort']}', in het FM {v['soort']}", plek(r)))
        if r["waardetype"] and v["waardetype"] and zachte(r["waardetype"]) != zachte(v["waardetype"]):
            B.append(("KERN-C-BC03", r["feittype"], f"waardetype '{r['waardetype']}', in het FM '{v['waardetype']}'", plek(r)))
        if (r["afleiding"] or v["afleiding"]) and zachte(r["afleiding"]) != zachte(v["afleiding"]):
            B.append(("KERN-C-BC03", r["feittype"], f"afleiding '{r['afleiding'] or 'leeg'}', in het FM '{v['afleiding'] or 'geen'}'", plek(r)))
        bron = {x.strip() for x in r["bron"].split(",") if x.strip()}
        if bron != v["bron"]:
            delen = [f"te veel: {', '.join(sorted(bron - v['bron']))}" if bron - v["bron"] else "",
                     f"ontbreekt: {', '.join(sorted(v['bron'] - bron))}" if v["bron"] - bron else ""]
            B.append(("KERN-C-BC04", r["feittype"], ("bron FM is leeg; in het FM: " + ", ".join(sorted(v["bron"]))) if not bron
                      else "bron FM wijkt af (" + "; ".join(d for d in delen if d) + ")", plek(r)))
        bank = nr(r["bank"]) if r["bank"] else ""
        if bank and (TK or MTKS):
            if v["soort"] == "productsoort" and v["pk"] and bank != v["pk"]:
                B.append(("KERN-C-BC06", r["feittype"], f"productsoort PK{v['pk']} staat in bank {r['bank']}, verwacht {v['pk']}", plek(r)))
            eig = F["ET"].get(v["eigenaar"]) if v["eigenaar"] else None
            if eig and v["soort"] != "productsoort":
                intern = "in" in eig["focus"]
                if intern and bank not in TK:
                    B.append(("KERN-C-BC06", r["feittype"], f"{v['eigenaar']} is in focus (intern), maar bank {r['bank']} is geen transactiesoort", plek(r)))
                elif not intern and bank in TK and bank not in MTKS:
                    B.append(("KERN-C-BC06", r["feittype"], f"{v['eigenaar']} is buiten focus (extern), maar bank {r['bank']} is een transactiesoort, geen MTK", plek(r)))
    banken = {}
    for r in rijen:
        if r["bank"]:
            banken.setdefault(nr(r["bank"]), r)
    if TK or MTKS:
        for b, r in sorted(banken.items(), key=lambda x: (not x[0].isdigit(), int(x[0]) if x[0].isdigit() else 0)):
            if b not in TK and b not in MTKS:
                B.append(("KERN-C-BC05", f"bank {r['bank']}", f"'{r['banknaam']}' is geen MTK of transactiesoort in het CM", plek(r)))
            elif b in MTKS and b not in TK and r["banknaam"] and zachte(r["banknaam"]) != zachte(MTKS[b]):
                B.append(("KERN-C-BC05", f"bank {r['bank']}", f"naam '{r['banknaam']}', in het CM MTK {b} '{MTKS[b]}'", plek(r)))
    alle = set(gezien) | set(fm)
    for r in rijen:
        if r["bank"]:
            continue
        if not r["opmerking"]:
            B.append(("KERN-C-BC08", r["feittype"], "geen bank en geen toelichting", plek(r)))
            continue
        m = re.match(r"gedekt door\s+(.+)", r["opmerking"], re.I)
        if m and bct_sleutel(m.group(1), afk) not in alle:
            B.append(("KERN-C-BC08", r["feittype"], f"'gedekt door {m.group(1)}': dat feit staat niet in de BCT of het FM", plek(r)))
    return B


def controleer(paden, begrippenlijst=None, bct=None):
    B = []                                              # (regel, element, bevinding, bron)
    data = {p: lees_json(p) for p in paden}
    soort = lambda d: {n["type"] for n in d.get("nodes", [])}
    cm_paden = [p for p, d in data.items() if soort(d) & {"transactor", "self_activation", "transaction"}]
    fm_paden = [p for p, d in data.items() if soort(d) & {"entity_type", "attribute"}]
    naam = lambda p: data[p].get("fileName", p)
    niet, overgeslagen = [], set()             # toelichting; regel-id's die niet zijn gecontroleerd

    # ---------- CM ----------
    TK, TK_BRON, RAADPLEEG, MTKS = {}, defaultdict(set), [], {}   # nr -> type; nr -> exports; (label, rol, export); nr -> naam
    for p in cm_paden:
        M, _ = tpt.lees(p)
        if not M:
            continue
        for m in M["mtk"].values():
            MTKS.setdefault(nr(m["nr"]), m["naam"])
        for i, t in M["tk"].items():
            TK.setdefault(nr(t["nr"]), t["type"])
            TK_BRON[nr(t["nr"])].add(M["bestand"])
        geinitieerd = set().union(*M["initieert"].values(), M["init_omgeving"])
        for i, t in sorted(M["tk"].items(), key=lambda x: tpt.sorteer_id(x[1]["nr"])):
            if not t["zelf"] and i not in geinitieerd:
                B.append(("KERN-C-CM01", M["tk_label"](i), f"geen initiator (uitvoerder: {t['uitvoerder']})", M["bestand"]))
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
        niet.append("CM01, TK01, TK02, TK04 en NM02: geen CM (CSD) in de exports")
        overgeslagen |= {"KERN-C-CM01", "KERN-C-TK01", "KERN-C-TK02", "KERN-C-TK04", "KERN-C-NM02"}
    if not F:
        niet.append("TK, PK, ES, AS, ET, NM01, NM03, TL02 en BG: geen feitenmodel in de exports")
        overgeslagen |= {r for r, _, _ in REGELS if r not in ("KERN-C-CM01", "KERN-C-NM02", "KERN-C-TL01")}
    if cm_paden and F:
        for n_, t in sorted(TK.items(), key=lambda x: tpt.sorteer_id(x[0])):
            if not n_.isdigit():
                B.append(("KERN-C-TK01", f"TK{n_}", "transactiesoort zonder nummer; niet te controleren", br(TK_BRON[n_])))
            elif t == "O" and n_ not in pk_nrs:
                B.append(("KERN-C-TK01", f"TK{n_}", "geen productsoort PK" + n_ + " in het FM", br(TK_BRON[n_])))
        for (tk, form), v in sorted(PK.items()):
            if nr(tk) not in TK:
                B.append(("KERN-C-TK02", f"{form} (PK{tk})", f"geen transactiesoort TK{tk} in het CM", br(v["bron"])))
            elif TK[nr(tk)] != "O":
                B.append(("KERN-C-TK02", f"{form} (PK{tk})", f"TK{tk} is van type {TK[nr(tk)]}, niet O", br(v["bron"])))
        for l, rol, bron in sorted(set(RAADPLEEG)):
            m = re.match(r"TK(\d+)", l)
            if m and nr(m.group(1)) not in pk_nrs:
                B.append(("KERN-C-TK04", l, f"{rol} raadpleegt de bank van {l}, maar PK{m.group(1)} staat niet in het FM", bron))
    for tk, forms in sorted(pk_nrs.items()):
        if len(forms) > 1:
            B.append(("KERN-C-TK03", f"PK{tk}", "meerdere formuleringen: " + " / ".join(sorted(forms)),
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
            B.append(("KERN-C-PK01", el, "productsoort hangt aan geen entiteittype", br(v["bron"])))
        elif agg and len(vs) > 1:
            mist = [c for c in comp(agg[0]) if norm(c) not in vs]
            if mist:
                B.append(("KERN-C-PK01", el, f"hangt aan aggregaat {agg[0]}; component(en) {', '.join(mist)} niet als "
                          f"variabele (variabelen: {fmt(vs)})", br(v["bron"])))
        elif not any(norm(x) in vs for x in doel):
            B.append(("KERN-C-PK01", el, f"hangt aan {', '.join(doel)}, maar de variabele is {fmt(vs)}"
                      + hint(doel[0], vs), br(v["bron"])))
        n_ok = len(comp(agg[0])) if agg else 1
        if len(vs) != n_ok or not re.search(r"\b(is|zijn)\s+\S+$", form):
            B.append(("KERN-C-PK02", el, f"{len(vs)} variabele(n), verwacht {n_ok}"
                      if len(vs) != n_ok else "eindigt niet op 'is/zijn <voltooid deelwoord>'", br(v["bron"])))

    # eigenschapsoorten
    gezien = {}
    for l in F["PT_LIJNEN"] if F else []:
        gezien.setdefault((l["form"], l["van"], l["naar"], l["kard_van"], l["kard_naar"]), set()).add(l["bron"])
    for (form, van, naar, kv, kn), bron in sorted(gezien.items(), key=lambda x: (x[0][0].lower(), x[0][1:3])):
        el = form or f"(geen formulering: {van} → {naar})"
        vs = var(form)
        if not form:
            B.append(("KERN-C-ES01", el, "eigenschapsoort zonder formulering", br(bron)))
        elif form.count("[") != form.count("]"):
            B.append(("KERN-C-ES01", el, "haken [ ] niet in evenwicht", br(bron)))
        else:
            mist = [x for x in dict.fromkeys((van, naar)) if norm(x) not in vs]
            if van == naar and len(vs) < 2:
                mist = [van]
            if mist:
                B.append(("KERN-C-ES01", el, f"{' en '.join(mist)} niet als variabele in de formulering "
                          f"(variabelen: {fmt(vs)})" + "".join(hint(x, vs) for x in mist), br(bron)))
        if not feittypen.max1(kn):
            B.append(("KERN-C-ES02", el, f"{van} → {naar}: doelkant is '{kn or 'leeg'}', verwacht 0..1 of 1..1", br(bron)))
        if not kv:
            B.append(("KERN-C-ES03", el, f"{van} → {naar}: kardinaliteit aan de bronkant ontbreekt", br(bron)))

    # attribuutsoorten
    for nm, e in sorted(ET.items()):
        per_naam = defaultdict(set)
        for (a, w), bron in e["attrs"].items():
            per_naam[a.lower()].add(w)
            if not w:
                B.append(("KERN-C-AS01", f"{a} van [{nm.lower()}]", "geen waardetype", br(bron)))
        for a in sorted(e["dubbel"]):
            B.append(("KERN-C-AS02", f"{a} van [{nm.lower()}]", "komt meer dan één keer voor in hetzelfde blok", br(e["bron"])))
        for a, ws in sorted(per_naam.items()):
            if len(ws - {""}) > 1:
                B.append(("KERN-C-AS02", f"{a} van [{nm.lower()}]", "verschillende waardetypen: " + ", ".join(sorted(ws - {""})), br(e["bron"])))

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
            B.append(("KERN-C-ET01", ster(nm), "focus verschilt per diagram: " + "; ".join(
                f"{k or 'geen'} ({', '.join(sorted(v))})" for k, v in sorted(f.items())), br(e["bron"])))
        if "in" in f and not heeft_pk[nm]:              # een productsoort aan een extern entiteittype mag wel
            B.append(("KERN-C-ET01", ster(nm), "in focus (intern) maar geen productsoort", br(e["bron"])))
    for nm, e in sorted(ET.items()):
        if not e["attrs"] and nm not in in_pt and not heeft_pk[nm] and nm not in in_afl:
            B.append(("KERN-C-ET02", ster(nm), "geen eigenschap-, attribuut- of productsoort en geen afleiding", br(e["bron"])))

    # namen en hygiëne
    for canon, namen in (F["conflicten"] if F else []):
        B.append(("KERN-C-NM01", canon, "heet ook: " + "; ".join(f"{n} ({', '.join(k)})" for n, k in namen.items() if n != canon),
                  br(set().union(*namen.values()))))
    def labels(paden, soorten, tekst):
        """Node-id's van de gegeven soorten met per export een ander label: {id: {label: {exports}}}."""
        per = defaultdict(lambda: defaultdict(set))
        for p in paden:
            nodes = data[p].get("nodes", [])
            kind = defaultdict(list)
            for n in nodes:
                if n.get("parentId"):
                    kind[n["parentId"]].append(n)
            for n in nodes:
                if n["type"] in soorten:
                    per[n["id"]][tekst(n, kind)].add(naam(p))
        return [l for l in per.values() if len(l) > 1]
    SOORT = {"transaction": "transactiesoort", "actor": "actorrol", "multiple_transaction_kind": "MTK"}
    def cm_tekst(n, kind):
        t = " ".join(tpt.tekstregels(n["data"].get("content")))
        return f"{SOORT[n['type']]} {'TK' if n['type'] == 'transaction' else ''}{t}"
    def pk_tekst(n, kind):
        txt = [k for k in kind[n["id"]] if k["type"] == "text"]
        form = feittypen.schoon(feittypen.plak(feittypen.regels(feittypen.inhoud(txt[0]).get("body")))) if txt else ""
        return f"{form or '(geen formulering)'} (PK{''.join(feittypen.regels(feittypen.inhoud(n).get('body')))})"
    for regel, paden, soorten, tekst in (("KERN-C-NM02", cm_paden, set(SOORT), cm_tekst),
                                         ("KERN-C-NM03", fm_paden, {"production_event"}, pk_tekst)):
        for l in labels(paden, soorten, tekst):
            meest = max(l, key=lambda x: len(l[x]))
            B.append((regel, meest, "label verschilt per diagram: " + "; ".join(
                f"{x} ({', '.join(sorted(e))})" for x, e in sorted(l.items())), br(set().union(*l.values()))))
    overal = {n["id"] for d in data.values() for n in d.get("nodes", [])}
    for p, d in data.items():
        ids = {n["id"] for n in d.get("nodes", [])}
        los = [e for e in d.get("edges", []) if e["source"] not in ids or e["target"] not in ids]
        if los:
            elders = sum(1 for e in los if all(x in overal for x in (e["source"], e["target"])))
            B.append(("KERN-C-TL01", naam(p), f"{len(los)} edges naar ontbrekende nodes"
                      + (f", waarvan {elders} naar nodes in een andere export" if elders else ""), naam(p)))
    for kort, i, nm in (F["kop_a"] if F else []):
        B.append(("KERN-C-TL02", nm, f"entiteittype met kop 'A' (node {i})", kort))

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
                B.append(("KERN-C-BG01", ster(nm), "geen begrip gevonden (op term, kern of synoniem)", bron_lijst))
            else:
                exact = [t for t in term[nm] if t.lower() == nm.lower()]
                if not exact:
                    B.append(("KERN-C-BG01", ster(nm), "gekoppeld aan " + ", ".join(sorted(term[nm]))
                              + " (schrijfwijze of kwalificatie verschilt)", bron_lijst))
        for (s, x), ys in sorted(AFL.items()):
            if not ys or x not in ET or not term[x]:
                continue
            tx = sorted(term[x])
            if s == "specialisatie":
                ouders = termen(ys)
                genus = set().union(*(uit[t]["genus"] for t in tx))
                if not ouders:
                    B.append(("KERN-C-BG02", ster(x), f"ouder {', '.join(sorted(ys))} heeft geen begrip", bron_lijst))
                elif not genus & ouders:
                    B.append(("KERN-C-BG02", ster(x), f"FM: specialisatie van {', '.join(sorted(ys))}; genus in de definitie: "
                              + (", ".join(sorted(genus)) or "niet herkend"), bron_lijst))
            elif s == "generalisatie":
                leden = termen(ys)
                ops = set().union(*(uit[t]["opsomming"] for t in tx))
                if ops != leden:
                    B.append(("KERN-C-BG03", ster(x), f"FM: generalisatie van {', '.join(sorted(ys))}; opsomming in de definitie: "
                              + (", ".join(sorted(ops)) or "geen"), bron_lijst))
            elif s == "aggregatie":
                comp = termen(ys)
                alle = set().union(*(set().union(*uit[t].values()) for t in tx))
                mist = sorted(comp - alle)
                if mist or len(comp) < len(ys):
                    B.append(("KERN-C-BG04", ster(x), f"FM: aggregatie van {' × '.join(sorted(ys))}; definitie verwijst niet naar "
                              + ", ".join(mist + [y for y in sorted(ys) if not term.get(y)]), bron_lijst))
        gen = {x for (s, x), ys in AFL.items() if s == "generalisatie" and ys}
        for nm in sorted(ET):
            for t in sorted(term[nm]):
                if uit[t]["opsomming"] and nm not in gen:
                    B.append(("KERN-C-BG03", ster(nm), f"definitie van '{t}' is een opsomming ("
                              + ", ".join(sorted(uit[t]["opsomming"])) + "), maar het FM heeft geen generalisatie", bron_lijst))
        for l in sorted({(l["van"], l["naar"], l["form"]) for l in F["PT_LIJNEN"]}):
            van, naar, form = l
            if van == naar or not term.get(van) or not term.get(naar):
                continue
            alle = set().union(*(set().union(*uit[t].values()) for t in term[van]))
            if not alle & term[naar]:
                B.append(("KERN-C-BG05", form or f"{van} → {naar}", f"definitie van {', '.join(sorted(term[van]))} "
                          f"verwijst niet naar {', '.join(sorted(term[naar]))}", bron_lijst))
        gekoppeld = set().union(*term.values()) if term else set()
        # BG06 in drie groepen: in een ander feittype, alleen in andere definities, of nergens gebruikt
        feiten = [norm(v["feittype"]) for v in fm_feiten(F, {}).values() if v["soort"] != "entiteittype"]
        gebruikt = {r["doel"] for r in randen if r["bron"] != r["doel"]}
        groepen = {"in een feittype": [], "alleen in andere definities": [], "nergens gebruikt": []}
        for b in begrippen:
            if b["term"] in gekoppeld:
                continue
            vormen = {v for n_ in [b["term"], graaf.kern(b["term"])] + b["synoniemen"] for v in graaf.varianten(norm(n_))}
            if any(re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", f) for v in vormen for f in feiten):
                groepen["in een feittype"].append(b["term"])
            elif b["term"] in gebruikt:
                groepen["alleen in andere definities"].append(b["term"])
            else:
                groepen["nergens gebruikt"].append(b["term"])
        for g, los in groepen.items():
            if los:
                B.append(("KERN-C-BG06", f"{g} ({len(los)})", ", ".join(los), bron_lijst))
    elif begrippenlijst:
        pass                                            # al gemeld: geen feitenmodel
    else:
        niet.append("BG01 t/m BG06: geen begrippenlijst opgegeven (-b)")
        overgeslagen |= {r for r, _, _ in REGELS if r.startswith("KERN-C-BG")}

    # ---------- BCT ----------
    if bct and F:
        B += bct_controle(bct, F, TK if cm_paden else {}, MTKS)
        if not cm_paden:
            niet.append("BC05 en BC06: geen CM in de exports")
            overgeslagen |= {"KERN-C-BC05", "KERN-C-BC06"}
    elif not bct:
        niet.append("BC01 t/m BC08: geen BCT opgegeven (-t)")
        overgeslagen |= {r for r, _, _ in REGELS if r.startswith("KERN-C-BC")}
    onbekend ={b[0] for b in B} - {r[0] for r in REGELS}
    if onbekend:
        sys.exit(f"Regel-id's niet in references/regels.csv: {', '.join(sorted(onbekend))}")
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
    p.add_argument("-t", "--bct", help="bankcontactentabel (CSV, één feittype per regel; zie docs/yadm-consistency.md)")
    p.add_argument("-o", "--output", help="schrijf het resultaat ook naar dit Markdown-bestand")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tekst = "\n".join(rapport(*controleer(args.exports, args.begrippen, args.bct)))
    print(tekst)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tekst + "\n")


if __name__ == "__main__":
    main()
