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
            ('subject','max_length',2,'0','invalid bounds'),
            ('subject','min_length',3,'-1','invalid bounds'),
            ('subject','min_length',3,'1','realized length outside'),
            ('subject','atom_id',0,'10','exactly one selector'),
            ('subject','level',0,'atom','selector level'),
            ('subject','data_id',0,'4','model/data mismatch'),
            ('relation','target_subject_id',0,'4','logical order: cycle'),
            ('relation','relation',0,'connected','bond order applicability'),
            ('value','subject_id_2',1,'6','endpoint level'),
            ('value','array_id',4,'999','missing array'),
            ('value','definition_id',7,'2','must be materialized'),
            ('domain_value','code',1,'donor','duplicate code'),
            ('domain_value','comp_id',3,'ALA','duplicate component'),
            ('atom','value_text',2,'unknown_role','outside closed domain'),
            ('definition','version',0,'other','shared term'),
            ('definition','units',0,'nm','angstroms'),
            ('definition','symmetric',3,False,'symmetric only'),
            ('definition','body_order',2,'1','system iff'),
            ('definition','domain_id',11,False,'complete domain'),
            ('definition','array_rank',8,'3','incomplete or duplicate axes'),
            ('array_value','element_index',0,'5','out-of-range'),
            ('array_value','element_index',1,'1','duplicate/out-of-range'),
            ('array_value','value_real',2,'1','non-specified'),
            ('axis','length',2,'3','incomplete/duplicate labels'),
            ('axis_label','label',1,'row_a','unique'),
            ('axis_label','index',1,'3','incomplete/duplicate'),
            ('relation','source_subject_id',3,'6','endpoint pattern'),
            ('relation','protocol_step_id',1,'2','outside protocol'),
            ('relation','target_subject_id',1,'7','level mismatch'),
            ('relation','target_ordinal_id',1,'2','order must be contiguous'),
            ('relation','target_ordinal_id',2,'1','order applicability'),
            ('value','group_id',7,'1','default: no subject'),
            ('value','is_default',0,None,'invalid default flag'),
            ('value','subject_id_1',2,'1','subject selectors'),
            ('value','subject_id_1',8,'1','one-body subject must be logical'),
            ('value','is_default',4,'YES','default/element must be scalar'),
            ('subject','atom_id',2,'10','logical position has no structural'),
            ('subject','min_length',0,'1','no logical bounds'),
            ('relation','protocol_step_id',0,'1','topology has no producing'),
            ('relation','bond_order',2,'single','mapping has no topology-only'),
            ('axis','array_id',0,'1','exactly one definition/array owner'),
            ('axis','label_kind',2,'text','inherit label/domain'),
            ('axis','array_id',2,False,'exactly one definition/array owner'),
            ('axis_label','axis_id',0,'99','missing axis'),
            ('axis','length',0,None,'unknown length is not a variable'),
        ]
        for cat, field, row, value, diagnostic in cases:
            with self.subTest(category=cat, field=field, row=row, value=value):
                b = example(); mutate(b,cat,field,row,value)
                self.assertTrue(any(diagnostic in e for e in validate(b)), validate(b))

    def test_symmetric_alias_duplicate(self):
        b = example()
        p = b.get_mmcif_category('_ma_annotation_value.')
        for k in p:
            p[k].append({'id':'10','subject_id_1':'2','subject_id_2':'1'}.get(k,p[k][1]))
        b.set_mmcif_category('_ma_annotation_value.',p)
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
                mutate(b,'axis','length',1,'3')
                mutate(b,'axis','label_kind',1,'Cartesian')
                mutate(b,'value','frame_id',4,'G')
                labels = b.get_mmcif_category('_ma_annotation_axis_label.')
                labels['label'][2:] = ['x','y']
                for k in labels:
                    labels[k].append({'axis_id':'2','index':'3','label':'z'}[k])
                b.set_mmcif_category('_ma_annotation_axis_label.',labels)
                mutate(b,'array_value','state',2,'specified')
                mutate(b,'array_value','value_real',2,'.5')
                self.assertEqual(validate(b),[])
                mutate(b,'array_value','state',2,'unknown')
                mutate(b,'array_value','value_real',2,False)
                self.assertTrue(any('partial geometric triple' in e for e in validate(b)))

    def test_zero_length_array_dimension(self):
        b = example()
        mutate(b,'axis','length',2,'0')
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

    def test_fixed_axis_lengths_and_inherited_labels(self):
        b = example()
        axes = b.get_mmcif_category('_ma_annotation_axis.')
        for k in axes:
            axes[k].append({'id':'4','array_id':'1','axis_order':'2','length':'2'}.get(k,False))
        b.set_mmcif_category('_ma_annotation_axis.',axes)
        self.assertEqual(validate(b),[])  # Fixed axis and its labels are inherited.
        mutate(b,'axis','length',3,'3')
        self.assertTrue(any('disagrees with definition' in e for e in validate(b)))
        mutate(b,'axis','length',3,'2')
        labels = b.get_mmcif_category('_ma_annotation_axis_label.')
        for k in labels:
            labels[k].append({'axis_id':'4','index':'1','label':'replacement'}[k])
        b.set_mmcif_category('_ma_annotation_axis_label.',labels)
        self.assertTrue(any('cannot override shared labels' in e for e in validate(b)))

    def test_fixed_shape_needs_no_per_array_axes(self):
        b = example()
        # Move the variable dimension and labels into the shared declaration.
        mutate(b,'axis','length',0,'2')
        for i in (0,1): mutate(b,'axis_label','axis_id',i,'1')
        axes = b.get_mmcif_category('_ma_annotation_axis.')
        b.set_mmcif_category('_ma_annotation_axis.',{k:v[:2] for k,v in axes.items()})
        self.assertEqual(validate(b),[])
        # A second array inherits the same dimensions/labels with no new axis rows.
        arr = b.get_mmcif_category('_ma_annotation_array.')
        arr['id'].append('2'); arr['omitted_state'].append('unknown')
        b.set_mmcif_category('_ma_annotation_array.',arr)
        values = b.get_mmcif_category('_ma_annotation_value.')
        for k in values:
            values[k].append({'id':'10','group_id':'2','array_id':'2'}.get(k,values[k][4]))
        b.set_mmcif_category('_ma_annotation_value.',values)
        self.assertEqual(validate(b),[])

    def test_default_and_explicit_value_remain_distinct(self):
        b = example()
        # Uniform YES and an explicit unconstrained override coexist.
        self.assertEqual(validate(b),[])
        values = b.get_mmcif_category('_ma_annotation_value.')
        for k in values: values[k].append('10' if k == 'id' else values[k][7])
        b.set_mmcif_category('_ma_annotation_value.',values)
        self.assertTrue(any('default: duplicate assignment' in e for e in validate(b)))

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
