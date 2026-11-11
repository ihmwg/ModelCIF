# Input annotations for computational modeling workflows

**Discussion draft; proposed direct addition to ModelCIF 1.4.9.** Category names and semantics require working-group approval. This proposal is not part of the released dictionary.

## Purpose

AtomWorks and RFD4-Proteina exchange molecular structures together with typed input conditions and preparation annotations. We propose targeted ModelCIF additions so independent tools can preserve these inputs, compare methods on the same tasks, and reuse prepared datasets. This builds on the protein-design protocol/data vocabulary introduced in #31; no existing categories or enumerations are removed or deprecated.

The 2026 update explains how ModelCIF represents design workflows and recommends documenting selected models and their protocols. Here the additional requirement is a machine-readable description of the conditions and prepared features consumed by those protocols. The execution rules below apply to consumers claiming the exchange profile, not to every ModelCIF reader or archive.

## Keep and reuse

- Keep `backbone generation`, `sequence design`, `structural validation`, `intermediate backbone`, `intermediate sequence`, and the existing `input structure` definition from #31.
- Use `ma_data`, `ma_data_group` and `ma_protocol_step` to connect annotation datasets to their producing and consuming steps. Use existing software and parameter categories for software, settings and provenance.
- Use `ma_feature_list`, `ma_atom_feature`, `ma_poly_residue_feature` and `ma_entity_instance_feature` for selections. A feature can contain a set; body order counts feature operands, not selected atoms.
- Reuse `ma_restraints` and the distance/angle/dihedral restraint categories where their scientific meaning and endpoint representation fit. A feature-based annotation is not a competing representation of an already representable restraint.
- Keep quality assessments in `ma_qa_metric*`, energy estimates in `ma_energy_estimates*`, and experimental validation in `ma_experimental_validation`. This input layer does not replace these results categories.
- Use associated files for large prepared data and benchmark manifests. An audit record of failed/discarded attempts does not require deposition of every intermediate coordinate model. Campaign-wide investigation metadata should be coordinated with the ModelCIF/InvestigationCIF discussion identified in the 2026 paper.

## Proposed categories

The following descriptions and item properties follow the style of ModelCIF category proposals such as #29. A matching DDL2 discussion component and CIF fragment accompany this document. They are kept outside the production dictionary until review. All categories are optional; required items below apply when that category is present. Conditional scientific rules are listed separately.


### ma_input_annotation_type

Category description: Data items in the MA_INPUT_ANNOTATION_TYPE category describe the meaning and representation of input annotations supplied to a computational modeling protocol.

Items with properties and description:

- `id` (key, required, data type: int): A unique identifier for the annotation type.

- `name` (required, data type: line): The name of the annotation type. Interoperable interpretation requires a shared definition and version.

- `version` (required, data type: code): The version of the annotation definition.

- `description` (required, data type: text): The scientific meaning, value domain and interpretation of the annotation.

- `data_type` (required, data type: code): The type of value assigned to an annotation. Allowed values: `boolean`, `integer`, `real`, `text`, `component`, `vector3`.

- `feature_type` (required, data type: line): The kind of feature operand; system denotes an annotation without feature operands. Allowed values: `atom`, `residue`, `entity instance`, `system`.

- `body_order` (required, data type: int): The number of feature operands, independent of value shape. Allowed values: `0`, `1`, `2`.

- `unit` (required, data type: line): Units for numeric values; use none for dimensionless or non-numeric values.

- `symmetric` (optional, data type: boolean): Whether exchanging two feature operands preserves meaning. Inapplicable for body orders zero and one. Allowed values: `YES`, `NO`.

- `reference` (optional, data type: line): A resolvable reference to the annotation definition, if available.

### ma_input_annotation

Category description: Data items in the MA_INPUT_ANNOTATION category identify input annotation assignments and their states. Annotation data are connected to modeling protocol steps through MA_DATA and MA_DATA_GROUP. These records do not assert that an output model satisfies a condition.

Items with properties and description:

- `ordinal_id` (key, required, data type: int): A unique identifier for the annotation assignment.

- `type_id` (required, data type: int, parent: `_ma_input_annotation_type.id`): The identifier for the annotation type.

- `data_id` (required, data type: int, parent: `_ma_data.id`): The identifier for the annotation dataset used or produced by a protocol step.

- `model_id` (optional, data type: int, parent: `_ma_model_list.ordinal_id`): The identifier for the structural model containing the selected features, if applicable.

- `feature_id_1` (optional, data type: int, parent: `_ma_feature_list.feature_id`): The identifier for the first feature operand.

- `feature_id_2` (optional, data type: int, parent: `_ma_feature_list.feature_id`): The identifier for the second feature operand.

- `purpose` (required, data type: line): Whether the annotation specifies a requested condition or a prepared input feature. Allowed values: `condition`, `prepared feature`.

