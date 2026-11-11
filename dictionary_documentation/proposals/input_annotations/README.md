# Annotated CIF in ModelCIF

Incorporate the annotation data contract used by AtomWorks and RFD4-Proteina into ModelCIF, enabling seamless tool pipelines, meaningful cross-tool benchmarking and exchangeable preprocessed datasets. Preserve familiar subject/value rows and existing Python APIs. Older files may be converted to this single standardized representation.

**Proposed dictionary component 0.2.0 for working-group review.** The extension has 16 categories and 157 items. Both dictionary generators include it; published ModelCIF remains 1.4.9. No released category is removed or redefined. Maintainers determine final names, scientific profiles and release packaging.

## Compact construction

**Definition + shared context + subject/value row.** Atom coordinates remain one atom/XYZ row. Residue probabilities remain one residue/component/value row. Only applicable columns are written. Other annotation forms reuse one value table; grouping, geometry and arrays add metadata only when needed.

| Records | Purpose |
| --- | --- |
| `definition`, `set` | Meaning/version/type and shared data/model context |
| `atom`, `residue`, `value` | Direct atom/residue values; shared layout for system, chain, group, logical, pair and default values |
| `subject`, `relation` | Reusable or logical identities; order, connectivity and source/output mapping |
| `group`, `group_member`, `frame` | Explicit membership, index offsets and geometric placement |
| `domain`, `domain_value` | Custom closed vocabularies |
| `array`, `axis`, `axis_label`, `array_value` | Shaped values, with fixed dimensions/labels shared once per definition |

This covers all six semantic levels, body orders 0/1/2, typed scalars/arrays, explicit states/defaults, sparse pairs, coordinate/index groups, expandable segments and ordered correspondence. Direct atom/residue categories avoid forcing ordinary mixed XYZ/probability data into a wide, mostly empty table. ModelCIF types, keys and references remain explicit; values are not hidden in JSON or private tensor blobs.

## Contribution

- [DDL2 component](../../../base/mmcif_ma-annotation.dic) and [interpretation rules](annotation-module.md).
- [Compact complete CIF](worked-annotations.cif) and [extended CIF](extended-annotations.cif) exercising every category.
- [Coverage/migration](annotation-coverage.md) for all 59 scoped source entries.
- [Validation](validation.md), including dictionary checks, conditional-rule tests and typed CIF/BinaryCIF interchange.

## Standards integration and adoption

Reuse the protein-design vocabulary introduced by [issue #31](https://github.com/ihmwg/ModelCIF/issues/31): `backbone generation`, `sequence design`, **`structure validation`**, `intermediate backbone`, `intermediate sequence` and `input structure`. The issue originally used “structural validation”; the released spelling is “structure validation”. Reuse ModelCIF data groups, protocols, software, applicable restraints and existing QA/energy/experimental result categories. Annotation artifacts use the current `other` content type with details. DDL2 category/item definitions follow the existing dictionary and the proposal approach in [issue #29](https://github.com/ihmwg/ModelCIF/issues/29).

AtomWorks needs canonical I/O, metadata retention and reference remapping/invalidation after edits. RFD4 needs adapters that record authored/effective inputs and provenance, and verify equivalent model conditioning. A versioned converter can rewrite old files and dataset manifests; ambiguous legacy values must be reported. These production adapters are not implemented by this dictionary PR.

Prepared-data profiles specify sources/CCD versions, recipes, licenses, splits, checksums and tensor axes. Benchmark profiles additionally specify effective inputs, budgets, evaluators and all-attempt accounting. A mask does not hide identity or coordinates still supplied in the structure. Associated resources need standard-defined interpretation and explicit file links; investigation-level metadata should align with InvestigationCIF.

References: [published dictionary/history](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/), [usage guide](../../documentation.md), [Tauriello et al., ModelCIF Update (2026)](https://doi.org/10.1016/j.jmb.2026.169658).
