# Incorporating Annotated CIF into ModelCIF

**Discussion proposal for a direct extension of ModelCIF 1.4.9.** Proposed names and semantics require working-group approval; they are not in the released dictionary.

## Purpose and scope

Incorporate the annotation data model used by AtomWorks and RFD4-Proteina into ModelCIF, enabling seamless tool pipelines, meaningful cross-tool benchmarking and exchangeable preprocessed datasets. The endpoint is one ModelCIF annotation capability, implemented by both libraries. Existing Annotated CIF files may be converted; preserving their item names, layout or permanent backward compatibility is not a requirement.

The [annotation-module design](annotation-module.md) specifies the full target: atom, residue, chain, molecule, token and system semantic levels; 0/1/2-body annotations; typed scalar and shaped values; categorical domains, defaults and states; sparse relations; coordinate frames and index groups; logical design sites/expandable segments; and source-to-output correspondence. General `ma_annotation_*` categories are proposed for conditions, prepared features and derived annotation data, with existing ModelCIF result categories reused where applicable.

The [API coverage matrix](api-coverage.json) maps all 59 inventoried entries and the generic API surface to proposed representations, recording unresolved scientific and implementation work. It is a scoped source inventory, not a claim that every plugin has been enumerated or that the full module is implemented. The standard describes data and semantics, not executable Python methods. A reader can preserve a condition without executing it; an execution consumer must reject unsupported required conditions.

Retain useful StandardAnnotation/ConditionBase and array operations where practical, while allowing API changes that clarify portable semantics. Make the accepted ModelCIF representation canonical through normal library I/O. A versioned converter can migrate older datasets, with new checksums and provenance. No permanently separate annotation standard or mandatory private annotation sidecar is proposed.

## Alignment with existing ModelCIF

The 2026 update explains how ModelCIF represents protein-design workflows, including protocol and selection metadata for selected models. This proposal supplies the missing machine-readable conditions and prepared features consumed by those workflows. It retains the vocabulary from #31 and removes or deprecates no existing ModelCIF categories or values.

| Existing content | Use in this proposal |
| --- | --- |
| `backbone generation`, `sequence design`, `structural validation`, `intermediate backbone`, `intermediate sequence`, `input structure` | Keep the design workflow vocabulary from #31. |
| `ma_data`, `ma_data_group`, `ma_protocol_step`, software and parameters | Link authored, effective and derived annotations to producing/consuming steps. |
| `ma_feature_list`, atom/residue/entity-instance feature categories | Reuse structural selections; add semantic level, grouping context and logical future subjects where needed. |
| `ma_restraints` and spatial restraint categories | Reuse when scientific meaning and endpoint coverage fit; avoid competing encodings. |
| `ma_qa_metric*`, `ma_energy_estimates*`, `ma_experimental_validation` | Keep quality, energy and experimental results in their existing categories. |
| Associated files and database references | Link large prepared resources, benchmark accounting and provenance, with standard-defined interpretation. Coordinate investigation-level metadata with the ongoing ModelCIF discussion. |

## Reviewable components and status

- [annotation-module.md](annotation-module.md): complete target architecture and annotation construction examples.
- [api-coverage.json](api-coverage.json): proposed term mappings, generic API requirements and unresolved work.
- [compatibility.md](compatibility.md): library integration, migration and acceptance plan.
- [subset-prototype.md](subset-prototype.md): earlier item-level descriptions following the style of category proposal #29. The accompanying DDL2 component, example, schema and 25 bounded checks cover only this small existing-structure subset; they are not the final module schema or evidence of full API support.

Agree the full architecture and coverage before implementing reviewable increments. A small first increment must not define a permanent ceiling on the proposal. New standardization work includes the generic module, shared scientific definitions and application profiles; exact category boundaries and external resource formats remain review questions. Existing released dictionaries are unchanged by this PR.

## Exchange profiles and boundaries

**Pipeline exchange.** Preserve chemical identity, feature references, condition definitions and coordinate frames through supported operations. Record structure-to-structure correspondence through the proposed relations or a standard-defined associated representation, scoped by artifact hash, data block, model and local IDs, including one-to-many assembly copies and generated/deleted subjects. This mapping profile is an acceptance requirement; it is not implemented by the subset prototype. Do not silently transform an unsupported task into another task.

**Prepared datasets.** Associate a manifest containing source/CCD snapshots, licenses, checksums, preparation parameters, stable example IDs and split provenance. Distinguish prepared structures from stochastic sampled examples and model-specific feature tensors; include token-to-structure and tensor-axis mappings where applicable. Custom component definitions take precedence only under an explicit recorded chemistry policy.

**Benchmarks.** Associate a manifest defining tasks, permitted information, seeds and sampling budgets, all scheduled attempts, failure states, evaluator versions, selections/alignment, thresholds and denominators. Record effective inputs after defaults and consistency transforms. Enforce the permitted information at the consumer boundary: an unconditioned mask does not hide identities or coordinates that remain readable in the source structure. Remove prohibited information from the supplied artifact or use a documented, verified input projection. Report valid-only summaries separately from all-attempt summaries. Unavailable evaluation evidence is `not_evaluated`, not a measured zero. Equal samples and equal compute are distinct comparisons. Existing QA categories hold suitable model-level/feature-level results; attempt accounting is associated metadata.

These are proposed application-profile requirements. The manifest schemas and production transformations require further validation before claiming profile conformance. Future residues, variable-length topology, coordinate-free task profiles, multi-model selection rules and portable token-index semantics are required parts of the integrated design scope. They are not implemented by the subset prototype. A small first increment must not imply full support for every RFD4 condition.

