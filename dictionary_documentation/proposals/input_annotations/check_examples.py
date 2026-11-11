"""Bounded checks for this discussion fragment, not a general DDL2 validator.
Run with Python 3.10+ and gemmi 0.7.5 from any directory.
"""
from pathlib import Path
import json, math, copy
import gemmi
D=Path(__file__).resolve().parent
S=json.loads((D/'schema.json').read_text())
NULL={'.','?',''}
def rows(block,cat):
    t=block.find_mmcif_category('_'+cat+'.')
    return [{str(k).split('.',1)[1]:gemmi.cif.as_string(str(v)) if str(v) not in NULL else str(v) for k,v in zip(t.tags,r)} for r in t]
def validate(text):
    b=gemmi.cif.read_string(text).sole_block()
    data={cat:rows(b,cat) for cat in S}
    for cat,meta in S.items():
        rr=data[cat];key=meta['items'][0]['name'];seen=set()
        for r in rr:
            assert set(r)<=set(i['name'] for i in meta['items']),cat
            assert r[key] not in seen;seen.add(r[key])
            for i in meta['items']:
                v=r.get(i['name'],'.')
                if i['required']:assert v not in NULL,(cat,i['name'])
                if v in NULL:continue
                if i['enum']:assert v in i['enum'],(cat,i['name'],v)
                if i['type']=='int':int(v)
                if i['type']=='float':assert math.isfinite(float(v))
                if i['parent']:
                    pc,pn=i['parent'][1:].split('.')
                    assert v in {x.get(pn) for x in rows(b,pc)},(i['parent'],v)
    types={r['id']:r for r in data['ma_input_annotation_type']}
    # A declared pilot name/version must retain its defined scientific signature.
    pilot_types={
        'sequence identity':('component','residue','1','none'),
        'absolute coordinate':('vector3','atom','1','angstroms'),
        'relative coordinate':('vector3','atom','1','angstroms'),
        'task label':('text','system','0','none'),
    }
    for t in types.values():
        if t['version']=='draft-1' and t['name'] in pilot_types:
            assert tuple(t[k] for k in ('data_type','feature_type','body_order','unit'))==pilot_types[t['name']]
    atoms={r['id']:r for r in rows(b,'atom_site')}
    feats={r['feature_id']:r for r in rows(b,'ma_feature_list')}
    am={};rm={}
    for r in rows(b,'ma_atom_feature'):am.setdefault(r['feature_id'],[]).append(r['atom_id'])
    for r in rows(b,'ma_poly_residue_feature'):rm.setdefault(r['feature_id'],[]).append(r)
    scal={r['annotation_id']:r for r in data['ma_input_annotation_value']}
    vec={r['annotation_id']:r for r in data['ma_input_annotation_vector']}
    frames={r['id']:r for r in data['ma_input_annotation_frame']}
    for fr in frames.values():
        assert (fr.get('model_id','.') not in NULL)==(fr['kind']=='model Cartesian')
    slots={'boolean':'value_boolean','integer':'value_integer','real':'value_real','text':'value_text','component':'value_comp_id'}
    assignment_keys=set()
    for a in data['ma_input_annotation']:
        t=types[a['type_id']];n=int(t['body_order']);ids=[a.get('feature_id_1','.'),a.get('feature_id_2','.')]
        assert sum(v not in NULL for v in ids)==n
        assert n!=1 or ids[0] not in NULL
        assert (t['feature_type']=='system')==(n==0)
        if n==2:assert t.get('symmetric','.') in {'YES','NO'}
        for fid in ids[:n]:
            assert feats[fid]['feature_type']==t['feature_type']
            if fid in am:
                assert a.get('model_id','.') not in NULL
                assert all(atoms[k]['pdbx_PDB_model_num']==a['model_id'] for k in am[fid])
        pair=tuple(sorted(ids)) if n==2 and t['symmetric']=='YES' else tuple(ids)
        key=(a['data_id'],a.get('model_id'),a['type_id'],a['purpose'],pair)
        assert key not in assignment_keys;assignment_keys.add(key)
        if a['value_state']=='unconstrained':assert a['purpose']=='condition'
        ident=a['ordinal_id'];has_s=ident in scal;has_v=ident in vec
        if a['value_state']!='specified':assert not has_s and not has_v;continue
        if t['data_type']=='vector3':
            assert has_v and not has_s
            assert t['unit']=='angstroms' and n==1 and len(am.get(ids[0],[]))==1
            fr=frames[vec[ident]['frame_id']]
            if t['name']=='absolute coordinate':assert fr['kind']=='model Cartesian' and fr['model_id']==a['model_id']
            if t['name']=='relative coordinate':assert fr['kind']=='independent rigid'
        else:
            assert has_s and not has_v
            occupied=[k for k,v in scal[ident].items() if k!='annotation_id' and v not in NULL]
            assert occupied==[slots[t['data_type']]]
            if t['name']=='sequence identity':
                assert t['data_type']=='component' and n==1 and len(rm.get(ids[0],[]))==1
                residue=rm[ids[0]][0]
                assert any(all(ar[k]==residue[k] for k in ['label_asym_id','label_seq_id','label_comp_id']) and ar['pdbx_PDB_model_num']==a['model_id'] for ar in atoms.values())
    # Compare all example content, including subjects and payloads, independently of row order.
    return {cat:sorted(json.dumps(r,sort_keys=True) for r in rows(b,cat[1:-1]))
            for cat in b.get_mmcif_category_names()}
