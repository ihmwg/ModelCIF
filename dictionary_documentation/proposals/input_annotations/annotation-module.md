# Compact annotation module

Proposed component 0.2.0. The [DDL2 component](../../../base/mmcif_ma-annotation.dic) defines items, types, keys and parent links. These rules supply conditional and scientific interpretation. All category names below have prefix `ma_annotation_`; all IDs are local to the data block.

## Three value layouts

An annotation consists of a **definition, shared set context and subject/value row**. A definition declares scientific identity/version, semantic level, body order, value type, units and omission behavior. A set declares annotation data, optional reference model, authored/effective/derived stage, purpose and execution requirements.

| Layout | Subject fields |
| --- | --- |
| `atom` | `atom_id`, for one structural atom |
| `residue` | Joint `label_asym_id`, `label_entity_id`, `label_seq_id`, for one polymer residue |
| `value` | No selector for a system value; `label_asym_id` for a chain; `group_id` for a token/molecule; `subject_id_1` for a logical position/segment; `subject_id_1` and `subject_id_2` for a pair |

Body order counts operands, independently of group size or value shape: 0 for system, 1 for one subject, 2 for a pair. Definitions are atom/residue/chain/token/molecule/system level; pair endpoints have the same declared level and an explicit symmetry rule. Ordinary structural atom/residue values use their direct layout, not a second encoding through `value`. No separate subject records are needed for those rows.

A specified value occupies exactly its typed scalar slot (`value_boolean`, `value_integer`, `value_real`, `value_text`, `value_comp_id`), all three `x/y/z` plus a frame, `array_id` (plus frame for geometric arrays), or `value_group_id`. Booleans use YES/NO, integers are mathematical integers and real values are finite. Unused columns may be omitted. A candidate `component_id` is a parameter, distinct from a component-valued payload or the reference structure's identity.

## States, defaults and execution

`state` defaults to `specified` when its column is absent. Explicit `?`/`.` does not invoke that default. `unconstrained`, `unknown` and `not_applicable` carry no payload and remain distinct. CIF null markers retain their ordinary meanings elsewhere. False and zero are values; converting an inactive historical code to a state requires the particular annotation's semantics.

`value.is_default = YES` declares a uniform scalar default for the set/definition, with no subject, component parameter or partner selector. Otherwise `is_default` is NO, including when the column is absent. Explicit rows override defaults, including explicit non-specified states. A default activates its definition even without other rows. Geometry, arrays, groups, component-parameterized values and exact sequence identities must be materialized. Structure-dependent functions become effective rows with preprocessing provenance.

A definition is active in a set only if a row/default uses it. Omitted applicable values of an active definition inherit its `omitted_state` unless a typed default applies. `(set, definition, subject(s), component parameter, partner context)` is unique; defaults are unique by set/definition. Reversed endpoints duplicate a symmetric pair, and aliases of structural subjects do not create different assignments.

`required_for_execution` requires the consumer to understand the definition, resolve required data and implement the conditions before execution. Generic preservation is insufficient. Unknown required values, unsupported semantics and conflicting effective conditions must be reported. The flag does not assert output satisfaction. Combining sets requires an explicit workflow/profile and a conflict check after combination.

## Definitions and reference scope

A namespaced `(definition_key, version)` has one meaning. Custom definitions document scientific interpretation, units, domains and preparation method for an independent implementation, with a source reference where available. Changed semantics require a new version/key. Executable code is not part of interchange. `example:` terms illustrate storage, not a shared scientific registry.

Use `none` for dimensionless/non-numeric values and `angstroms` for points. Other units require `units_details` describing meaning/conversion and should use existing dictionary unit names where applicable. Custom domains are closed, versioned vocabularies in `domain`/`domain_value`; list every member. Categorical scalar values use symbolic text codes; component domains use unique `chem_comp` identities. Custom component parameters require an explicit domain unless the shared definition fixes it.

Scope is the set model for structural subjects, or its data artifact and declared groups/logical positions for coordinate-free tasks. Atom references belong to that model. Polymer residues use consistent chain/entity/sequence identities, including unresolved positions; non-polymers use groups. Structural subjects/groups identify the model's `ma_data` artifact; logical ones identify their own data artifact. The set's data ID identifies the annotations independently of the model data ID. Cross-file exchange needs the relevant declarations and standard associated-file links, not bare array offsets or unqualified external IDs. Partner/context groups must match the model, or data artifact when coordinate-free.

## Groups, frames and subjects

`group` gives explicit token, molecule, index or context membership and a versioned grouping method. Each `group_member` selects one atom, child group or logical subject. Membership and enclosing-context references are acyclic; direct members are unique. Ordered groups preserve member order; ordinals need not be contiguous. An index group belongs to an enclosing context and contains tokens or unit logical token positions with unique, increasing integer offsets. Offsets have arbitrary origin but preserve differences; offsets between distinct groups are unknown. Expandable segments acquire token offsets after realization. Structural edits remap references or explicitly invalidate dependent annotations.

