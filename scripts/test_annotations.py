"""Regression tests for the proposed annotation contract (run with unittest)."""
from pathlib import Path
import tempfile
import unittest
import gemmi
from validate_annotations import validate, records

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'dictionary_documentation/proposals/input_annotations'


def example(name='extended-annotations.cif'):
    return gemmi.cif.read_file(str(EXAMPLES / name)).sole_block()


def mutate(block, category, field, index, value):
    tag = '_ma_annotation_' + category + '.'
    data = block.get_mmcif_category(tag)
    if field not in data:
        data[field] = [('specified' if field == 'state' else False)] * len(next(iter(data.values())))
    data[field][index] = value
    block.set_mmcif_category(tag, data)


class AnnotationTests(unittest.TestCase):
    def test_examples(self):
        for name in ('worked-annotations.cif', 'extended-annotations.cif'):
            with self.subTest(name=name):
                self.assertEqual(validate(example(name)), [])

    def test_reject_invalid_inputs(self):
        cases = [
            ('atom','x',0,False,'payload fields'),
            ('atom','x',0,'NaN','nonfinite'),
            ('atom','state',0,'unknown','non-specified'),
            ('atom','state',0,None,'invalid state'),
            ('atom','atom_id',0,'30','outside model'),
            ('atom','value_real',0,'3','payload fields'),
            ('atom','definition_id',0,'2','level mismatch'),
            ('residue','label_entity_id',0,'99','residue identity'),
            ('residue','component_id',0,'MSE','outside domain'),
            ('residue','value_real',0,'1.2','outside [0,1]'),
            ('residue','value_real',1,'.5','mass exceeds'),
            ('residue','component_id',1,'ALA','duplicate semantic'),
            ('group_member','child_group_id',0,'3','exactly one selector'),
            ('group_member','child_group_id',2,'3','cycle'),
            ('group_member','index_offset',5,'0','increase uniquely'),
            ('group_member','index_offset',4,False,'offset applicability'),
            ('group','context_group_id',3,'4','self context'),
            ('group','model_id',0,'2','model/data mismatch'),
            ('group','ordered',4,'NO','ordered and coordinate-free'),
            ('site','max_length',0,'0','invalid bounds'),
            ('site','min_length',1,'-1','invalid bounds'),
            ('site','min_length',1,'1','realized length outside'),
            ('subject','atom_id',0,'10','exactly one selector'),
            ('subject','level',0,'atom','selector level'),
            ('subject','data_id',0,'4','model/data mismatch'),
            ('site_link','subject_id',0,'4','site order: cycle'),
            ('site_link','relation',0,'connected','bond order applicability'),
            ('pair','subject_id_2',0,'6','endpoint level'),
            ('group_value','array_id',1,'999','missing array'),
            ('default','definition_id',0,'2','must be materialized'),
            ('domain_value','code',1,'donor','duplicate code'),
            ('domain_value','comp_id',3,'ALA','duplicate component'),
            ('atom','value_text',2,'unknown_role','outside closed domain'),
            ('definition','version',0,'other','shared term'),
            ('definition','units',0,'nm','angstroms'),
            ('definition','symmetric',3,False,'symmetric only'),
            ('definition','body_order',2,'1','system iff'),
            ('definition','domain_id',11,False,'complete domain'),
            ('array','rank',0,'3','rank mismatch'),
            ('array_value','element_index',0,'5','out-of-range'),
            ('array_value','element_index',1,'1','duplicate/out-of-range'),
            ('array_value','value_real',2,'1','non-specified'),
            ('axis','length',1,'3','disagrees with definition'),
            ('axis_label','label',1,'row_a','unique'),
            ('axis_label','index',1,'3','incomplete/duplicate'),
            ('correspondence','source_subject_id',2,'6','endpoint pattern'),
            ('correspondence','protocol_step_id',0,'2','outside protocol'),
            ('correspondence','target_subject_id',0,'7','level mismatch'),
            ('correspondence','target_ordinal_id',0,'2','order must be contiguous'),
            ('correspondence','target_ordinal_id',1,'1','order applicability'),
        ]
        for cat, field, row, value, diagnostic in cases:
            with self.subTest(category=cat, field=field, row=row, value=value):
                b = example(); mutate(b,cat,field,row,value)
                self.assertTrue(any(diagnostic in e for e in validate(b)), validate(b))

    def test_symmetric_alias_duplicate(self):
        b = example()
        p = b.get_mmcif_category('_ma_annotation_pair.')
        for k in p:
            p[k].append({'id':'2','subject_id_1':'2','subject_id_2':'1'}.get(k,p[k][0]))
        b.set_mmcif_category('_ma_annotation_pair.',p)
        self.assertTrue(any('duplicate semantic' in e for e in validate(b)))

    def test_identity_probability_conflict(self):
        b = example()
        r = b.get_mmcif_category('_ma_annotation_residue.')
        r['value_comp_id'] = [False]*4
        for k in r:
            r[k].append({'id':'5','set_id':'1','definition_id':'10','label_asym_id':'A','label_entity_id':'1','label_seq_id':'1','value_comp_id':'ALA'}.get(k,False))
        b.set_mmcif_category('_ma_annotation_residue.',r)
        self.assertTrue(any('conflicts with exact identity' in e for e in validate(b)))
        mutate(b,'residue','value_real',0,'1')
        self.assertEqual(validate(b),[])

    def test_record_reordering_and_id_renaming(self):
        b = example()
        for cat in b.get_mmcif_category_names():
            data = b.get_mmcif_category(cat)
            b.set_mmcif_category(cat,{k:list(reversed(v)) for k,v in data.items()})
        for cat,field in [('frame','id'),('atom','frame_id')]:
            data = b.get_mmcif_category('_ma_annotation_'+cat+'.')
            data[field] = ['renamed' if v == 'G' else v for v in data[field]]
            b.set_mmcif_category('_ma_annotation_'+cat+'.',data)
        self.assertEqual(validate(b),[])

    def test_geometric_arrays(self):
        for transform, units in [('point3','angstroms'),('vector3','none')]:
            with self.subTest(transform=transform):
                b = example()
                mutate(b,'definition','array_transform',8,transform)
                mutate(b,'definition','units',8,units)
                for cat in ('definition_axis','axis'):
                    mutate(b,cat,'length',1,'3')
                    mutate(b,cat,'label_kind',1,'Cartesian')
                mutate(b,'group_value','frame_id',1,'G')
                labels = b.get_mmcif_category('_ma_annotation_axis_label.')
                labels['label'][2:] = ['x','y']
                for k in labels:
                    labels[k].append({'array_id':'1','axis_order':'2','index':'3','label':'z'}[k])
                b.set_mmcif_category('_ma_annotation_axis_label.',labels)
                mutate(b,'array_value','state',2,'specified')
                mutate(b,'array_value','value_real',2,'.5')
                self.assertEqual(validate(b),[])
                mutate(b,'array_value','state',2,'unknown')
                mutate(b,'array_value','value_real',2,False)
                self.assertTrue(any('partial geometric triple' in e for e in validate(b)))

    def test_zero_length_array_dimension(self):
        b = example()
        mutate(b,'axis','length',0,'0')
        data = b.get_mmcif_category('_ma_annotation_axis_label.')
        b.set_mmcif_category('_ma_annotation_axis_label.',{k:v[2:] for k,v in data.items()})
        b.find_mmcif_category('_ma_annotation_array_value.').erase()
        self.assertEqual(validate(b),[])

    def test_unknown_and_inapplicable_probability(self):
        b = example()
        mutate(b,'residue','state',0,'unknown')
        mutate(b,'residue','value_real',0,False)
        # Unknown is valid exchange data but must be resolved before required execution.
        self.assertEqual(validate(b),[])
        mutate(b,'residue','state',0,'not_applicable')
        r = b.get_mmcif_category('_ma_annotation_residue.')
        r['value_comp_id'] = [False]*4
        for k in r:
            r[k].append({'id':'5','set_id':'1','definition_id':'10','label_asym_id':'A','label_entity_id':'1','label_seq_id':'1','value_comp_id':'ALA','state':'specified'}.get(k,False))
        b.set_mmcif_category('_ma_annotation_residue.',r)
        self.assertTrue(any('outside applicable domain' in e for e in validate(b)))

    def test_cif_binarycif_roundtrip(self):
        # An independent parser/writer checks retained categories, values and null
        # states. This does not test production AtomWorks/RFD4 adapter behavior.
        import biotite.structure.io.pdbx as pdbx
        b = example()
        types = {}
        dictionary = gemmi.cif.read_file(str(ROOT/'base/mmcif_ma-annotation.dic')).sole_block()
        for item in dictionary:
            if item.frame is not None:
                tag = item.frame.find_value('_item.name')
                kind = item.frame.find_value('_item_type.code')
                if tag and kind in ('int','float'):
                    types[gemmi.cif.as_string(tag)] = int if kind == 'int' else float
        with tempfile.TemporaryDirectory() as tmp:
            source = pdbx.CIFFile.read(str(EXAMPLES/'extended-annotations.cif'))
            binary = pdbx.BinaryCIFFile()
            for name, block in source.items():
                out = pdbx.BinaryCIFBlock()
                for cat, table in block.items():
                    out[cat] = pdbx.BinaryCIFCategory({k:pdbx.BinaryCIFColumn(v.as_array(types.get('_'+cat+'.'+k,str)),v.mask.array if v.mask is not None else None) for k,v in table.items()})
                binary[name] = out
            path = Path(tmp)/'example.bcif'; binary.write(path)
            reread = pdbx.BinaryCIFFile.read(path)
            text = pdbx.CIFFile()
            for name, block in reread.items():
                out = pdbx.CIFBlock()
                for cat, table in block.items():
                    out[cat] = pdbx.CIFCategory({k:pdbx.CIFColumn(v.as_array(str),v.mask.array if v.mask is not None else None) for k,v in table.items()})
                text[name] = out
            target = Path(tmp)/'example.cif'; text.write(target)
            rb = gemmi.cif.read_file(str(target)).sole_block()
            self.assertEqual(validate(rb),[])
            for cat in b.get_mmcif_category_names():
                left, right = b.get_mmcif_category(cat), rb.get_mmcif_category(cat)
                self.assertEqual(set(left),set(right),cat)
                for field in left:
                    cast = types.get(cat+field,str)
                    def normalized(values):
                        return [cast(v) if isinstance(v,str) else v for v in values]
                    self.assertEqual(normalized(left[field]),normalized(right[field]),cat+field)


if __name__ == '__main__':
    unittest.main()
