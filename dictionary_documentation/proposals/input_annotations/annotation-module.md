# A compact ModelCIF annotation module

**Design proposal for working-group review, not a released dictionary.** Preserve Annotated CIF's compact tables: put the subject reference and its scalar or XYZ value on the same row, with shared metadata written once. The categories below specify the worked example. Additional domains, general arrays, grouping, logical topology and correspondence remain in the full scope and require item-level completion.

## Objective and representation

Incorporate the annotation data contract used by AtomWorks and RFD4-Proteina into ModelCIF. Both libraries implement one standardized representation through their existing annotation/I/O APIs. Older files may be converted; permanent legacy compatibility is unnecessary. Keep the familiar compact layout wherever it can express the scientific meaning clearly.

Current scalar annotations are extra `atom_site` columns; nonscalar one-body and sparse two-body annotations use index/value rows. The proposed dictionary-defined categories retain that row-oriented approach while replacing array offsets with structural references. Registered and custom definitions share fixed typed value fields, so adding a custom annotation does not require inventing unregistered CIF item names.

For common values, an annotation is:

**shared definition + set context + one row containing subject, value and any frame**

Set metadata supplies data/model, stage, purpose and execution requirements. Definition metadata supplies scientific meaning/version, level, body order, type, units and defaults. A scalar stays in one typed field; an XYZ target stays in three named fields on one row. Shape/axis metadata is needed only for general arrays whose interpretation is not already fixed by the dictionary. There is one authoritative encoding for each declared value kind.

| Current API concept | Compact standard representation |
| --- | --- |
| Names, registry and aliases | Versioned shared/custom definition; historical names map during conversion. |
| Six semantic levels | Atom, residue, chain, molecule, token and system; direct structural references where sufficient, explicit membership for groups. |
| `n_body` and symmetry | Zero, one or two subject references in the value row; pair endpoints and symmetry remain explicit. |
| Scalar type and `value_shape` | Typed scalar fields or `x/y/z`; general arrays use declared dimensions, axis labels and element states only when needed. |
| Defaults and masks | Registered default/state semantics; explicit overrides; structure-dependent defaults materialized with provenance. |
| Broadcasting and sparse pairs | Validate consistency before collapsing atom-broadcast values; preserve sparse rows and omitted-value rules. |
| Coordinate/index groups | Frame reference on each coordinate row; explicit grouping/context and relative index offsets. |
| Expandable segments | Logical positions/segments, length bounds, order/anchors and realization mappings. |
| Source and derived annotations | Artifact-scoped correspondence and provenance; existing QA, energy and experimental categories retain their meanings. |

The [coverage table](annotation-coverage.md) retains all 59 inventoried entries. Full scope includes extensibility and scientific meaning, rather than executable Python functions or arbitrary NumPy dtype encodings.

## Levels and body order

| Level | Subject reference | Example |
| --- | --- | --- |
| Atom | `atom_site.id`, within the set's model | Coordinate target or hotspot |
| Residue | Model-scoped asym/sequence identity, or a logical site | Fixed component or sequence probability |
| Chain | Model-scoped chain instance | Chain membership relation |
| Molecule | Explicit molecular group and context | Molecular annotation |
| Token | Explicit ordered membership and tokenizer/version | Index group |
| System | Annotation set/data context | Zero-body task label |

Body order counts subjects, not value components or atoms inside a group. A system label has no subject fields; a point has one atom reference; a pair relation has two subject references on the same row. Chain and token/molecule groups may select many atoms without changing body order. Existing ModelCIF features may identify complex selections; ordinary atom/residue rows do not require an additional feature or subject table.

The worked atom/residue categories below are the first concrete items. System, chain/group, pair, logical-site and array records complete the same module; their exact items require working-group review. Pair rows should use two direct structural references where possible, or existing feature/group references for complex subjects, with explicit model/instance context. Avoid forced dense matrices or a separate operand row for each endpoint.

## Concrete category and item definitions

Names are provisional. Required items apply when the category is present; keys are unique within the data block. Null markers retain CIF meanings: `?` is unknown and `.` inapplicable. Neither substitutes for the explicit state `unconstrained`.