A `model Cartesian` frame refers to the set model. An `independent rigid` frame permits whole-frame rotation/translation while preserving relative geometry. Points rotate/translate; vectors rotate only. Complete finite XYZ values are required. Group-local Cartesian targets are not bond-angle/torsion coordinates; reserved legacy group integers become frame IDs/kinds and states.

`subject.kind = reference` selects one atom, chain/residue or group for pair endpoints and mappings. `position` or `segment` directly declares a logical subject: atom/residue/token level, no model/structural selector, an ordered coordinate-free context containing it, and explicit length bounds. Positions have length one; segments have `0 <= min_length <= max_length`. Zero permits deletion. A segment value applies to each realized member; differing values need separate positions or post-realization rows. A pair with segment endpoints applies to every realized endpoint combination; the scientific definition determines whether resulting self-relations are meaningful.

## Relations

`relation` uses common source/target subject references for topology and correspondence:

| Relation | Rules |
| --- | --- |
| `before`, `after`, `adjacent_before`, `adjacent_after` | Logical source; no producing step. Order agrees with context and is acyclic. Adjacency prohibits intervening realized positions. |
| `connected` | Logical source; chemical bond order, with atom names only for residue endpoints. No producing step. |
| `mapped`, `copy` | Source and target; producing protocol step; matching levels. Copy permits one-to-many mapping. |
| `realized` | Logical source to referenced output subjects; matching levels; step and contiguous `target_ordinal_id` starting at one. |
| `generated`, `deleted` | Generated has only a target; deleted only a source; producing step required. |

Logical topology endpoints share context; a structural anchor shares a declared data-group context with its logical artifact. Chemical feasibility, valence and realized adjacency are interpreter checks. Mapping sources belong to protocol inputs and targets to outputs. Mapping rows do not carry topology-only bond/name fields. Count distinct realized identities against bounds; duplicates are invalid. Record zero realization by deletion. A site cannot be both realized and deleted in the same step. Copying, generation and deletion preserve artifact/instance identity without asserting geometric equality.

## Arrays

An `array` has exactly one owning value row. The owning definition supplies scalar element type, positive rank and transform. Row-major traversal, with the last axis fastest, is fixed by the specification. Missing element rows inherit the array's omission state, never numeric zero. Elements have one-based flat indices and explicit states where needed.

`axis` serves both shared declarations and instance dimensions. Exactly one of `definition_id`/`array_id` is present. Definition axes are contiguous from one through rank, with label kind, optional domain and fixed length, or `.` for a variable dimension. Unknown `?` is not a variable-dimension declaration. Array axes provide actual nonnegative lengths and inherit interpretation. A fixed length must agree; a variable dimension needs an array row. Fixed axes need no repeated per-array row.

`axis_label` references an axis ID and one-based index. Labelled axes have one unique label per position: explicit text, component identity, or exactly x/y/z for Cartesian. Fixed labels may be supplied once on the definition axis and cannot be overridden. Otherwise arrays provide their labels; variable definition axes have no fixed label list. Zero-length dimensions are allowed.

Geometric arrays have real elements and a final Cartesian axis of length three. Each triple is wholly finite/specified or wholly in one non-specified state. Point arrays use angstroms and rotate/translate; vectors rotate; invariant arrays do not transform. Other tensor laws or unsupported NumPy dtypes require an explicit supported mapping or rejection, not an opaque private encoding.

## Shared draft terms

These `proposal:` keys use version `draft-1` and omission state `unconstrained`; their meanings cannot be redefined locally. They are proposed terms, not already approved registry entries.

| Definition | Level/body/type | Meaning |
| --- | --- | --- |
| `proposal:coordinate` | Atom / 1 / point3, angstroms | Complete Cartesian target in the referenced frame. |
| `proposal:sequence_identity` | Residue / 1 / component, none | Exact requested identity, independent of observed identity. |
| `proposal:sequence_probability` | Residue / 1 / component-parameterized real, none | Partial probabilities over canonical-polymer-28. |

Canonical-polymer-28 is `ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL A C G U DA DC DG DT`. It is defined once here; no per-file alphabet/axis table is needed. Actually referenced components require `chem_comp` records. Other alphabets, including noncanonical components, use custom versioned definitions/domains.

Specified probabilities lie in [0,1] and sum to at most one; a complete distribution sums to one, with absolute tolerance 1e-6. Zero excludes a component. Unconstrained candidates share remaining mass without implicit uniformity or renormalization. Unknown values remain unresolved; inapplicable candidates receive no mass. Required execution resolves unknown states and supplies a valid distribution under its declared policy.

Exact identity fixes one-hot probabilities. Explicit probabilities must agree within tolerance; conflicts, including fixed identities outside the applicable domain, are errors. The reference sequence is not itself an identity condition. The compact example gives ALA=0.7 and GLY=0, leaving 0.3 for other unconstrained candidates.

Use existing ModelCIF distance restraints wherever their semantics fit, and existing QA/energy/experimental categories for results. The [coverage table](annotation-coverage.md) maps other source annotations through the same carriers. Shared profiles must define operational terms such as solvent accessibility, secondary structure, classification releases and interaction roles. Validation of the data contract does not certify custom calculations, chemical feasibility or production conditioning equivalence.
