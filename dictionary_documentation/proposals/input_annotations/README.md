# Incorporating Annotated CIF into ModelCIF

We propose incorporating the annotation data contract used by AtomWorks and RFD4-Proteina into ModelCIF. This enables seamless tool pipelines, meaningful cross-tool benchmarking and exchangeable preprocessed datasets through one standard and the libraries' existing annotation APIs. Scalar and XYZ values retain compact subject/value rows; definitions and context are shared. Older files may be converted.

**Proposed dictionary implementation for ModelCIF Working Group review.** The `ma_annotation_*` names and scientific terms are provisional. No released category is removed or redefined. The published release remains ModelCIF 1.4.9; draft component 0.1.0 is added to both source dictionary generators. Maintainers assign the eventual release number and regenerate distribution/archive files.

## Proposed addition

The module defines all six semantic levels, body orders 0/1/2, typed scalars and arrays, categorical domains, explicit states/defaults, sparse pairs, coordinate/index groups, logical design sites and artifact-scoped correspondence. It standardizes data and scientific interpretation, not executable Python functions.

- [Dictionary component](../../../base/mmcif_ma-annotation.dic): 24 DDL2 categories with item descriptions, types, keys, enumerations and parent links.
- [Interpretation rules](annotation-module.md): construction, scope, scientific definitions and conditional constraints.
- [Compact complete example](worked-annotations.cif): two atom/XYZ rows and two residue/component/probability rows, with structural and workflow context.
- [Extended example](extended-annotations.cif): every proposed category, including a custom domain, nested groups, scalar defaults, shaped values, logical positions and realization/copy/generation/deletion.
- [API coverage and migration](annotation-coverage.md): all 59 scoped source entries and implementation requirements.
- [Validation](validation.md): build commands, dictionary checks, semantic checks, negative cases and independent CIF/BinaryCIF roundtrip.

## Relationship to the published standard

[Issue #31](https://github.com/ihmwg/ModelCIF/issues/31) added protein-design vocabulary in ModelCIF 1.4.8. Reuse `backbone generation`, `sequence design`, **`structure validation`**, `intermediate backbone`, `intermediate sequence` and `input structure`. The issue originally used “structural validation”; the released spelling is “structure validation”. This module supplies annotation data to those workflows. Its category/item definitions follow the dictionary's DDL2 organization and the category-proposal approach in [issue #29](https://github.com/ihmwg/ModelCIF/issues/29).

Reuse `ma_data`, data groups, protocols, software and parameters; direct structural identities; applicable existing spatial restraints; and existing QA, energy and experimental-validation categories. Annotation artifacts use the current `other` data content type with explicit details. Large resources use ModelCIF associated-file links with a declared schema, source versions, checksums and axes; a private payload must not be the only definition of required data. Investigation-level metadata should be coordinated with InvestigationCIF.

## Adoption

AtomWorks needs canonical reading/writing, metadata retention and reference remapping or explicit invalidation after slicing, concatenation, assembly generation or edits. RFD4 needs condition adapters and recording of authored/effective inputs, derived references and provenance. Its model architecture and condition APIs need not be replaced. A versioned converter can rewrite historical files and update dataset versions/checksums; ambiguous legacy inputs must be reported rather than silently reinterpreted.

Prepared-data profiles identify sources/CCD versions, preprocessing recipes, licenses, examples, splits and tensor axes. Benchmark profiles additionally specify permitted effective inputs, budgets, evaluators and all-attempt accounting. A mask does not hide identity or coordinates still present in an input structure. These profile requirements do not assert that standardization alone makes benchmarks comparable.

The dictionary and examples are implemented and locally validated; production AtomWorks/RFD4/python-modelcif adapters and model-conditioning equivalence tests remain adoption work. Working-group acceptance is not implied by validation.

## Standards references

- [Published ModelCIF dictionary and release history](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/)
- [Published protocol method values](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.method_type.html)
- [ModelCIF usage guide](../../documentation.md)
- [Tauriello et al., ModelCIF Update (2026)](https://doi.org/10.1016/j.jmb.2026.169658)