### ma_annotation_definition

Category description: Data items in MA_ANNOTATION_DEFINITION identify the scientific meaning and interpretation shared by annotation rows.

- `id` (key, required, int): Local definition identifier.
- `definition_key` (required, line), `version` (required, code): Namespaced scientific definition and version. The example's `proposal:` definitions are specified below and are not registered terms.
- `name` (required, line), `description` (required, text): Human-readable name and interpretation.
- `subject_level` (required, code): `atom`, `residue`, `chain`, `molecule`, `token` or `system`.
- `body_order` (required, int): 0, 1 or 2. Zero-body definitions use system context.
- `value_kind` (required, code): `boolean`, `integer`, `real`, `text`, `component`, `point3`, `vector3` or `array`. A point translates and rotates; a vector rotates only. Other geometric tensors require declared transformation rules.
- `units` (required, line): Units, or `none` for dimensionless/non-numeric values.
- `omitted_state` (required, code): `unconstrained`, `unknown` or `not_applicable` for omitted applicable entries when this definition is used in a set. This is not a numeric default. Uniform typed defaults and categorical domains require supplementary definitions.
- `symmetric` (boolean, required for body order 2): Whether exchanging endpoints preserves meaning; `YES` or `NO`.

Registered definitions fix common shapes and vocabulary once in the dictionary/specification. Files identify the definition/version and need not reproduce Cartesian axes or a registered component alphabet. Custom shapes/domains must be explicitly declared through the module's supplementary records; a prose label is insufficient.

### ma_annotation_set

Category description: Data items in MA_ANNOTATION_SET give the shared data, model and workflow context for annotation rows.

- `id` (key, required, int): Set identifier.
- `data_id` (required, int; parent `_ma_data.id`): Annotation data artifact.
- `model_id` (int; parent `_ma_model_list.ordinal_id`): Reference model for structural rows. Required for the worked atom/residue categories; absent for coordinate-free tasks. Separate model contexts use separate sets.
- `stage` (required, code): `authored`, `effective` or `derived`.
- `purpose` (required, line): `condition`, `prepared feature` or `derived reference`.
- `required_for_execution` (required, boolean): `YES` or `NO`. A consumer must reject unsupported required conditions before execution.

Rows with different context, purpose or execution requirements use different sets. Transformations between sets reuse ModelCIF data groups and protocol steps. Required interpretation does not guarantee condition satisfaction.

### ma_annotation_atom and ma_annotation_residue

Category descriptions: MA_ANNOTATION_ATOM stores an annotation and its value for one atom. MA_ANNOTATION_RESIDUE stores an annotation and its value for one polymer residue. Non-polymer groups and future positions use the supplementary group/site representation, without invented polymer sequence identifiers.

Both categories have these items:

- `id` (key, required, int): Row identifier within its category.
- `set_id` (required, int; parent `_ma_annotation_set.id`): Shared context.
- `definition_id` (required, int; parent `_ma_annotation_definition.id`): Definition with matching level and body order 1.
- `state` (code; dictionary default `specified`): `specified`, `unconstrained`, `unknown` or `not_applicable`. The column may be omitted when every row has its default state.
- `value_real` (float), `value_integer` (int), `value_boolean` (boolean: `YES`/`NO`), `value_text` (text), `value_comp_id` (ucode; parent `_chem_comp.id`): Use only the field matching a scalar definition's value kind.
- `x`, `y`, `z` (float): Three finite components, all required for a specified `point3`/`vector3`. Other payload fields are then inapplicable.
- `frame_id` (code; parent `_ma_annotation_frame.id`): Required for specified geometric values, inapplicable for frame-independent scalars.

Only applicable columns need be written. Explicit non-specified states have no value payload. General arrays need supplementary payload/axis records and a defined link from their owning row; these items remain to be completed. They must not become a second encoding for the scalar and XYZ kinds above.

Atom subject item:
- `atom_id` (required, code; parent `_atom_site.id`): Atom in the set's model. Verify its `pdbx_PDB_model_num` against that context; array row offsets are not atom identities.

