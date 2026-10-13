"""Transactiesoorten, actorrollen en MTK's uit een YADM-export (DEMO-model, JSON) halen.

  python tpt.py "<export>.json" [meer exports ...] [-o uitvoer.md]

Leest het Cooperation Structure Diagram (CSD) in de export en schrijft per bestand:
- een tabel transactiesoorten: ID · Type · Uitvoerder · Initieert · Raadpleegt
- een tabel MTK's: ID · Naam
- opmerkingen: aannames, genormaliseerde namen, zwevende edges, ontbrekende nummers

Interpretatie van de export (React Flow-formaat: 'nodes' en 'edges'):
- 'transactor' (en 'self_activation') is een container met een 'transaction' (TK-nummer)
  en een 'actor' (rolnaam) als kinderen via 'parentId'; de actorrol is uitvoerder van de TK.
  Bij 'self_activation' is de actorrol ook initiator van die TK (zelfactiverend).
- edge met lineType 'solid' naar een 'transaction': initiatorlink (bron initieert de TK).
- edge met lineType 'dashed' tussen een actorrol en een 'multiple_transaction_kind' of
  'transaction': informatielink (de rol raadpleegt de MTK of de bank van de TK).
- data.color van een 'transaction': 'green' = I(nformationeel), 'blue' = D(ocumenteel),
  'red' = O(rigineel); 'default' of geen kleur = O (aanname: standaardkleur van de tool is rood).
- edges waarvan een eindpunt geen node in de export is, worden als zwevend gemeld en genegeerd.
"""

import argparse
import json
import re
import sys
from collections import defaultdict

KLEUR = {"green": "I", "blue": "D", "red": "O"}


def tekstregels(content):
    """Inhoud van een node als lijst regels (header en body samen)."""
    if not content:
        return []
    if isinstance(content, str):
        delen = [content]
    else:
        delen = [content.get("header") or "", content.get("body") or ""]
    regels = []
    for d in delen:
        regels += [r.strip() for r in str(d).split("\n") if r.strip()]
    return regels


def plak(regels, log, wat):
    """Regels samenvoegen; een afbreekstreepje aan het eind van een regel verdwijnt,
    behalve na een woord met een hoofdletter (KvK-gegevens, Napp-gegevens)."""
    uit = ""
    for r in regels:
        if not uit:
            uit = r
        elif uit.endswith("-"):
            laatste = re.split(r"\s", uit)[-1]
            if any(c.isupper() for c in laatste):
                uit += r
            else:
                uit = uit[:-1] + r
        else:
            uit += " " + r
    if any(r.endswith("-") for r in regels[:-1]):
        log.append(f"{wat}: '{' ⏎ '.join(regels)}' → '{uit}'")
    return uit


def sorteer_id(i):
    return (not i.isdigit(), int(i) if i.isdigit() else 0, i)


def lees(pad):
    """CSD uit één export als dict (zie het einde van deze functie) plus opmerkingen; None zonder CSD."""
    with open(pad, encoding="utf-8-sig") as f:
        d = json.load(f)
    nodes = {n["id"]: n for n in d.get("nodes", [])}
    edges = d.get("edges", [])
    log_namen, opm = [], []

    kinderen = defaultdict(list)
    for n in nodes.values():
        if n.get("parentId"):
            kinderen[n["parentId"]].append(n)

    tk = {}          # transaction-node-id -> gegevens
    rol = {}         # actor-node-id -> naam
    for c in nodes.values():
        if c["type"] not in ("transactor", "self_activation"):
            continue
        t = [k for k in kinderen[c["id"]] if k["type"] == "transaction"]
        a = [k for k in kinderen[c["id"]] if k["type"] == "actor"]
        if not t or not a:
            opm.append(f"Container {c['type']} zonder transactie of actorrol ({c['id'][:8]}) overgeslagen.")
            continue
        t, a = t[0], a[0]
        rol[a["id"]] = plak(tekstregels(a["data"].get("content")), log_namen, "actorrol")
        kleur = t["data"].get("color", "default")
        tk[t["id"]] = {
            "nr": " ".join(tekstregels(t["data"].get("content"))) or "?",
            "type": KLEUR.get(kleur, "O"),
            "kleur": kleur,
            "uitvoerder": rol[a["id"]],
            "uitvoerder_id": a["id"],
            "zelf": c["type"] == "self_activation",
        }

    mtk = {}
    for n in nodes.values():
        if n["type"] == "multiple_transaction_kind":
            regels = tekstregels(n["data"].get("content"))
            nr, naam = (regels[0], plak(regels[1:], log_namen, "MTK")) if regels else ("?", "")
            mtk[n["id"]] = {"nr": nr, "naam": naam}
    samengesteld = {n["id"]: " ".join(tekstregels(n["data"].get("content"))) for n in nodes.values()
                    if n["type"] == "composite"}

    if not tk and not mtk:
        return None, [f"Geen CSD-elementen (transactiesoorten of MTK's) gevonden in {pad}."]

    # labels; 'xx' (nog geen nummer) onderscheiden met uitvoerder of naam
    def tk_label(i):
        t = tk[i]
        return f"TK{t['nr']}" + (f" ({t['uitvoerder']})" if not t["nr"].isdigit() else "")

    def mtk_label(i):
        m = mtk[i]
        return f"MTK {m['nr']}" + (f" ({m['naam']})" if not m["nr"].isdigit() else "")

    initieert = defaultdict(set)   # rol-node-id -> {tk-id}
    raadpleegt = defaultdict(set)  # rol-node-id -> {label}
    zwevend = []
    for e in edges:
        s, t, lijn = e["source"], e["target"], (e.get("data") or {}).get("lineType")
        if s not in nodes or t not in nodes:
            soorten = [x.rsplit("_", 1)[0] for x in e["id"].split("->")] if "->" in e["id"] else ["?", "?"]
            bekend = [nodes[x]["type"] for x in (s, t) if x in nodes]
            zwevend.append(f"{soorten[0]} → {soorten[-1]} ({lijn}); "
                           + ("bestaand eindpunt: " + ", ".join(bekend) if bekend else "geen bestaand eindpunt"))
            continue
        ts, tt = nodes[s]["type"], nodes[t]["type"]
        if lijn == "solid" and tt == "transaction" and t in tk:
            if s in rol:
                initieert[s].add(t)
            elif s in samengesteld:
                opm.append(f"{tk_label(t)} wordt geïnitieerd door de samengestelde actorrol "
                           f"'{samengesteld[s]}' (omgeving); die heeft geen eigen rij.")
            else:
                opm.append(f"Initiatorlink van onbekend type '{ts}' naar {tk_label(t)} genegeerd.")
        elif lijn == "dashed":
            a, b = (s, t) if s in rol else (t, s)
            if a not in rol:
                opm.append(f"Informatielink tussen '{ts}' en '{tt}' zonder actorrol genegeerd.")
            elif b in mtk:
                raadpleegt[a].add(mtk_label(b))
            elif b in tk:
                raadpleegt[a].add(tk_label(b))
            else:
                opm.append(f"Informatielink van '{rol[a]}' naar '{nodes[b]['type']}' genegeerd.")
        else:
            opm.append(f"Edge {ts} → {tt} ({lijn}) niet geïnterpreteerd.")

    return {"bestand": d.get("fileName", pad), "tk": tk, "mtk": mtk, "tk_label": tk_label,
            "mtk_label": mtk_label, "initieert": initieert, "raadpleegt": raadpleegt,
            "zwevend": zwevend, "log_namen": log_namen}, opm