def run():
    text=(D/'example.cif').read_text();results=[]
    def check(name,fn):
        fn();results.append(name)
    def reject(x):
        try:validate(x)
        except (AssertionError,ValueError,KeyError):return
        raise AssertionError('Expected rejection')
    check('valid proposed example',lambda:validate(text))
    def content_changes():
        assert validate(text)!=validate(text.replace('_ma_input_annotation_vector.Cartn_x 0','_ma_input_annotation_vector.Cartn_x 100'))
        assert validate(text)!=validate(text.replace('10 C CA ALA A 1 1 0 0 0 1','10 C CB ALA A 1 1 0 0 0 1'))
    check('comparison detects changed coordinate targets and atom identity',content_changes)
    def wrong_pilot_signature():
        altered=text.replace('vector3 atom 1 angstroms .','real atom 1 angstroms .')
        altered=altered[:altered.index('_ma_input_annotation_vector.annotation_id')]
        altered=altered.replace("_ma_input_annotation_value.value_text\n3 ALA .\n4 . 'Illustrative task'",
            "_ma_input_annotation_value.value_text\n_ma_input_annotation_value.value_real\n3 ALA . .\n4 . 'Illustrative task' .\n1 . . 5")
        reject(altered)
    check('reject changed pilot type signature even with a matching scalar payload',wrong_pilot_signature)
    def dictionary():
        b=gemmi.cif.read_file(str(D/'modelcif-input-annotations.dic')).sole_block()
        frames={i.frame.name:i.frame for i in b if i.frame is not None}
        parent=gemmi.cif.read_file(str(D.parents[2]/'dist/mmcif_ma.dic')).sole_block()
        parent_frames={i.frame.name for i in parent if i.frame is not None}
        for cat,m in S.items():
            assert cat in frames and cat not in parent_frames
            for i in m['items']:
                tag='_'+cat+'.'+i['name'];f=frames[tag]
                assert gemmi.cif.as_string(f.find_value('_item_type.code'))==i['type']
                assert f.find_value('_item.mandatory_code')==('yes' if i['required'] else 'no')
                if i['parent']:assert i['parent'] in frames or i['parent'] in parent_frames
        # Check required items for every included existing ma_* category in the example.
        ex=gemmi.cif.read_string(text).sole_block()
        for category in ex.get_mmcif_category_names():
            if not category.startswith('_ma_') or category.startswith('_ma_input_annotation'):continue
            cat=category[1:-1]
            for i in parent:
                f=i.frame
                if f is None or not f.name.startswith(category):continue
                if f.find_value('_item.mandatory_code')=='yes':assert ex.find_values(f.name),f.name
    check('dictionary fields and parent references; existing ma category required columns',dictionary)
    a='10 C CA ALA A 1 1 0 0 0 1\n20 C CA GLY A 1 2 3.8 0 0 1'
    check('atom row reorder preserves assignments',lambda: (_ for _ in ()).throw(AssertionError()) if validate(text)!=validate(text.replace(a,'20 C CA GLY A 1 2 3.8 0 0 1\n10 C CA ALA A 1 1 0 0 0 1')) else None)
    mutations={
    'unknown feature':('1 1 2 1 1 . condition specified YES','1 1 2 1 99 . condition specified YES'),
    'missing required data link':('1 1 2 1 1 . condition specified YES','1 1 . 1 1 . condition specified YES'),
    'unknown data link':('1 1 2 1 1 . condition specified YES','1 1 99 1 1 . condition specified YES'),
    'unknown model':('1 1 2 1 1 . condition specified YES','1 1 2 9 1 . condition specified YES'),
    'extra one-body operand':('1 1 2 1 1 . condition specified YES','1 1 2 1 1 2 condition specified YES'),
    'wrong feature type':('3 2 2 1 3 . condition specified YES','3 2 2 1 1 . condition specified YES'),
    'payload on unconstrained assignment':('1 1 2 1 1 . condition specified YES','1 1 2 1 1 . condition unconstrained YES'),
    'unconstrained prepared feature':("4 3 2 . . . 'prepared feature' specified NO","4 3 2 . . . 'prepared feature' unconstrained NO"),
    'wrong scalar slot':('3 ALA .',"3 . 'ALA'"),
    'unknown component':('3 ALA .','3 XXX .'),
    'infinite coordinate':('_ma_input_annotation_vector.Cartn_x 0','_ma_input_annotation_vector.Cartn_x inf'),
    'partial coordinate':('_ma_input_annotation_vector.Cartn_z 0','_ma_input_annotation_vector.Cartn_z ?'),
    'unknown frame':('_ma_input_annotation_vector.frame_id 1','_ma_input_annotation_vector.frame_id 2'),
    'frame kind mismatch':("_ma_input_annotation_frame.kind 'model Cartesian'","_ma_input_annotation_frame.kind 'independent rigid'"),
    'invalid purpose':('condition specified YES','evaluation specified YES'),
    }
    for name,(old,new) in mutations.items():
        assert old in text
        check('reject '+name,lambda old=old,new=new:reject(text.replace(old,new,1)))
    # A valid free rigid frame demonstrates the distinction from absolute placement.
    relative=text.replace("'absolute coordinate'", "'relative coordinate'").replace("_ma_input_annotation_frame.kind 'model Cartesian'", "_ma_input_annotation_frame.kind 'independent rigid'").replace('_ma_input_annotation_frame.model_id 1','_ma_input_annotation_frame.model_id .')
    check('valid independent rigid coordinate frame',lambda:validate(relative))
    check('reject atom from another model',lambda:reject(text.replace('10 C CA ALA A 1 1 0 0 0 1','10 C CA ALA A 1 1 0 0 0 2')))
    check('reject duplicate assignment',lambda:reject(text.replace('1 1 2 1 1 . condition specified YES','1 1 2 1 1 . condition specified YES\n5 1 2 1 1 . condition specified YES')))
    # Reuse existing atom features for a scalar pairwise prepared feature.
    pair=text.replace("3 'task label'", "4 'same source group' draft-1 'Whether two atoms belong to the same recorded source group' boolean atom 2 none YES\n3 'task label'")
    pair=pair.replace("4 3 2 . . . 'prepared feature' specified NO", "4 3 2 . . . 'prepared feature' specified NO\n5 4 2 1 1 2 'prepared feature' specified NO")
    pair=pair.replace("_ma_input_annotation_value.value_text\n3 ALA .\n4 . 'Illustrative task'", "_ma_input_annotation_value.value_text\n_ma_input_annotation_value.value_boolean\n3 ALA . .\n4 . 'Illustrative task' .\n5 . . NO")
    check('valid explicit false pairwise prepared feature',lambda:validate(pair))
    check('reject reversed symmetric duplicate',lambda:reject(pair.replace("5 4 2 1 1 2 'prepared feature' specified NO","5 4 2 1 1 2 'prepared feature' specified NO\n6 4 2 1 2 1 'prepared feature' specified NO")))
    report={'status':'passed','count':len(results),'checks':results,'scope':'Bounded draft component and illustrative fragment only','not_run':['full RCSB dictionary assembly','general DDL2 conformance','complete deposition validation','BinaryCIF','AtomWorks/RFD4 runtime adapters','independent tool interoperation']}
    print(json.dumps(report,indent=2))
if __name__=='__main__':run()