- `value_state` (required, data type: code): The interpretation of value presence. Unconstrained applies only to conditions. Allowed values: `specified`, `unconstrained`, `unknown`, `not_applicable`.

- `required_for_execution` (required, data type: boolean): Whether an execution profile requires the consumer to interpret this annotation before running. This does not guarantee condition satisfaction. Allowed values: `YES`, `NO`.

### ma_input_annotation_value

Category description: Data items in the MA_INPUT_ANNOTATION_VALUE category record scalar input annotation values. Exactly one typed value is supplied for each specified scalar assignment.

Items with properties and description:

- `annotation_id` (key, required, data type: int, parent: `_ma_input_annotation.ordinal_id`): The identifier for the annotation assignment.

- `value_boolean` (optional, data type: boolean): A specified boolean value. Allowed values: `YES`, `NO`.

- `value_integer` (optional, data type: int): A specified integer value.

- `value_real` (optional, data type: float): A specified finite real value.

- `value_text` (optional, data type: text): A specified text value.

- `value_comp_id` (optional, data type: ucode, parent: `_chem_comp.id`): A specified chemical component identifier.

### ma_input_annotation_frame

Category description: Data items in the MA_INPUT_ANNOTATION_FRAME category describe Cartesian frames for coordinate inputs. A model Cartesian frame fixes a global placement. An independent rigid frame specifies internal geometry without a fixed placement relative to other frames.

Items with properties and description:

- `id` (key, required, data type: int): A unique identifier for the frame.

- `kind` (required, data type: line): The interpretation of the Cartesian frame. Allowed values: `model Cartesian`, `independent rigid`.

- `model_id` (optional, data type: int, parent: `_ma_model_list.ordinal_id`): The model defining a model Cartesian frame; inapplicable for an independent rigid frame.

- `details` (optional, data type: text): Additional information about frame construction and provenance.

### ma_input_annotation_vector

Category description: Data items in the MA_INPUT_ANNOTATION_VECTOR category record complete Cartesian coordinate targets for input annotations. Group-local Cartesian coordinates are not bond-length, bond-angle or torsion internal coordinates.

Items with properties and description:

- `annotation_id` (key, required, data type: int, parent: `_ma_input_annotation.ordinal_id`): The identifier for the annotation assignment.

- `frame_id` (required, data type: int, parent: `_ma_input_annotation_frame.id`): The identifier for the coordinate frame.

- `Cartn_x` (required, data type: float): The x component of the coordinate target in angstroms.

- `Cartn_y` (required, data type: float): The y component of the coordinate target in angstroms.

- `Cartn_z` (required, data type: float): The z component of the coordinate target in angstroms.

## Initial shared definitions and validation rules

The proposed initial vocabulary is deliberately small. `sequence identity` (component, residue, one-body) specifies a chemical component for one existing polymer residue; `absolute coordinate` (vector3, atom, one-body) specifies one atom target in a model Cartesian frame; `relative coordinate` (vector3, atom, one-body) specifies one atom target in an independent rigid frame; `task label` (text, system, zero-body) is descriptive metadata only. These names are draft definitions, not registered official terms. Other definitions must declare an unambiguous version and scientific meaning; generic storage alone does not establish cross-tool interoperability. Unknown required definitions are rejected by an executing consumer. Final vocabulary ownership and extension identifiers require WG agreement.

1. Zero-body assignments have no feature operands. One-body assignments have only feature_id_1; two-body assignments have both. Feature types must agree with the definition. Pair definitions declare symmetry; reversed symmetric duplicates must not conflict. A scalar value can be two-body; a three-component vector can be one-body.
2. `specified` has exactly one payload of the declared type. Other states have none. `unconstrained` is permitted only for conditions. `unknown` records unavailable information, and `not_applicable` records inapplicability. Missing records make no claim unless an explicitly versioned profile defines a default. CIF null tokens retain their standard meanings.
3. Zero and false can be specified values only where the definition gives them that meaning. They are not universal absence sentinels. Import adapters must translate legacy masking semantics by condition type; for example, RFD4 hotspot false is no hotspot request, not an anti-hotspot condition.
4. Numeric values must be finite. All three Cartesian components are required for a specified vector; the initial vocabulary uses angstroms. Partial-axis constraints are outside this initial proposal.
5. Coordinate annotations select exactly one atom. Sequence-identity annotations select exactly one polymer residue. Model IDs point to `_ma_model_list.ordinal_id`, including the frame's model ID, and atom selection must belong to that model. Bare atom-array positions are never structural identifiers.
6. A model Cartesian frame requires model_id. An independent rigid frame has no fixed placement and no model_id in the frame row; its common frame ID groups its coordinate targets. Rigid frames preserve internal geometry up to translation and proper rotation, not reflection. An assignment's model_id still identifies the source subjects. Reframing transforms all targets consistently. Renaming a whole group preserves geometry; changing its membership requires revalidation. A coordinate payload alone does not infer group membership or permission to move other atoms.
7. Required-for-execution means the consumer must interpret the condition, not that a stochastic generator is guaranteed to satisfy it. Support reports, adherence evaluation and failure accounting remain separate. Conditions and prepared features are distinguished from output confidence and experimental validation.
8. Link annotation data into the consuming protocol's input data group. If preparation produces an annotation dataset, link it as output of that preparation step and input of the next step. In the example, use existing `ma_data.content_type=other` and `content_type_other_details='Input annotations'`; adding a dedicated `input annotations` enum can be considered after scope agreement. No additions from #31 need to be changed.