def verwerk(pad):
    M, opm = lees(pad)
    if M is None:
        return None, opm
    tk, mtk, tk_label, mtk_label = M["tk"], M["mtk"], M["tk_label"], M["mtk_label"]
    initieert, raadpleegt, zwevend, log_namen = M["initieert"], M["raadpleegt"], M["zwevend"], M["log_namen"]

    def sorteer_label(lbl):
        m = re.match(r"(MTK |TK)(\w+)", lbl)
        return (lbl.startswith("TK"), sorteer_id(m.group(2)) if m else (True, 0, lbl), lbl)

    rijen = []
    for i, t in sorted(tk.items(), key=lambda x: (sorteer_id(x[1]["nr"]), x[1]["uitvoerder"])):
        init = sorted(initieert[t["uitvoerder_id"]], key=lambda x: (sorteer_id(tk[x]["nr"]), tk[x]["uitvoerder"]))
        init_lbl = [tk_label(x) + (" (zelfactiverend)" if x == i and t["zelf"] else "") for x in init]
        if t["zelf"] and i not in init:
            init_lbl.insert(0, f"{tk_label(i)} (zelfactiverend)")
        rijen.append((f"TK{t['nr']}", t["type"], t["uitvoerder"], ", ".join(init_lbl),
                      ", ".join(sorted(raadpleegt[t["uitvoerder_id"]], key=sorteer_label))))

    uit = [f"## {M['bestand']}", "", "### Transactiesoorten", "",
           "| ID | Type | Uitvoerder | Initieert | Raadpleegt |", "|---|---|---|---|---|"]
    uit += [f"| {' | '.join(r)} |" for r in rijen]
    uit += ["", "### MTK's", "", "| ID | Naam |", "|---|---|"]
    uit += [f"| {m['nr']} | {m['naam']} |" for m in sorted(mtk.values(), key=lambda m: (sorteer_id(m["nr"]), m["naam"]))]

    # opmerkingen
    standaard = [tk_label(i) for i, t in tk.items() if t["kleur"] not in KLEUR]
    if standaard:
        opm.insert(0, f"Type O aangenomen voor transactiesoorten zonder expliciete kleur (standaardkleur = rood): "
                      f"{', '.join(sorted(standaard))}.")
    zonder_nr = [tk_label(i) for i, t in tk.items() if not t["nr"].isdigit()] + \
                [mtk_label(i) for i, m in mtk.items() if not m["nr"].isdigit()]
    if zonder_nr:
        opm.append(f"Nog geen nummer: {', '.join(zonder_nr)}.")
    if zwevend:
        opm.append(f"{len(zwevend)} zwevende edges (eindpunt bestaat niet in de export) genegeerd:")
        opm += [f"  - {z}" for z in zwevend]
    if log_namen:
        opm.append("Afbreekstreepjes aan het eind van een regel verwerkt (controleer de schrijfwijze):")
        opm += [f"  - {l}" for l in log_namen]
    return uit, opm


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("exports", nargs="+", help="YADM-export(s) in JSON")
    p.add_argument("-o", "--output", help="schrijf de tabellen ook naar dit Markdown-bestand")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    alles = []
    for pad in args.exports:
        tabellen, opm = verwerk(pad)
        if tabellen:
            alles += tabellen
        if opm:
            alles += ["", "### Opmerkingen", ""] + [o if o.startswith("  ") else f"- {o}" for o in opm]
        alles.append("")
    tekst = "\n".join(alles)
    print(tekst)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
