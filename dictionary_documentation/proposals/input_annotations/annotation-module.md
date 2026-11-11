# A unified ModelCIF annotation module

**Design proposal for working-group review, not a released dictionary.** This document states the complete target scope and specifies a concrete record layout for the accompanying worked CIF. Items for additional domain, grouping, logical topology and correspondence semantics still need completion within this scope.

## Objective

Incorporate the data model underlying Annotated CIF into ModelCIF. AtomWorks and RFD4-Proteina should become implementations of this ModelCIF capability, with one authoritative standardized representation for newly written annotations. Existing Annotated CIF files may be converted to the agreed representation; permanent backward compatibility is not a design requirement. A permanently separate annotation standard, or mandatory private annotation sidecar, is not the proposed endpoint.

The scope is the complete annotation **data contract**, including extensibility, rather than Python methods or model implementation code. Preserve the current public annotation APIs where possible. A library can retain arrays, registries and convenience aliases while its reader/writer implements ModelCIF directly. A consumer need not execute every scientific condition to read the file, but must reject unsupported required conditions before execution.

## Data model to standardize

| Current API concept | Required ModelCIF representation |
| --- | --- |
| `name`, registry, aliases | Stable definition identifier and version; human-readable name; controlled scientific vocabulary and namespaced custom definitions. Historical aliases may be converter mappings; their spelling does not constrain the standard. |
| `level` | Atom, residue, chain, molecule, token and system semantic levels. Structural selection and semantic level are separate. |
| `n_body`, `is_symmetric` | Zero, one or two ordered subject operands; explicit pair symmetry and duplicate/conflict rules. Group size does not change body order. |
| `dtype`, enum domain | Boolean, integer, real, text and component values; categorical codes have explicit meanings. Define supported portable scalar domains explicitly rather than promising all NumPy dtypes. Machine widths and text capacities must not silently truncate values. |
| `value_shape` | Scalar or shaped values with rank, dimension lengths, axis order and, when needed, axis labels. Cartesian points, vectors and probability arrays have distinct definitions. |
| Defaults and masks | Explicit presence/state, uniform defaults when valid, per-element states for partially specified arrays, and materialized structure-dependent defaults with provenance. |
| Array broadcasting and sparse pairs | Subject membership and a defined broadcast rule; sparse relations with explicit omitted-value semantics. No dense pair matrix requirement. |
| Coordinate and index groups | Scoped membership, Cartesian frame semantics and explicit relative index offsets; reserved Python integers have no universal scientific meaning. |
| Expandable segments | Logical design sites, minimum/maximum length and connectivity/order constraints before realization; realized subjects linked afterwards. |
| Source annotations and reference geometry | Input/output correspondence and derived reference values linked to data and protocol steps. Existing QA/energy/experimental categories remain authoritative for their results. |
| Registered custom annotations | The same dictionary-defined containers and type rules; namespaced meaning/version, declared support and faithful retention. A description alone does not establish scientific equivalence. |

Whole-API support requires both schema expressiveness and tested mappings. The [coverage table](annotation-coverage.md) assigns all 59 inventoried entries to target representations and records unresolved semantics. It is a scoped inventory, not proof that every plugin or registry entry has been enumerated.

## Dictionary structure and remaining scope

The concrete items below cover definitions, annotation sets, subjects, shapes/axes, frames, assignments, operands and typed values. Use general `ma_annotation_*` names because intermediate/output reference data also need annotations. Existing restraint, QA, energy and experimental-validation categories remain authoritative wherever their meanings fit.

Additional records must complete these parts of the same module:

- **Domains and defaults:** versioned categorical meanings and typed uniform defaults; materialize structure-dependent defaults with provenance rather than serializing Python functions.
- **Membership and context:** explicit token/molecule grouping definition/version, ordered or nested membership, assembly-instance identity and relative index offsets. Existing atom/residue/entity-instance feature categories encode selections, not all these semantics.
- **Logical design sites:** positions or variable-length segments, bounds, molecular context, anchors/order and realization mappings. Link existing entity/sequence records when available; do not invent atom_site rows. Isolated coordinate-free tasks need an agreed application profile.
- **Correspondence:** data/artifact-scoped source and destination subjects, generated/deleted subjects and one-to-many copies, linked to the responsible protocol step. A short source label cannot be the only identity. Structural edits must remap or explicitly invalidate affected metadata.

These are required parts of the agreed target, although their exact items remain to be specified. The worked layout is a concrete example of the generic module, not its complete dictionary implementation. Large associated payloads must retain standard-defined shapes, axes and interpretation.

## How an annotation is constructed

`definition + set + ordered subject operands + typed value/state + optional frame`

| Example | Semantic level | Body order | Value | Supporting records |
| --- | --- | ---: | --- | --- |
| Task label | system | 0 | text scalar | Annotation set/data link |
| Fixed residue identity | residue | 1 | component scalar | Existing residue selection, or a declared logical position |
| Saved rigid motif target | atom | 1 | real shape (3) | Atom selection and independent rigid frame |
| Token index group | token | 1 | scoped group reference | Token membership and relative offsets/context |
| Base-pair type | residue | 2 | categorical scalar | Two residue operands and domain/symmetry definition |
| Sequence distribution | residue | 1 | real shape (k) | Component-labelled axis and per-component state |
| Expandable segment bounds | logical segment | 1 | integer bounds | Segment subject, anchors/order and realization mapping |