## Category example

See [example.cif](example.cif) for the complete illustrative fragment. It combines four annotation assignments with existing feature, data-group and protocol categories:


```cif
loop_
_ma_input_annotation_type.id
_ma_input_annotation_type.name
_ma_input_annotation_type.version
_ma_input_annotation_type.description
_ma_input_annotation_type.data_type
_ma_input_annotation_type.feature_type
_ma_input_annotation_type.body_order
_ma_input_annotation_type.unit
_ma_input_annotation_type.symmetric
1 'absolute coordinate' draft-1 'Required atom coordinate in a model Cartesian frame' vector3 atom 1 angstroms .
2 'sequence identity' draft-1 'Required chemical identity of one existing polymer residue' component residue 1 none .
3 'task label' draft-1 'Descriptive label of an input dataset' text system 0 none .
loop_
_ma_input_annotation.ordinal_id
_ma_input_annotation.type_id
_ma_input_annotation.data_id
_ma_input_annotation.model_id
_ma_input_annotation.feature_id_1
_ma_input_annotation.feature_id_2
_ma_input_annotation.purpose
_ma_input_annotation.value_state
_ma_input_annotation.required_for_execution
1 1 2 1 1 . condition specified YES
2 1 2 1 2 . condition unconstrained NO
3 2 2 1 3 . condition specified YES
4 3 2 . . . 'prepared feature' specified NO
loop_
_ma_input_annotation_value.annotation_id
_ma_input_annotation_value.value_comp_id
_ma_input_annotation_value.value_text
3 ALA .
4 . 'Illustrative task'
_ma_input_annotation_frame.id 1
_ma_input_annotation_frame.kind 'model Cartesian'
_ma_input_annotation_frame.model_id 1
_ma_input_annotation_vector.annotation_id 1
_ma_input_annotation_vector.frame_id 1
_ma_input_annotation_vector.Cartn_x 0
_ma_input_annotation_vector.Cartn_y 0
_ma_input_annotation_vector.Cartn_z 0
```


The input model contains atom IDs 10 and 20. Features 1 and 2 select those atoms, and feature 3 selects residue A/1. Annotation 1 fixes atom 10 at (0,0,0); annotation 2 leaves atom 20 unconditioned; annotation 3 fixes residue A/1 to ALA; annotation 4 labels the task. The existing `backbone generation` step consumes both the coordinate data and annotation data through input group 1. This is not an executed model run or a complete deposition.

## Exchange profiles and boundaries

**Pipeline exchange.** Preserve chemical identity, feature references, condition definitions and coordinate frames through supported operations. Record structure-to-structure correspondence in a versioned associated mapping artifact, scoped by artifact hash, data block, model and local IDs, including one-to-many assembly copies and generated/deleted subjects. This mapping profile is an acceptance requirement; it is not implemented by the five categories above. Do not silently transform an unsupported task into another task.

**Prepared datasets.** Associate a manifest containing source/CCD snapshots, licenses, checksums, preparation parameters, stable example IDs and split provenance. Distinguish prepared structures from stochastic sampled examples and model-specific feature tensors; include token-to-structure and tensor-axis mappings where applicable. Custom component definitions take precedence only under an explicit recorded chemistry policy.

**Benchmarks.** Associate a manifest defining tasks, permitted information, seeds and sampling budgets, all scheduled attempts, failure states, evaluator versions, selections/alignment, thresholds and denominators. Report valid-only summaries separately from all-attempt summaries. Unavailable evaluation evidence is `not_evaluated`, not a measured zero. Equal samples and equal compute are distinct comparisons. Existing QA categories hold suitable model-level/feature-level results; attempt accounting is associated metadata.

These are proposed application-profile requirements. The manifest schemas and production transformations require further validation before claiming profile conformance. Future residues, variable-length topology, fully model-independent coordinate-free task files, multi-model selection rules and portable token-index semantics are separate follow-up designs. A small first increment must not imply full support for every RFD4 condition.

## Implementation evidence and migration