## Implementation evidence and migration

Initial inventory: AtomWorks `a0c63a8f77e76aba93857f444d02092354972c45`. Local re-review: AtomWorks `d922a471381dd0f8bccaf78c384a6b56b6f8e391`; RFD4-Proteina `68058693cb88762a8aaf806571e13b291ce6318a`.

| Implementation convention | Exchange requirement |
| --- | --- |
| `name`, `n_body`, `level`, `dtype`, `value_shape`, aliases and defaults in StandardAnnotation | Preserve scientific meaning, body order, subject selection and type; aliases and Python class names are adapter concerns. |
| Residue-level annotations broadcast over atoms | Check consistency before collapsing to a residue feature; storage granularity is not semantic scope. |
| Scalar one-body data in atom_site; vectors/pairs in idx/val categories | The current loader remaps saved indices through unique atom_array_index after filtering and drops rows for removed atoms. Reuse this protection; add portable artifact/structural identity, one-to-many lineage and explicit loss handling. |
| `C_SEQ` uses `<M>`; `C_CRD` uses NaN; hotspot uses false | Translate condition-specific sentinels explicitly. Do not infer zero/false/absence equivalence for all fields. |
| `C_IDX` defaults to true; index groups depend on molecules and indexed status | Materialize or declare defaults; portable index relations need explicit offsets and molecular context, not raw group integers. |
| Positive `C_CRDGRP` plus `C_INTCRD` describes freely placed rigid groups | Preserve group membership and group-local Cartesian targets; reserved IDs -1/0 and int16 limits remain implementation details. |
| Sequence probabilities distinguish NaN from zero | Specify chemical-component vocabulary, partial mass and exact-identity conflict policy; do not standardize token-channel numbers. |
| FinalizeSequenceConditioning can infer additional sequence information from atomization/sidechain constraints | Record the effective model inputs and any implied conditions. Benchmarking must account for information actually supplied. |
| RFD4 annotation-preserving parser avoids renumbering preparation operations | Require correspondence and explicit loss reporting; parser success alone is not preservation. |

The simple Coordinate mask accepts any finite component; RFD4 CoordinateGroup assignment separately rejects partially specified absolute vectors. This is an API-level distinction, not evidence that all RFD4 execution accepts partial vectors. Saved internal targets may be preserved or materialized from live coordinates by specific transforms; any reconstruction must be recorded by adapters.

The existing loader can warn and skip malformed non-system annotation categories. A consumer claiming the execution profile needs a strict path: a malformed or unrepresentable required condition is an error. Unknown optional content can be retained opaquely for an unchanged artifact; after structural edits, remap, invalidate or reject affected content explicitly. The current native serializer demonstrates scalar system values, scalar/nonscalar one-body columns and sparse pair rows, not universal arbitrary-rank tensor interchange.

## Review and validation

The earlier subset DDL2 fragment uses existing ModelCIF conventions for keys, parent links and category descriptions. It demonstrates conventions for a future addition to `base/mmcif_ma-core.dic`; its categories must be reconciled with the unified module before incorporation; it is not a new syntax or a competing file type. This draft PR changes no released dictionary, does not assign a release version, and removes nothing from ModelCIF. Maintainers determine final names, integration and release.

Checks cover CIF parsing, declared fields/types/keys/enumerations, proposed and existing parent references, representative scientific invariants, row reorder preservation and rejection of malformed example mutations. Comparison includes definitions, subjects, payloads and frames; changed targets or atom identities must be observable. Pilot names at version draft-1 cannot be redefined with a different type/subject signature. Positive fixtures cover an independent rigid frame and an explicit false pairwise prepared feature. Full RCSB dictionary assembly, general DDL2 validation, deposition validation, BinaryCIF, runtime adapters, independent-tool workflows and scientific benchmarks remain release gates. The proposal intentionally does not equate a candidate-schema check with standards conformance.

Working-group review should cover the integrated architecture, shared definition governance, subject and shape representations, design-site/correspondence semantics, and independent evidence for the complete declared API coverage.

## References

- [ModelCIF dictionary and release history](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/)
- [Protein-design vocabulary proposal #31](https://github.com/ihmwg/ModelCIF/issues/31)
- [Category proposal style #29](https://github.com/ihmwg/ModelCIF/issues/29)
- [2026 ModelCIF update](https://doi.org/10.1016/j.jmb.2026.169658)
- [AtomWorks annotation base](https://github.com/RosettaCommons/atomworks/blob/d922a471381dd0f8bccaf78c384a6b56b6f8e391/src/atomworks/io/utils/standard_annotations/base.py)
- [AtomWorks serialization](https://github.com/RosettaCommons/atomworks/blob/d922a471381dd0f8bccaf78c384a6b56b6f8e391/src/atomworks/io/utils/standard_annotations/serialization.py)
- [AtomWorks conditions](https://github.com/RosettaCommons/atomworks/blob/d922a471381dd0f8bccaf78c384a6b56b6f8e391/src/atomworks/ml/conditions/definitions.py)
- [RFD4 conditions](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/conditions.py)
- [RFD4 sequence conditioning](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/transforms/sequence_conditioning.py)
- [RFD4 parsing presets](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/utils/parse_presets.py)

## Compatibility implementation

See [compatibility.md](compatibility.md) for the AtomWorks/RFD4 implementation plan and acceptance gates. To reproduce bounded checks, install gemmi 0.7.5 in an isolated environment and run `python check_examples.py`. Tests use the repository’s published dist/mmcif_ma.dic.