The 28 scalar probability classes currently exposed by RFD4 can map reversibly to component-keyed values of one shared probability definition. Keep component-specific explicitness: zero excludes an identity; unspecified leaves it unassigned. Specify remaining mass, normalization and exact-identity precedence. Full-API support also permits separate scalar component assignments if the working group selects that encoding; independently editable duplicate encodings should not be authoritative simultaneously.

## Concrete item definitions for the worked CIF

The following is one proposed layout of the module, using the category-description and item-property style of ModelCIF proposals. All names are provisional. Required items apply when the category is present. References are scoped to the CIF data block unless explicitly stated otherwise. The complete example is [worked-annotations.cif](worked-annotations.cif); no separate annotation file format is introduced.

### ma_annotation_definition

Category description: Data items in the MA_ANNOTATION_DEFINITION category identify the scientific meaning, subject level and value interpretation of an annotation.

- `id` (key, required, int): Local definition identifier.
- `definition_key` (required, line): Namespaced identifier of a shared or custom scientific definition. The example's `proposal:` names are draft terms, not registered identifiers.
- `version` (required, code): Version of that definition; combined with its key it identifies its meaning.
- `name` (required, line): Human-readable definition name.
- `description` (required, text): Scientific interpretation and term-specific rules.
- `subject_level` (required, code): `atom`, `token`, `residue`, `chain`, `molecule` or `system`.
- `body_order` (required, int): Number of subject operands: 0, 1 or 2. Zero-body definitions use system scope.
- `value_type` (required, code): `boolean`, `integer`, `real`, `text` or `component`.
- `units` (required, line): Value units, or `none` for non-numeric/dimensionless data.
- `transform_rule` (required, code): `point`, `vector` or `invariant` for the quantities illustrated here. Other geometric tensors require further declared transformation rules before execution support can be claimed.
- `omitted_element_state` (required, code): Interpretation of an omitted element within a present assignment: `unknown`, `unconstrained` or `not_applicable`. It never implicitly means numeric zero. Additional uniform-value defaults require an explicit typed default definition.
- `symmetric` (boolean, required for body order 2): Whether exchanging the operands preserves meaning; `YES` or `NO`.

The rigid-point definition requires three finite Cartesian coordinates in angstroms. The partial-probability definition fixes specified component probabilities, leaves omitted components unconstrained, and requires specified values in [0,1] with total at most 1; a complete distribution sums to 1. Unspecified components can share remaining mass. This is a proposed declarative interpretation, not a claim that all current RFD4 normalization paths already conform. Exact-identity precedence and canonicalization must be agreed for the registered scientific term.

### ma_annotation_set

Category description: Data items in the MA_ANNOTATION_SET category connect annotations to the data used or produced by a modeling protocol.

- `id` (key, required, int): Annotation-set identifier.
- `data_id` (required, int; parent `_ma_data.id`): Data artifact represented by this set.
- `stage` (required, code): `authored`, `effective` or `derived`. Transformations between sets use the existing protocol/data-group relations.

### ma_annotation_subject

Category description: Data items in the MA_ANNOTATION_SUBJECT category identify the semantic subjects on which annotations are defined.

- `id` (key, required, int): Subject identifier.
- `level` (required, code): One of the six semantic levels above.
- `model_id` (int; parent `_ma_model_list.ordinal_id`): Structural model containing the subject, when applicable.
- `feature_id` (int; parent `_ma_feature_list.feature_id`): Existing structural selection supporting the subject, when applicable.

The example requires model and feature references for its existing atoms/residue. Token/molecule context, ordered membership and logical future subjects require supplementary records described in the full scope above; a feature alone is not their complete semantics. Coordinate-free tasks must not manufacture coordinate models to satisfy these references.

### ma_annotation_shape and ma_annotation_axis

Category descriptions: MA_ANNOTATION_SHAPE defines the shape and traversal order of a value. MA_ANNOTATION_AXIS defines its individual dimensions.

Shape items:
- `id` (key, required, int): Shape identifier.
- `rank` (required, int): Number of axes, at least zero; a scalar has rank zero.
- `element_order` (required, code): `row-major`: the last axis varies fastest.

Axis items:
- `shape_id`, `axis_order` (composite key, required, int): Parent `_ma_annotation_shape.id` and one-based axis order.
- `length` (required, int): Nonnegative number of elements on that axis.
- `label_kind` (required, code): `Cartesian`, `component`, `text` or `unlabelled`.

### ma_annotation_axis_label

Category description: Data items in the MA_ANNOTATION_AXIS_LABEL category give semantic labels to positions along an annotation-value axis.

