#!/usr/bin/env python3
"""
cofactores_metagenomas.py

Reimplementacion de la logica de modify_sbmlv2.py (B. Ulloa)
SIN pasar por cobra.io.read_sbml_model / write_sbml_model. Trabaja directo
sobre el arbol XML con lxml, para poder procesar modelos SBML de
metagenoma completo (cientos de MB) sin colgarse.

Uso:
    from cofactores_metagenomas import curar_sbml
    curar_sbml("in.sbml", "cofactors.tsv", "out.sbml", verbose=True)
"""

import csv
import os
import time
from copy import deepcopy
from lxml import etree


def sbml_escape(raw_id: str) -> str:
    out = []
    for ch in raw_id:
        if ch.isalnum() or ch == "_":
            out.append(ch)
        else:
            out.append(f"__{ord(ch)}__")
    return "".join(out)


def cofactor_to_species_id(cof_id: str) -> str:
    return "M_" + sbml_escape(cof_id)


def load_cofactor_adjacency(cofactors_tsv: str):
    adjacency = {}

    def add_edge(a, b):
        a_sid = cofactor_to_species_id(a)
        b_sid = cofactor_to_species_id(b)
        adjacency.setdefault(a_sid, set()).add(b_sid)

    with open(cofactors_tsv, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            c1 = row["Cofactor_1"].strip()
            c2 = row["Cofactor_2"].strip()
            if not c1 or not c2:
                continue
            add_edge(c1, c2)
            add_edge(c2, c1)

    return adjacency


def curar_sbml(input_sbml: str, cofactors_tsv: str, output_sbml: str, verbose: bool = True):
    t0 = time.time()

    def log(msg):
        if verbose:
            print(f"[{time.time()-t0:7.1f}s] {msg}")

    log(f"Cargando pares de cofactores desde {cofactors_tsv} ...")
    adjacency = load_cofactor_adjacency(cofactors_tsv)
    log(f"  {sum(len(v) for v in adjacency.values())} relaciones cofactor cargadas.")

    log(f"Parseando SBML: {input_sbml} ...")
    parser = etree.XMLParser(huge_tree=True, remove_blank_text=False)
    tree = etree.parse(input_sbml, parser=parser)
    root = tree.getroot()
    log(f"  Parseo completo. Tamaño del archivo: {os.path.getsize(input_sbml)/1e6:.1f} MB")

    nsmap = root.nsmap
    sbml_ns = nsmap.get(None)
    if sbml_ns is None:
        raise RuntimeError("No se encontró namespace SBML por defecto en el archivo.")
    fbc_ns = None
    for prefix, uri in nsmap.items():
        if uri and "fbc" in uri:
            fbc_ns = uri
            break

    def tag(local_name, ns=sbml_ns):
        return f"{{{ns}}}{local_name}"

    model = root.find(tag("model"))
    if model is None:
        raise RuntimeError("No se encontró <model> en el SBML.")

    list_of_species = model.find(tag("listOfSpecies"))
    list_of_reactions = model.find(tag("listOfReactions"))
    if list_of_species is None or list_of_reactions is None:
        raise RuntimeError("No se encontró listOfSpecies o listOfReactions.")

    list_of_flux_bounds = None
    if fbc_ns is not None:
        list_of_flux_bounds = model.find(tag("listOfFluxBounds", fbc_ns))

    log("Indexando especies y reacciones ...")
    species_by_id = {}
    for sp in list_of_species.findall(tag("species")):
        sid = sp.get("id")
        if sid:
            species_by_id[sid] = sp

    n_reactions_original = 0
    reactions_info = []
    for rxn in list_of_reactions.findall(tag("reaction")):
        n_reactions_original += 1
        reactant_ids, product_ids = set(), set()

        lor = rxn.find(tag("listOfReactants"))
        if lor is not None:
            for sref in lor.findall(tag("speciesReference")):
                sp_id = sref.get("species")
                if sp_id:
                    reactant_ids.add(sp_id)

        lop = rxn.find(tag("listOfProducts"))
        if lop is not None:
            for sref in lop.findall(tag("speciesReference")):
                sp_id = sref.get("species")
                if sp_id:
                    product_ids.add(sp_id)

        reactions_info.append((rxn, reactant_ids, product_ids))

    log(f"  {n_reactions_original} reacciones, {len(species_by_id)} especies indexadas.")

    flux_bounds_by_reaction = {}
    if list_of_flux_bounds is not None:
        for fb in list_of_flux_bounds.findall(tag("fluxBound", fbc_ns)):
            rxn_id = fb.get(f"{{{fbc_ns}}}reaction")
            flux_bounds_by_reaction.setdefault(rxn_id, []).append(fb)
        log(f"  Bloque fbc:listOfFluxBounds encontrado ({len(flux_bounds_by_reaction)} reacciones con bounds).")
    else:
        log("  No se encontró fbc:listOfFluxBounds global (bounds embebidos por reacción, se copian solos).")

    log("Iniciando curación de cofactores ...")
    new_species_created = {}
    new_reactions = []
    new_flux_bounds = []
    n_matched_reactions = 0

    def get_or_create_cof_species(original_species_id):
        new_id = original_species_id + "__cof__"
        if new_id not in new_species_created:
            orig_el = species_by_id.get(original_species_id)
            if orig_el is None:
                return None
            new_el = deepcopy(orig_el)
            new_el.set("id", new_id)
            if new_el.get("name") is not None:
                new_el.set("name", new_el.get("name") + "__cof__")
            if new_el.get("metaid") is not None:
                new_el.set("metaid", new_el.get("metaid") + "__cof__")
            new_species_created[new_id] = new_el
        return new_id

    for idx, (rxn, reactant_ids, product_ids) in enumerate(reactions_info):
        if verbose and idx % 2000 == 0 and idx > 0:
            log(f"  ... procesadas {idx}/{n_reactions_original} reacciones "
                f"({n_matched_reactions} con cofactores hasta ahora)")

        replacements = {}
        for prod_sid in product_ids:
            partners = adjacency.get(prod_sid)
            if not partners:
                continue
            for partner_sid in partners:
                if partner_sid in reactant_ids:
                    new_prod_id = get_or_create_cof_species(prod_sid)
                    new_react_id = get_or_create_cof_species(partner_sid)
                    if new_prod_id and new_react_id:
                        replacements[prod_sid] = new_prod_id
                        replacements[partner_sid] = new_react_id

        if not replacements:
            continue

        n_matched_reactions += 1
        orig_id = rxn.get("id")
        orig_name = rxn.get("name")

        new_rxn = deepcopy(rxn)
        new_rxn.set("id", orig_id + "__cof__")
        if orig_name is not None:
            new_rxn.set("name", (orig_name or "") + "__cof__")
        if new_rxn.get("metaid") is not None:
            new_rxn.set("metaid", new_rxn.get("metaid") + "__cof__")

        notes_el = new_rxn.find(tag("notes"))
        if notes_el is not None:
            new_rxn.remove(notes_el)

        for list_tag in ("listOfReactants", "listOfProducts"):
            lst = new_rxn.find(tag(list_tag))
            if lst is None:
                continue
            for sref in lst.findall(tag("speciesReference")):
                sp_id = sref.get("species")
                if sp_id in replacements:
                    sref.set("species", replacements[sp_id])

        new_reactions.append(new_rxn)

        if list_of_flux_bounds is not None:
            for fb in flux_bounds_by_reaction.get(orig_id, []):
                new_fb = deepcopy(fb)
                new_fb.set(f"{{{fbc_ns}}}reaction", orig_id + "__cof__")
                new_flux_bounds.append(new_fb)

    log(f"Curación lógica completa: {n_matched_reactions} reacciones con cofactores detectadas.")
    log(f"  Especies nuevas: {len(new_species_created)}")
    log(f"  Reacciones nuevas: {len(new_reactions)}")
    log(f"  FluxBounds nuevos: {len(new_flux_bounds)}")

    log("Insertando nuevos elementos en el árbol XML ...")
    for sp_el in new_species_created.values():
        list_of_species.append(sp_el)
    for rxn_el in new_reactions:
        list_of_reactions.append(rxn_el)
    if list_of_flux_bounds is not None:
        for fb_el in new_flux_bounds:
            list_of_flux_bounds.append(fb_el)

    out_dir = os.path.dirname(output_sbml)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    log(f"Escribiendo SBML curado en {output_sbml} ...")
    tree.write(output_sbml, xml_declaration=True, encoding="UTF-8", pretty_print=False)
    log(f"  Listo. Tamaño de salida: {os.path.getsize(output_sbml)/1e6:.1f} MB")
    log(f"TOTAL: {time.time()-t0:.1f} s")

    return {
        "n_reactions_original": n_reactions_original,
        "n_reactions_matched": n_matched_reactions,
        "n_new_species": len(new_species_created),
        "n_new_reactions": len(new_reactions),
    }