Pinned sources: AtomWorks `a0c63a8f77e76aba93857f444d02092354972c45`; RFD4-Proteina `68058693cb88762a8aaf806571e13b291ce6318a`.

| Implementation convention | Exchange requirement |
| --- | --- |
| `name`, `n_body`, `level`, `dtype`, `value_shape`, aliases and defaults in StandardAnnotation | Preserve scientific meaning, body order, subject selection and type; aliases and Python class names are adapter concerns. |
| Residue-level annotations broadcast over atoms | Check consistency before collapsing to a residue feature; storage granularity is not semantic scope. |
| Scalar one-body data in atom_site; vectors/pairs in idx/val categories | Map original row indices to explicit structural IDs before edits; keep file encoding independent of semantic meaning. |
| `C_SEQ` uses `<M>`; `C_CRD` uses NaN; hotspot uses false | Translate condition-specific sentinels explicitly. Do not infer zero/false/absence equivalence for all fields. |
| `C_IDX` defaults to true; index groups depend on molecules and indexed status | Materialize or declare defaults; portable index relations need explicit offsets and molecular context, not raw group integers. |
| Positive `C_CRDGRP` plus `C_INTCRD` describes freely placed rigid groups | Preserve group membership and group-local Cartesian targets; reserved IDs -1/0 and int16 limits remain implementation details. |
| Sequence probabilities distinguish NaN from zero | Specify chemical-component vocabulary, partial mass and exact-identity conflict policy; do not standardize token-channel numbers. |
| FinalizeSequenceConditioning can infer additional sequence information from atomization/sidechain constraints | Record the effective model inputs and any implied conditions. Benchmarking must account for information actually supplied. |
| RFD4 annotation-preserving parser avoids renumbering preparation operations | Require correspondence and explicit loss reporting; parser success alone is not preservation. |

The simple Coordinate mask accepts any finite component; RFD4 CoordinateGroup assignment separately rejects partially specified absolute vectors. This is an API-level distinction, not evidence that all RFD4 execution accepts partial vectors. Saved internal targets may be preserved or materialized from live coordinates by specific transforms; any reconstruction must be recorded by adapters.

## Review and validation

The DDL2 fragment uses existing ModelCIF conventions for keys, parent links and category descriptions. It is a candidate for direct incorporation into `base/mmcif_ma-core.dic` after agreement; it is not a new syntax or a competing file type. This draft PR changes no released dictionary, does not assign a release version, and removes nothing from ModelCIF. Maintainers determine final names, integration and release.

Checks cover CIF parsing, declared fields/types/keys/enumerations, proposed and existing parent references, representative scientific invariants, row reorder preservation and rejection of malformed example mutations. Positive fixtures cover an independent rigid frame and an explicit false pairwise prepared feature. Full RCSB dictionary assembly, general DDL2 validation, deposition validation, BinaryCIF, runtime adapters, independent-tool workflows and scientific benchmarks remain release gates. The proposal intentionally does not equate a candidate-schema check with standards conformance.

Review decisions: typed dedicated conditions versus the generic type/value layer; registry ownership; model-free inputs and future topology; independent frame semantics; mapping/profile governance; and the smallest vocabulary justified by independent consumers.

## References

- [ModelCIF dictionary and release history](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/)
- [Protein-design vocabulary proposal #31](https://github.com/ihmwg/ModelCIF/issues/31)
- [Category proposal style #29](https://github.com/ihmwg/ModelCIF/issues/29)
- [2026 ModelCIF update](https://doi.org/10.1016/j.jmb.2026.169658)
- [AtomWorks annotation base](https://github.com/RosettaCommons/atomworks/blob/a0c63a8f77e76aba93857f444d02092354972c45/src/atomworks/io/utils/standard_annotations/base.py)
- [AtomWorks serialization](https://github.com/RosettaCommons/atomworks/blob/a0c63a8f77e76aba93857f444d02092354972c45/src/atomworks/io/utils/standard_annotations/serialization.py)
- [AtomWorks conditions](https://github.com/RosettaCommons/atomworks/blob/a0c63a8f77e76aba93857f444d02092354972c45/src/atomworks/ml/conditions/definitions.py)
- [RFD4 conditions](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/conditions.py)
- [RFD4 sequence conditioning](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/transforms/sequence_conditioning.py)
- [RFD4 parsing presets](https://github.com/RosettaCommons/RFD4-Proteina/blob/68058693cb88762a8aaf806571e13b291ce6318a/src/rfproteina/utils/parse_presets.py)

## Compatibility implementation

See [compatibility.md](compatibility.md) for the AtomWorks/RFD4 implementation plan and acceptance gates. To reproduce bounded checks, install gemmi 0.7.5 in an isolated environment and run `python check_examples.py`. Tests use the repository’s published dist/mmcif_ma.dic.