Polymer-residue subject items:
- `label_asym_id` (required, code; parent `_struct_asym.id`) and `label_seq_id` (required, int): Residue in the set's model. The asym identifies the entity; sequence identity must agree with that entity's polymer sequence and model context. Full dictionary assembly must express the corresponding entity/sequence links.
- `component_id` (ucode; parent `_chem_comp.id`): Component parameter for definitions such as sequence probability. It identifies the candidate being constrained, not the observed residue identity or a component-valued payload. Required for the probability definition; otherwise inapplicable unless the definition explicitly uses it.

Within a category, `(set, definition, subject, component parameter when applicable)` must be unique. Duplicate/conflicting values are errors, not an ordering convention. Absence of a definition from a set does not instantiate it. For a used definition, omitted applicable subjects/components follow its declared omission rule within the set's scope. Structure-dependent defaults must be materialized; they cannot be inferred from an unspecified Python function.

### ma_annotation_frame

Category description: Data items in MA_ANNOTATION_FRAME define the Cartesian frame and permitted placement of geometric values.

- `id` (key, required, code): Frame identifier.
- `kind` (required, line): `model Cartesian` or `independent rigid`.
- `model_id` (int; parent `_ma_model_list.ordinal_id`): Required for model Cartesian placement and must match the consuming set; inapplicable for an independent rigid frame.

Points sharing an independent rigid frame retain their relative geometry while the whole frame may rotate and translate. This represents saved group-local Cartesian coordinates, not bond lengths/angles/torsions. Group renaming must preserve references; changing membership requires revalidation.

## Worked definitions and CIF interpretation

The full [worked CIF](worked-annotations.cif) uses five proposed categories: definitions, sets, frames, atom rows and residue rows. It supplies existing structural/workflow records without adding a feature for each atom.

`proposal:coordinate`, version `draft-1`, is an atom-level, one-body `point3` in angstroms, with complete finite XYZ values and omission meaning unconstrained. Two atom rows reference atoms 10 and 20 and frame G; their targets are `(0,0,0)` and `(3.8,0,0)`. Set 1 supplies model 1, authored condition status and required interpretation once for both rows.

`proposal:sequence_probability`, version `draft-1`, is a residue-level, one-body real value parameterized by chemical component. This draft term uses the fixed canonical-polymer-28 domain:

`ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL A C G U DA DC DG DT`.

That domain belongs to this definition, not to the generic residue category or a model's private channel ordering. Other alphabets require a separately versioned definition/domain, including support for custom components. Only components referenced by actual rows need corresponding component records in the fragment.

The two probability rows specify ALA at 0.7 and GLY at 0 for residue A/1. The other 26 components are unconstrained and can share the remaining 0.3. Explicit values must lie in [0,1] and sum to at most 1; a fully specified distribution sums to 1. Zero excludes an identity. Exact-identity precedence and canonicalization require agreement before registering the term; this proposed interpretation does not establish conformity of every current RFD4 normalization path. The reference structure's observed identity is not itself a requested identity condition.

## Full scope and integration

Retain explicit categorical domains and typed defaults; token/molecule membership, order and context; index groups and relative offsets; logical design sites, length bounds and connectivity; and artifact-scoped correspondence, including generated/deleted subjects and assembly copies. General shaped values retain rank, axis labels/order, per-element states and transformation semantics. These supplementary items are required for complete API coverage but need not appear in ordinary scalar/XYZ files.

AtomWorks keeps its registry, array storage and accessors while its codec maps compact rows and preserves/remaps metadata after edits. RFD4 keeps ConditionBase while recording authored/effective inputs and provenance. Readers must distinguish optional retention from execution support and reject unsupported required conditions. Existing QA, energy, experimental-validation and applicable restraint categories remain authoritative for their respective quantities.

See the [overview](README.md) for migration and exchange profiles. Complete dictionary assembly, the remaining items, representative conversion/equivalent-input tests, measured CIF/BinaryCIF performance and independent interoperability precede a release claim.