- `shape_id`, `axis_order`, `index` (composite key, required, int): Parent axis and one-based position. The first two items jointly reference the key of MA_ANNOTATION_AXIS.
- `label` (line): A Cartesian or text label, for example `x`, `y` or `z`.
- `comp_id` (ucode; parent `_chem_comp.id`): Chemical component at this position on a component-labelled axis.

Exactly the applicable label field is populated for each labelled position. Component axes list their full declared alphabet; identities are not inferred from array order. A different alphabet uses a different shape/axis record while reusing the scientific definition.

### ma_annotation_frame

Category description: Data items in the MA_ANNOTATION_FRAME category describe the placement freedom and Cartesian frame of geometric annotation values.

- `id` (key, required, code): Frame identifier.
- `kind` (required, line): `model Cartesian` or `independent rigid`.
- `model_id` (int; parent `_ma_model_list.ordinal_id`): Required for a model Cartesian frame; inapplicable for an independent rigid frame.

Points in one independent rigid frame retain their relative geometry while that whole frame may rotate and translate. The saved values are Cartesian points, not bond-length/angle/torsion internal coordinates. Frame membership follows the assignment's frame reference.

### ma_annotation

Category description: Data items in the MA_ANNOTATION category identify annotation assignments and their interpretation.

- `id` (key, required, int): Assignment identifier.
- `set_id` (required, int; parent `_ma_annotation_set.id`): Annotation set.
- `definition_id` (required, int; parent `_ma_annotation_definition.id`): Scientific definition.
- `shape_id` (required, int; parent `_ma_annotation_shape.id`): Shape, including rank-zero scalar shapes.
- `frame_id` (code; parent `_ma_annotation_frame.id`): Frame for geometric values; inapplicable for frame-independent values.
- `purpose` (required, line): `condition`, `prepared feature` or `derived reference`. Existing ModelCIF results categories remain authoritative for their respective results.
- `value_state` (required, code): `specified`, `unconstrained`, `unknown` or `not_applicable`. `specified` means a value container is supplied; individual elements can still be unconstrained. Other assignment states have no value rows.
- `required_for_execution` (required, boolean): `YES` or `NO`. Required interpretation is not a guarantee of condition satisfaction.

### ma_annotation_operand

Category description: Data items in the MA_ANNOTATION_OPERAND category identify the ordered subjects of an annotation assignment.

- `annotation_id`, `position` (composite key, required, int): Parent `_ma_annotation.id` and operand position, from 1 through the definition's body order.
- `subject_id` (required, int; parent `_ma_annotation_subject.id`): Subject operand.

A zero-body annotation has no operand rows. Every subject has the definition's semantic level. Pair symmetry and duplicate/conflict rules apply independently of shape and the number of atoms selected by each subject.

### ma_annotation_value

Category description: Data items in the MA_ANNOTATION_VALUE category store typed scalar or shaped annotation values and explicit element states.

- `id` (key, required, int): Value-row identifier.
- `annotation_id` (required, int; parent `_ma_annotation.id`): Assignment.
- `element_index` (required, int): One-based flattened position in the declared row-major shape; 1 for a scalar. The assignment/index pair is unique.
- `state` (required, code): `specified`, `unconstrained`, `unknown` or `not_applicable`.
- `value_real` (float), `value_integer` (int), `value_boolean` (boolean: `YES`/`NO`), `value_text` (text), `value_comp_id` (ucode; parent `_chem_comp.id`): Exactly the definition's typed slot is populated for a specified element; no payload is present for other states. Numeric values are finite.

Axis positions and labels are decoded from the declared shape, rather than a private tensor convention. Missing element rows use the definition's omitted-element state; an entirely absent assignment does not inherit that rule. CIF `?` and `.` retain unknown/inapplicable meanings and do not encode unconstrained conditions by themselves.

## Worked records and interpretation

The example links annotation set 1 to data 2, alongside the reference coordinate data in the backbone-generation input group. Definitions 1 and 2 describe rigid points and partial sequence probabilities. Subjects 1/2 select atoms 10/20; subject 3 selects residue A/1. Shape 1 is `(3)` with x/y/z labels; shape 2 is `(28)` with explicit chemical-component labels.

Assignments 1 and 2 share frame `G`, with targets `(0,0,0)` and `(3.8,0,0)`. Assignment 3 specifies ALA at probability 0.7 and GLY at 0; the other 26 components remain unconstrained. These are requested conditions, not observed frequencies or claims that generated models satisfy them. The reference structure's existing residue identity is not itself an identity condition.

The full file supplies all supporting definitions, shape labels, selections and protocol links. Its workflow uses the released spelling `structure validation`. The dictionary additions, term registration and broader grouping/topology/correspondence item definitions remain proposed work.

## Integration

See the [proposal overview](README.md) for library integration, dataset migration and exchange-profile requirements. Full coverage includes every inventoried term and generic API fixtures, with separate claims for representation, roundtrip preservation, transformations and execution. Dictionary assembly, reference implementations and independent CIF/BinaryCIF tests are required before release. Adoption, naming and release remain ModelCIF Working Group decisions.
