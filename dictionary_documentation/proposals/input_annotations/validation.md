# Validation of draft component 0.2.0

The Python files are narrowly scoped validation tools: one checks conditional rules that DDL2 cannot express, and one tests the contract. They are not an alternative format, a migration implementation or a required production dependency. The dictionary component is the authoritative item/type/key reference.

## Reproduce

Use Python 3.12 with `mmcif==1.2.1`, `gemmi==0.7.5` and `biotite==2.0.0`. Initialize the repository's pinned `mmcif_pdbx` submodule. Commands below run from the repository root; choose a fresh output directory so previous diagnostic files cannot be mistaken for new results.

```sh
git submodule update --init --recursive
mkdir -p build/annotations
build_dict_cli --op build \
  --input_dict_path base/mmcif_ma-generator-local.dic \
  --output_dict_path build/annotations/mmcif_ma.dic --cleanup
build_dict_cli --op build \
  --input_dict_path base/mmcif_ma_ext-generator-local.dic \
  --output_dict_path build/annotations/mmcif_ma_ext.dic --cleanup
python -m unittest discover -s scripts -p test_annotations.py -v
python scripts/validate_annotations.py \
  dictionary_documentation/proposals/input_annotations/worked-annotations.cif \
  dictionary_documentation/proposals/input_annotations/extended-annotations.cif
```

Build `DictToSdb` and `CifCheck` from [RCSB cpp-dict-pack](https://github.com/rcsb/cpp-dict-pack), including submodules, following its CMake instructions. This review used commit `b227176b018b79cda33422a1676880e73df4a209` and its downloaded DDL 2.3.3. With those executables available and `mmcif_ddl.dic` pointing to that DDL:

```sh
DictToSdb -ddlFile mmcif_ddl.dic \
  -dictFile build/annotations/mmcif_ma.dic \
  -dictSdbFile build/annotations/mmcif_ma.sdb
CifCheck \
  -f dictionary_documentation/proposals/input_annotations/worked-annotations.cif \
  -dictSdb build/annotations/mmcif_ma.sdb
CifCheck \
  -f dictionary_documentation/proposals/input_annotations/extended-annotations.cif \
  -dictSdb build/annotations/mmcif_ma.sdb
```

Inspect `*-diag.log` and `*-parser.log` in the working directory, **not just process exit codes**. Dictionary compilation validates against DDL2; file checks validate against the assembled ModelCIF dictionary. The extension-only build depends on the parent dictionary and is not a standalone replacement for the assembled dictionary.

## Results on 11 November 2026

| Check | Result |
| --- | --- |
| Combined and extension-only source assembly | Passed; includes 16 annotation categories / 157 items |
| Combined dictionary against RCSB DDL | No diagnostic errors |
| Both complete annotation examples against assembled dictionary | No parser or dictionary diagnostics |
| Deliberately invalid `value_kind` enumeration | Rejected in diagnostic log |
| Existing four repository examples | Diagnostics identical with published baseline and proposed dictionary; existing examples are not all clean under the current validator |
| Semantic suite | 12 tests passed, including 64 invalid-input mutations plus identity conflict, symmetric-pair duplicate and incomplete geometric-triple rejection |
| Valid edge cases | Unknown data retention, zero-length array dimension, point/vector arrays, explicit defaults/states, shared fixed axes/labels, no redundant per-array axes, shuffled records and frame-ID renaming |
| Independent interchange | Gemmi and Biotite CIF/BinaryCIF roundtrip preserves category content and null states; semantic checks pass after roundtrip |

The extended example exercises all 16 categories. Parsed definitions, sets, frames, atom rows and residue rows in the compact example are unchanged from draft 0.1.0; only its draft audit/version declaration changes. The dictionary shrinks from 247 to 157 items without dropping the 59-entry source crosswalk. Conditional checks cover selectors, scopes, payloads, domains, frames, pair uniqueness, membership/order, logical bounds, arrays, shared probability/identity semantics and protocol-linked correspondence. Production readers must additionally implement scientific definitions, final chemical/topological feasibility, lifecycle transformations and effective-condition execution. These checks are not a ModelArchive deposition certification, a throughput benchmark or proof of AtomWorks/RFD4/python-modelcif adapter compatibility. No such adapter is claimed in this PR.
