#!/usr/bin/env python3
"""Validate conditional rules of the proposed ModelCIF annotation module.

Run CifCheck with the assembled dictionary first: this checker supplements DDL2
(types, keys, enumerations and parent links); it is not a deposition validator or
an interpreter of arbitrary custom scientific definitions.
"""
import argparse
from collections import Counter, defaultdict
import math
import sys
import gemmi

PREFIX = '_ma_annotation_'
CANONICAL28 = set('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL A C G U DA DC DG DT'.split())
SCALAR = dict(real='value_real', integer='value_integer', boolean='value_boolean', text='value_text', component='value_comp_id')
PAYLOAD = set(SCALAR.values()) | {'x', 'y', 'z', 'array_id', 'value_group_id', 'frame_id'}
CARRIERS = ('atom', 'residue', 'chain', 'group_value', 'system', 'site_value', 'pair')
TOLERANCE = 1e-6


def records(block, category):
    data = block.get_mmcif_category('_' + category + '.')
    if not data:
        return []
    return [{k: (v[i] if isinstance(v[i], str) else None) for k, v in data.items()}
            for i in range(len(next(iter(data.values()))))]


def validate(block):
    """Return diagnostics for one block; structural/DDL validation is separate."""
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    def rows(cat):
        return records(block, 'ma_annotation_' + cat)
    def idx(cat, key='id', standard=False):
        rr = records(block, cat) if standard else rows(cat)
        check(len({r.get(key) for r in rr}) == len(rr), f'{cat}: duplicate {key}')
        return {r.get(key): r for r in rr}
    def num(v, message, integer=False):
        try:
            n = int(v) if integer else float(v)
            if not math.isfinite(n):
                raise ValueError()
            return n
        except (ValueError, TypeError, OverflowError):
            errors.append(message)
            return 0
    def get(table, ident, message):
        check(ident in table, message)
        return table.get(ident, {})
    def selected(row, fields):
        return {k for k in fields if row.get(k) is not None}
    defs, sets, frames = idx('definition'), idx('set'), idx('frame')
    groups, sites, subjects = idx('group'), idx('site'), idx('subject')
    domains, arrays = idx('domain'), idx('array')
    atoms = idx('atom_site', standard=True)
    models = idx('ma_model_list', 'ordinal_id', True)
    data = idx('ma_data', standard=True)
    chains = idx('struct_asym', standard=True)
    seq = {(r.get('entity_id'), r.get('num')) for r in records(block, 'entity_poly_seq')}
    components = idx('chem_comp', standard=True)
    steps = idx('ma_protocol_step', 'ordinal_id', True)
    data_groups = defaultdict(set)
    for r in records(block, 'ma_data_group'):
        data_groups[r.get('group_id')].add(r.get('data_id'))
    domain_values = defaultdict(dict)
    for r in rows('domain_value'):
        dd = get(domains, r.get('domain_id'), 'domain_value: missing domain')
        check(r.get('code') not in domain_values[r.get('domain_id')], 'domain_value: duplicate code')
        domain_values[r.get('domain_id')][r.get('code')] = r
        check((dd.get('kind') == 'component') == bool(r.get('comp_id')), 'domain_value: kind/component mismatch')
        if r.get('comp_id'):
            check(r['comp_id'] in components, 'domain_value: missing chem_comp')
    for ident, dd in domains.items():
        vv = domain_values[ident]
        check(bool(vv), 'domain: closed domain has no members')
        if dd.get('kind') == 'component':
            check(len({v.get('comp_id') for v in vv.values()}) == len(vv), 'domain: duplicate component identity')
    meanings = set()
    def_axes = defaultdict(list)
    for r in rows('definition_axis'):
        get(defs, r.get('definition_id'), 'definition_axis: missing definition')
        def_axes[r.get('definition_id')].append(r)
    for ident, d in defs.items():
        meaning = (d.get('definition_key'), d.get('version'))
        check(meaning not in meanings, 'definition: duplicate scientific key/version')
        meanings.add(meaning)
        check(':' in (d.get('definition_key') or ''), 'definition: key needs a namespace')
        order = num(d.get('body_order'), 'definition: body_order must be integer', True)
        check((order == 0) == (d.get('subject_level') == 'system'), 'definition: system iff zero-body')
        check((order == 2) == bool(d.get('symmetric')), 'definition: symmetric only and always for pairs')
        kind = d.get('value_kind')
        arrfields = selected(d, {'array_rank', 'array_element_kind', 'array_transform'})
        check(arrfields == ({'array_rank', 'array_element_kind', 'array_transform'} if kind == 'array' else set()), 'definition: array metadata mismatch')
        if kind == 'array':
            rank = num(d.get('array_rank'), 'definition: invalid array rank', True)
            check(rank > 0, 'definition: array rank must be positive')
            aa = def_axes[ident]
            check(sorted(num(a.get('axis_order'), 'definition_axis: invalid order', True) for a in aa) == list(range(1, rank + 1)), 'definition: incomplete or duplicate axes')
            for a in aa:
                if a.get('length'):
                    check(num(a['length'], 'definition_axis: invalid length', True) >= 0, 'definition_axis: negative length')
        else:
            check(not def_axes[ident], 'definition: axes on a non-array')
        if kind in ('boolean', 'text', 'component', 'group'):
            check(d.get('units') == 'none', 'definition: nonnumeric values must use units none')
        if kind == 'point3' or (kind == 'array' and d.get('array_transform') == 'point3'):
            check(d.get('units') == 'angstroms', 'definition: point coordinates use angstroms')
        if d.get('units') not in ('none', 'angstroms'):
            check(bool(d.get('units_details')), 'definition: other units require units_details')
        domain = domains.get(d.get('domain_id'))
        if d.get('domain_id'):
            check(domain is not None, 'definition: missing domain')
            check((d.get('parameter_kind') == 'component' or kind == 'component') == (domain and domain.get('kind') == 'component'), 'definition: incompatible domain kind')
            check(kind in ('text', 'component') or d.get('parameter_kind') == 'component', 'definition: domains use text/component or component parameters')
        key = d.get('definition_key')
        standard = {'proposal:coordinate': ('atom', 'point3', 'angstroms'),
                    'proposal:sequence_probability': ('residue', 'real', 'none'),
                    'proposal:sequence_identity': ('residue', 'component', 'none')}
        if key in standard:
            check((d.get('subject_level'), kind, d.get('units')) == standard[key] and order == 1 and d.get('version') == 'draft-1' and d.get('omitted_state') == 'unconstrained', 'definition: shared term metadata changed')
            check(not d.get('domain_id'), 'definition: shared term has fixed domain; use a custom key for another domain')
        if key == 'proposal:sequence_probability':
            check(d.get('parameter_kind') == 'component', 'definition: probability needs component parameter')
        elif key in standard:
            check(d.get('parameter_kind') in (None, 'none'), 'definition: shared term has no component parameter')
        elif d.get('parameter_kind') == 'component':
            check(domain and domain.get('kind') == 'component', 'definition: custom component parameter requires complete domain')
    for s in sets.values():
        check(s.get('data_id') in data, 'set: missing data')
        if s.get('model_id'):
            check(s['model_id'] in models, 'set: missing model')
    for f in frames.values():
        check((f.get('kind') == 'model Cartesian') == bool(f.get('model_id')), 'frame: kind/model mismatch')
        if f.get('model_id'):
            check(f['model_id'] in models, 'frame: missing model')

    def scope(row, label):
        check(row.get('data_id') in data, label + ': missing data')
        if row.get('model_id'):
            m = get(models, row['model_id'], label + ': missing model')
            check(m.get('data_id') == row.get('data_id'), label + ': model/data mismatch')
    def structural(row, model, label):
        check(model in models, label + ': structural subject needs model')
        if row.get('atom_id'):
            a = get(atoms, row['atom_id'], label + ': missing atom')
            check(a.get('pdbx_PDB_model_num') == model, label + ': atom outside model')
        if row.get('label_asym_id'):
            c = get(chains, row['label_asym_id'], label + ': missing chain')
            if row.get('label_seq_id'):
                check(c.get('entity_id') == row.get('label_entity_id') and (row.get('label_entity_id'), row['label_seq_id']) in seq, label + ': residue identity mismatch')
            # A coordinate-free chain may exist in the declared target even when
            # none of its residues is resolved; do not require an atom at a residue.
    def same_context(a, b, label):
        check(a.get('model_id') == b.get('model_id'), label + ': model mismatch')
        if not a.get('model_id'):
            check(a.get('data_id') == b.get('data_id'), label + ': logical data mismatch')
    members = defaultdict(list)
    for r in rows('group_member'):
        members[r.get('group_id')].append(r)
        get(groups, r.get('group_id'), 'group_member: missing group')
    graph = defaultdict(set)
    for gid, g in groups.items():
        scope(g, 'group')
        mm = members[gid]
        check(bool(mm), 'group: empty membership')
        ordinals = [num(m.get('ordinal_id'), 'group: invalid ordinal', True) for m in mm]
        check(len(set(ordinals)) == len(mm) and all(i > 0 for i in ordinals), 'group: duplicate/nonpositive ordinal')
        seen = set()
        for m in mm:
            selector = selected(m, {'atom_id', 'child_group_id', 'site_id'})
            check(len(selector) == 1, 'group: member needs exactly one selector')
            identity = tuple(m.get(k) for k in ('atom_id', 'child_group_id', 'site_id'))
            check(identity not in seen, 'group: duplicate member')
            seen.add(identity)
            if m.get('atom_id'):
                structural(m, g.get('model_id'), 'group member')
            if m.get('child_group_id'):
                child = get(groups, m['child_group_id'], 'group: missing child')
                same_context(g, child, 'nested group')
                graph[gid].add(m['child_group_id'])
            if m.get('site_id'):
                site = get(sites, m['site_id'], 'group: missing site')
                check(not g.get('model_id') and site.get('data_id') == g.get('data_id'), 'group: site context mismatch')
            check((g.get('kind') == 'index') == bool(m.get('index_offset') is not None), 'group: index offset applicability')
            if g.get('kind') == 'index':
                check((m.get('child_group_id') and groups.get(m['child_group_id'], {}).get('kind') == 'token') or (m.get('site_id') and sites.get(m['site_id'], {}).get('level') == 'token' and sites.get(m['site_id'], {}).get('kind') == 'position'), 'index group: member must be token or unit token position')
        if g.get('context_group_id'):
            context = get(groups, g['context_group_id'], 'group: missing context')
            same_context(g, context, 'group context')
            check(gid != g['context_group_id'], 'group: self context')
        if g.get('kind') == 'index':
            check(g.get('ordered') == 'YES' and bool(g.get('context_group_id')), 'index group: ordered and contextual')
            offsets = [num(m.get('index_offset'), 'index group: invalid offset', True) for m in sorted(mm, key=lambda r: int(r['ordinal_id']))]
            check(offsets == sorted(set(offsets)), 'index group: offsets must increase uniquely')
    def acyclic(edges, label):
        visiting, done = set(), set()
        def walk(n):
            if n in visiting:
                check(False, label + ': cycle'); return
            if n in done:
                return
            visiting.add(n)
            for child in edges.get(n, ()):
                walk(child)
            visiting.remove(n); done.add(n)
        for n in list(edges):
            walk(n)
    acyclic(graph, 'group membership')
    acyclic({i: {g['context_group_id']} for i, g in groups.items() if g.get('context_group_id')}, 'group context')
    def leaves(gid, path=frozenset()):
        if gid in path:
            return set()
        result = set()
        for m in members[gid]:
            if m.get('child_group_id'):
                result |= leaves(m['child_group_id'], path | {gid})
            else:
                result.add((m.get('atom_id'), m.get('site_id')))
        return result
    for gid, g in groups.items():
        if g.get('kind') == 'index' and g.get('context_group_id'):
            check(leaves(gid) <= leaves(g['context_group_id']), 'index group: members outside enclosing context')
    for i, s in sites.items():
        check(s.get('data_id') in data, 'site: missing data')
        context = get(groups, s.get('context_group_id'), 'site: missing context')
        check(not context.get('model_id') and context.get('data_id') == s.get('data_id') and context.get('ordered') == 'YES', 'site: context must be ordered and coordinate-free')
        check(any(m.get('site_id') == i for m in members[s.get('context_group_id')]), 'site: absent from context membership')
        lo, hi = (num(s.get(k), 'site: invalid bounds', True) for k in ('min_length','max_length'))
        check(0 <= lo <= hi, 'site: invalid bounds')
        if s.get('kind') == 'position':
            check(lo == hi == 1, 'site: position must have length one')
    for s in subjects.values():
        scope(s, 'subject')
        selector = selected(s, {'atom_id', 'label_asym_id', 'group_id', 'site_id'})
        check(len(selector) == 1, 'subject: exactly one selector')
        level = s.get('level')
        if s.get('site_id'):
            site = get(sites, s['site_id'], 'subject: missing site')
            check(not s.get('model_id') and site.get('data_id') == s.get('data_id') and site.get('level') == level, 'subject: site scope/level mismatch')
        elif s.get('group_id'):
            g = get(groups, s['group_id'], 'subject: missing group')
            same_context(s, g, 'subject group')
            check(g.get('kind') == level and level in ('token', 'molecule'), 'subject: group level mismatch')
        else:
            structural(s, s.get('model_id'), 'subject')
            expected = 'atom' if s.get('atom_id') else 'residue' if s.get('label_seq_id') else 'chain'
            check(level == expected, 'subject: selector level mismatch')
        check((level == 'residue' and bool(s.get('label_asym_id'))) == bool(s.get('label_entity_id') and s.get('label_seq_id')), 'subject: residue selector incomplete')
    order_edges = defaultdict(set)
    for r in rows('site_link'):
        site = get(sites, r.get('site_id'), 'site_link: missing site')
        sub = get(subjects, r.get('subject_id'), 'site_link: missing subject')
        rel = r.get('relation')
        if sub.get('site_id'):
            other = sites.get(sub['site_id'], {})
            check(other.get('context_group_id') == site.get('context_group_id'), 'site_link: different logical context')
            if rel != 'connected':
                a,b = r.get('site_id'), sub['site_id']
                if rel in ('after', 'adjacent_after'): a,b = b,a
                order_edges[a].add(b)
                ordinals = {m.get('site_id'): int(m['ordinal_id']) for m in members[site.get('context_group_id')] if m.get('site_id')}
                check(a in ordinals and b in ordinals and ordinals[a] < ordinals[b], 'site_link: inconsistent with declared order')
        else:
            check(any({site.get('data_id'), sub.get('data_id')} <= contents for contents in data_groups.values()), 'site_link: structural anchor lacks shared data context')
        check((rel == 'connected') == bool(r.get('bond_order')), 'site_link: bond order applicability')
        for role, level in [('site', site.get('level')), ('subject', sub.get('level'))]:
            check(bool(r.get(role+'_atom_name')) == (rel == 'connected' and level == 'residue'), 'site_link: named atom applicability')
        if rel == 'connected':
            check(site.get('level') in ('atom','residue') and sub.get('level') in ('atom','residue'), 'site_link: chemical endpoints must be atoms/residues')
    acyclic(order_edges, 'site order')

    owners = defaultdict(list)
    semantic_keys = set()
    probabilities = defaultdict(dict)
    probability_states = defaultdict(dict)
    identities = {}
    def payload(row, definition, context, label, scalar_only=False):
        state = row.get('state', 'specified')
        check(state in ('specified','unconstrained','unknown','not_applicable'), label + ': explicit null/invalid state')
        actual = selected(row, PAYLOAD)
        if state != 'specified':
            check(not actual, label + ': non-specified state carries payload'); return
        kind = definition.get('value_kind')
        expected = {SCALAR[kind]} if kind in SCALAR else {'x','y','z','frame_id'} if kind in ('point3','vector3') else {'array_id'} if kind == 'array' else {'value_group_id'}
        if kind == 'array' and definition.get('array_transform') in ('point3','vector3'): expected.add('frame_id')
        check(not scalar_only or kind in SCALAR, label + ': default/element must be scalar')
        check(actual == expected, label + ': payload fields do not match kind')
        for field in actual & {'value_real','x','y','z'}:
            num(row[field], label + ': nonfinite/invalid number')
        if row.get('value_integer'):
            num(row['value_integer'], label + ': invalid integer', True)
        if row.get('value_boolean'):
            check(row['value_boolean'] in ('YES','NO'), label + ': invalid boolean')
        if row.get('value_comp_id'):
            check(row['value_comp_id'] in components, label + ': missing component')
        if row.get('frame_id'):
            frame = get(frames, row['frame_id'], label + ': missing frame')
            if frame.get('kind') == 'model Cartesian':
                check(frame.get('model_id') == context.get('model_id'), label + ': frame/model mismatch')
        if row.get('value_group_id'):
            g = get(groups, row['value_group_id'], label + ': missing value group')
            same_context(context, g, label + ' value group')
        if row.get('array_id'):
            get(arrays, row['array_id'], label + ': missing array')
            owners[row['array_id']].append((definition, context))
        domain = definition.get('domain_id')
        if domain and definition.get('parameter_kind') != 'component':
            allowed = set(domain_values[domain]) if kind == 'text' else {v.get('comp_id') for v in domain_values[domain].values()}
            check(row.get(SCALAR.get(kind)) in allowed, label + ': value outside closed domain')
    for cat in CARRIERS:
        for r in rows(cat):
            s = get(sets, r.get('set_id'), cat + ': missing set')
            d = get(defs, r.get('definition_id'), cat + ': missing definition')
            level = d.get('subject_level')
            order = '0' if cat == 'system' else '2' if cat == 'pair' else '1'
            check(d.get('body_order') == order, cat + ': body order mismatch')
            subject = ()
            if cat in ('atom','residue','chain'):
                check(level == cat, cat + ': level mismatch')
                structural(r, s.get('model_id'), cat)
                subject = (r.get('atom_id'),) if cat == 'atom' else (r.get('label_asym_id'), r.get('label_entity_id'), r.get('label_seq_id'))
            elif cat == 'group_value':
                g = get(groups, r.get('group_id'), 'group_value: missing group')
                same_context(s, g, cat)
                check(level == g.get('kind') and level in ('token','molecule'), 'group_value: level mismatch')
                subject = (r.get('group_id'),)
            elif cat == 'site_value':
                site = get(sites, r.get('site_id'), 'site_value: missing site')
                check(not s.get('model_id') and site.get('data_id') == s.get('data_id') and site.get('level') == level, 'site_value: context/level mismatch')
                subject = (r.get('site_id'),)
            elif cat == 'pair':
                endpoints = [get(subjects, r.get(k), 'pair: missing endpoint') for k in ('subject_id_1','subject_id_2')]
                for endpoint in endpoints:
                    same_context(s, endpoint, 'pair endpoint')
                    check(endpoint.get('level') == level, 'pair: endpoint level mismatch')
                # Resolve alias subject IDs to scientific identity before deduplication.
                subject = tuple(tuple(e.get(k) for k in ('data_id','model_id','level','atom_id','label_asym_id','label_entity_id','label_seq_id','group_id','site_id')) for e in endpoints)
                if d.get('symmetric') == 'YES': subject = tuple(sorted(subject, key=repr))
            param = r.get('component_id')
            check(bool(param) == (d.get('parameter_kind') == 'component'), cat + ': component parameter applicability')
            if param:
                check(param in components, cat + ': missing candidate component')
                allowed = CANONICAL28 if d.get('definition_key') == 'proposal:sequence_probability' else {v.get('comp_id') for v in domain_values[d.get('domain_id')].values()}
                check(param in allowed, cat + ': component outside domain')
            if r.get('context_group_id'):
                g = get(groups, r['context_group_id'], cat + ': missing context group')
                same_context(s, g, cat + ' context')
            key = (cat, r.get('set_id'), r.get('definition_id'), subject, param, r.get('context_group_id'))
            check(key not in semantic_keys, cat + ': duplicate semantic assignment')
            semantic_keys.add(key)
            payload(r, d, s, cat)
            sitekey = (r.get('set_id'), cat, subject)
            if d.get('definition_key') == 'proposal:sequence_probability':
                probability_states[sitekey][param] = r.get('state', 'specified')
            if r.get('state', 'specified') == 'specified':
                if d.get('definition_key') == 'proposal:sequence_probability':
                    value = num(r.get('value_real'), 'probability: invalid value')
                    check(0 <= value <= 1, 'probability: value outside [0,1]')
                    probabilities[sitekey][param] = value
                if d.get('definition_key') == 'proposal:sequence_identity':
                    identities[sitekey] = r.get('value_comp_id')
    default_keys = set()
    for r in rows('default'):
        s = get(sets, r.get('set_id'), 'default: missing set')
        d = get(defs, r.get('definition_id'), 'default: missing definition')
        key = (r.get('set_id'), r.get('definition_id'))
        check(key not in default_keys, 'default: duplicate assignment'); default_keys.add(key)
        check(d.get('parameter_kind') != 'component', 'default: component parameters must be materialized')
        check(d.get('definition_key') != 'proposal:sequence_identity', 'default: exact identities must be materialized')
        payload(r, d, s, 'default', True)
    for key, values in probabilities.items():
        total = sum(values.values())
        check(total <= 1 + TOLERANCE, 'probability: supplied mass exceeds one')
        states = probability_states[key]
        if len(states) == len(CANONICAL28) and all(v in ('specified','not_applicable') for v in states.values()):
            check(abs(total - 1) <= TOLERANCE, 'probability: complete distribution must sum to one')
        if key in identities:
            target = identities[key]
            check(target in CANONICAL28, 'probability: fixed identity outside candidate domain')
            check(all(abs(v - (1 if c == target else 0)) <= TOLERANCE for c,v in values.items()), 'probability: conflicts with exact identity')
    for key, target in identities.items():
        if key in probability_states:
            check(target in CANONICAL28 and probability_states[key].get(target) != 'not_applicable', 'probability: exact identity outside applicable domain')
    axes = defaultdict(list)
    labels = defaultdict(list)
    elements = defaultdict(list)
    for r in rows('axis'): axes[r.get('array_id')].append(r)
    for r in rows('axis_label'): labels[(r.get('array_id'),r.get('axis_order'))].append(r)
    for r in rows('array_value'): elements[r.get('array_id')].append(r)
    for arrid in set(axes) | set(elements) | {k[0] for k in labels}:
        check(arrid in arrays, 'array: orphan axis/element')
    for aid, axis_order in labels:
        check(any(a.get('axis_order') == axis_order for a in axes[aid]), 'axis_label: missing axis')
    for aid, array in arrays.items():
        check(len(owners[aid]) == 1, 'array: requires exactly one owner')
        if len(owners[aid]) != 1: continue
        d, context = owners[aid][0]
        rank = num(array.get('rank'), 'array: invalid rank', True)
        check(rank == num(d.get('array_rank'), 'array: invalid definition rank', True), 'array: rank mismatch')
        aa = sorted(axes[aid], key=lambda r: num(r.get('axis_order'), 'axis: invalid order', True))
        check([a.get('axis_order') for a in aa] == [str(i) for i in range(1,rank+1)], 'array: missing/duplicate axis')
        shape = []
        declared = {a.get('axis_order'): a for a in def_axes[d.get('id')]}
        for a in aa:
            n = num(a.get('length'), 'axis: invalid length', True); shape.append(n)
            check(n >= 0, 'axis: negative length')
            da = declared.get(a.get('axis_order'), {})
            check(a.get('label_kind') == da.get('label_kind') and a.get('domain_id') == da.get('domain_id') and (not da.get('length') or da['length'] == a.get('length')), 'axis: disagrees with definition')
            ll = labels[(aid,a.get('axis_order'))]
            kind = a.get('label_kind')
            indices = [num(l.get('index'), 'axis_label: invalid index', True) for l in ll]
            check(sorted(indices) == ([] if kind == 'unlabelled' else list(range(1,n+1))), 'axis: incomplete/duplicate labels')
            vv = [l.get('comp_id' if kind == 'component' else 'label') for l in sorted(ll,key=lambda l: int(l['index']))]
            check(len(set(vv)) == len(vv) and all(v is not None for v in vv), 'axis: labels must be non-null and unique')
            for l in ll:
                check(selected(l, {'label','comp_id'}) == ({'comp_id'} if kind == 'component' else {'label'}), 'axis_label: payload mismatch')
                if kind == 'component': check(l.get('comp_id') in components, 'axis_label: missing chem_comp')
            if kind == 'Cartesian': check(n == 3 and vv == ['x','y','z'], 'axis: Cartesian order must be x/y/z')
            if a.get('domain_id'):
                domain = get(domains, a['domain_id'], 'axis: missing domain')
                allowed = {v.get('comp_id') for v in domain_values[a['domain_id']].values()} if kind == 'component' else set(domain_values[a['domain_id']])
                check(set(vv) <= allowed and (domain.get('kind') == 'component') == (kind == 'component'), 'axis: labels outside domain')
        size = math.prod(shape)
        seen = set()
        element_states = {}
        for e in elements[aid]:
            i = num(e.get('element_index'), 'array_value: invalid index', True)
            check(1 <= i <= size and i not in seen, 'array_value: duplicate/out-of-range index'); seen.add(i)
            payload({k:v for k,v in e.items() if k != 'array_id'}, {'value_kind':d.get('array_element_kind')}, context, 'array_value', True)
            element_states[i] = e.get('state','specified')
        if d.get('array_transform') in ('point3','vector3'):
            check(bool(aa) and aa[-1].get('label_kind') == 'Cartesian' and shape[-1] == 3 and d.get('array_element_kind') == 'real', 'array: geometric values require final real Cartesian axis')
            for start in {((i-1)//3)*3+1 for i in seen}:
                states = {element_states.get(i,array.get('omitted_state')) for i in range(start,start+3)}
                check(len(states) == 1, 'array: partial geometric triple')
    realized = defaultdict(set)
    realization_modes = defaultdict(set)
    realization_order = defaultdict(list)
    mapping_keys = set()
    for r in rows('correspondence'):
        rel = r.get('relation')
        source, target = subjects.get(r.get('source_subject_id')), subjects.get(r.get('target_subject_id'))
        check(bool(source) == (rel != 'generated') and bool(target) == (rel != 'deleted'), 'correspondence: endpoint pattern')
        check((rel == 'realized') == bool(r.get('target_ordinal_id')), 'correspondence: realized member order applicability')
        step = get(steps, r.get('protocol_step_id'), 'correspondence: missing protocol step')
        for endpoint, side in [(source,'input'),(target,'output')]:
            if endpoint: check(endpoint.get('data_id') in data_groups[step.get(side+'_data_group_id')], 'correspondence: subject outside protocol '+side)
        key = (r.get('source_subject_id'),r.get('target_subject_id'),rel,r.get('protocol_step_id'))
        check(key not in mapping_keys, 'correspondence: duplicate mapping'); mapping_keys.add(key)
        if source and target:
            check(source.get('level') == target.get('level'), 'correspondence: level mismatch')
        if rel == 'realized' and source and target:
            check(bool(source.get('site_id')) and not target.get('site_id'), 'correspondence: realization needs logical source and realized target')
            identity = tuple(target.get(k) for k in ('data_id','model_id','level','atom_id','label_asym_id','label_entity_id','label_seq_id','group_id'))
            check(identity not in realized[(source.get('site_id'),r.get('protocol_step_id'))], 'correspondence: duplicate realized identity')
            realized[(source.get('site_id'),r.get('protocol_step_id'))].add(identity)
            realization_modes[(source.get('site_id'),r.get('protocol_step_id'))].add('realized')
            realization_order[(source.get('site_id'),r.get('protocol_step_id'))].append(num(r.get('target_ordinal_id'), 'correspondence: invalid realized order', True))
        if rel == 'deleted' and source and source.get('site_id'):
            realized[(source['site_id'],r.get('protocol_step_id'))]
            realization_modes[(source['site_id'],r.get('protocol_step_id'))].add('deleted')
    for (site_id, step_id), targets in realized.items():
        site = sites.get(site_id,{})
        check(len(realization_modes[(site_id,step_id)]) == 1, 'correspondence: site both realized and deleted')
        check(sorted(realization_order[(site_id,step_id)]) == list(range(1,len(targets)+1)), 'correspondence: realized order must be contiguous')
        check(num(site.get('min_length'), 'realization: missing site bounds', True) <= len(targets) <= num(site.get('max_length'), 'realization: missing site bounds', True), 'correspondence: realized length outside bounds')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    failed = False
    for filename in args.files:
        try:
            doc = gemmi.cif.read_file(filename)
            for block in doc:
                diagnostics = validate(block)
                for message in diagnostics:
                    print(f'{filename}:{block.name}: {message}', file=sys.stderr)
                failed |= bool(diagnostics)
            if not failed: print(f'{filename}: annotation semantic checks passed')
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            print(f'{filename}: invalid input: {exc}', file=sys.stderr); failed = True
    return int(failed)


if __name__ == '__main__':
    sys.exit(main())
