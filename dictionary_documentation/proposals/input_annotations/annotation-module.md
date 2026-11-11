# Compact ModelCIF annotation module

Proposed component 0.1.0. The [DDL2 component](../../../base/mmcif_ma-annotation.dic) is the item/type/key reference; the rules below define conditional and scientific semantics that cannot all be expressed through DDL2. The module incorporates Annotated CIF into ModelCIF and supports custom definitions through the same fields.

## Construction

**Shared definition + annotation set + a row containing subject and value.** A frame is added for geometry. A definition supplies stable scientific identity/version, description, level, body order, value kind, units and omission behavior. A set supplies data/model context, authored/effective/derived stage, purpose and execution requirements. Unused optional columns need not appear.

| Level | Subject | Example |
| --- | --- | --- |
| Atom | `atom_site.id` in the set model | XYZ target |
| Residue | Joint asym/entity/polymer-sequence identity, or a logical site | Component or sequence probability |
| Chain | `struct_asym.id` in the set model | Chain label or chain-pair relation |
| Molecule | Explicit molecular group with definition/version | Molecular feature |
| Token | Explicit membership and tokenizer/version | Indexed status or shaped feature |
| System | Set/data context | Zero-body task label |

Body order counts operands: 0 for system, 1 for one subject, 2 for a pair. It is independent of atom count within a group or value shape. Pair operands occupy the same value row. Scalar and XYZ values have one canonical direct encoding; arrays add metadata only for other shaped values.

## Categories

Every name below has prefix `ma_annotation_`. Keys are unique within the data block. Individual item parents and composite asym/entity, entity/sequence and array/axis links are declared in DDL2.

| Categories | Role and key |
| --- | --- |
| `definition`, `domain` | Versioned scientific definitions and closed vocabularies; `id` |
| `domain_value` | Every member of a custom domain; `(domain_id, code)` |
| `set`, `frame` | Shared execution/data context and Cartesian placement; `id` |
| `atom`, `residue`, `chain`, `group_value`, `system`, `site_value`, `pair` | Compact value rows for the corresponding subjects; `id` |
| `default` | Uniform scalar default; `(set_id, definition_id)` |
| `group`, `group_member` | Explicit nested membership; `id` and `(group_id, ordinal_id)` |
| `site`, `site_link`, `subject` | Logical positions/topology and reusable pair/anchor/mapping identities; `id` |
| `correspondence` | Source/output mapping through a protocol step; `id` |
| `array`, `definition_axis`, `axis`, `axis_label`, `array_value` | Shaped values, dimensions, labels and elements; `id`, `(definition_id, axis_order)`, `(array_id, axis_order)`, `(array_id, axis_order, index)`, `(array_id, element_index)` |

## Definitions, values and scope

1. A `(definition_key, version)` identifies one scientific meaning. Use a namespaced key and a resolvable reference where available. Custom definitions must document operational meaning, units, domains and preparation method sufficiently for an independent implementation; importing executable code is not part of interpretation. Changing these semantics requires a new version/key. Shared draft terms are specified below; `example:` terms are illustrative, not a shared scientific registry.
2. A used definition must match the carrier's body order and level. Zero-body definitions use system; two-body definitions declare `symmetric` YES/NO. Both pair endpoints have that level. Heterogeneous raw selectors do not change the declared semantic level.
3. A specified value uses exactly one matching scalar slot (`value_boolean`, `value_integer`, `value_real`, `value_text`, `value_comp_id`), all three `x/y/z` plus a frame, an `array_id` (plus frame for geometric arrays), or a `value_group_id`. Integers are mathematical integers; reals must be finite. Booleans use YES/NO. A candidate `component_id` is a parameter, distinct from a component-valued payload and from the reference structure's identity.
4. `state` defaults to `specified` only when its column is absent. Explicit `?` or `.` is not that default. `unconstrained`, `unknown` and `not_applicable` have no payload and remain distinct. CIF null markers keep their ordinary unknown/inapplicable meanings in other fields. False and numeric zero are ordinary values unless the definition explicitly maps a historical inactive code to a state.
5. A definition is active in a set only when a value row or default uses it. For active definitions, omitted applicable values inherit `omitted_state`, except where a set-specific typed default applies. Explicit rows override that default, including explicit non-specified states. Defaults are uniform scalars, without component parameters; exact identities, geometry, groups and arrays are materialized. Structure-dependent default functions must become effective rows and recorded preprocessing provenance.
6. Scope is the set model for structural subjects, or the annotation data artifact and its declared logical sites/groups for coordinate-free tasks. Atom IDs reference actual atoms in that model. Polymer residues use consistent asym/entity/sequence identity, including unresolved residues; non-polymer subjects use explicit groups. Structural groups and reusable subjects identify the model's `ma_data` artifact; logical ones identify their own data artifact. An annotation set's data ID identifies the annotations, independently of the referenced model's data ID. Cross-file references require the relevant declarations in the exchange context and standard associated-file links, not bare array offsets or unqualified external IDs.
7. `(set, definition, subject(s), component parameter, context group)` is unique. Equivalent subject aliases count as the same identity; reversed endpoints duplicate a symmetric pair. Explicit context permits distinct partner-specific values. A context group must match the set's model, or its data artifact when coordinate-free. Consumers combine sets only under an explicit workflow/profile and check conflicts after that combination.
8. `required_for_execution` means the consumer must understand the definition, resolve required data and implement its conditions before execution. Preservation by a generic reader is insufficient. Unknown required values, unsupported semantics and conflicting effective conditions must be reported before execution. This flag does not assert that an output satisfies a condition.

Use units `none` for dimensionless/non-numeric values and `angstroms` for point coordinates. Other units require `units_details` describing their meaning/conversion, using existing dictionary unit names where applicable. Use a separately versioned scientific definition to change units or interpretation.

## Geometry, groups and logical topology

Points rotate and translate; vectors rotate only. A `model Cartesian` frame refers to the set model. An `independent rigid` frame has no model placement: its complete finite XYZ points retain their relative geometry while the frame can rotate/translate as a whole. Partial XYZ targets are not representable as complete points and must not be silently filled. Reserved legacy coordinate-group integers become explicit frame IDs/kinds and states. Group-local Cartesian coordinates do not mean internal bond-angle/torsion coordinates.

Groups declare data/model, kind, definition/version, order and explicit members. Each member selects exactly one atom, child group or logical site. Membership and enclosing-context references are acyclic; duplicate direct members are invalid. Token/molecule interpretation is determined by the named grouping method, not by array storage or chain labels. Ordered membership preserves its declared relative order; ordinals need not be contiguous.

An index group is ordered within an explicit enclosing context. Its members are tokens or logical token positions of length one; each has an integer offset. Expandable segments acquire token offsets after realization. Offsets increase uniquely in member order, may have arbitrary origin and must preserve known relative differences. Members belong to the enclosing context. Distances between separate index groups are unknown unless separately asserted. Slicing or assembly copying must remap all references and frames, or explicitly invalidate dependent annotations.

A logical position has realized length one. A segment has explicit nonnegative `min_length <= max_length`; zero permits deletion. Sites name an ordered, coordinate-free context that includes them. A site-value row on a segment applies the same value/state to each realized member; use separate positions or post-realization rows for differing member values. A pair with a segment endpoint applies to every realized endpoint combination. The definition determines whether any resulting self-relation is meaningful. `before`/`after` impose order; `adjacent_before`/`adjacent_after` additionally prohibit intervening realized positions. Logical order must be acyclic and agree with context order. Structural anchors must share a declared data-group context with the logical artifact. `connected` means a chemical bond with bond order; residue endpoints name atoms, atom endpoints do not repeat atom names. Chemical feasibility, valence and final adjacency are checked by an interpreter against the realized structure.

`correspondence` references the producing protocol step. Source data occur among its inputs and target data among its outputs. `mapped`, `copy` and `realized` require both endpoints; `generated` only a target; `deleted` only a source. Endpoint levels agree. `realized` maps logical sites to actual output subjects, allowing one-to-many segment realization. Realized rows supply contiguous target_ordinal_id values starting at one within each source site/protocol step, so segment order survives row shuffling. Duplicate realized identities are invalid. Count distinct realized identities, not alias IDs, against the length bounds; zero realization is recorded by deletion. A site cannot be both realized and deleted in one step. Correspondence does not itself assert geometric equality. Copies, inserted/generated subjects and deleted subjects must retain distinct artifact/instance identity.

## Arrays and custom domains

An array has exactly one owning annotation row. Its definition gives scalar element type, positive rank, transform rule and one `definition_axis` per dimension. A fixed axis length is an integer; `.` declares a variable dimension whose length is supplied by each array. Dimensions may be zero. Array axes are numbered contiguously from one, match the definition and record all dimension lengths. Flat element indices are one-based and row-major, with the last axis varying fastest. Sparse missing elements inherit the array's explicit omission state, never numeric zero.

Labelled axes give one unique label per index. Text labels are explicit strings; component labels reference `chem_comp`; a Cartesian axis is exactly x,y,z. Custom categorical/component domains list every member in `domain_value`, with unique component identities where applicable. Categorical scalar payloads use symbolic text codes, rather than undocumented integer enum values. Component parameters require an explicit complete component domain unless their shared definition fixes it.

Geometric arrays use real elements and a final Cartesian axis of length three. Each triple has one state: all specified with finite values, or all the same non-specified state. Point arrays use angstroms and translate/rotate; vector arrays rotate. Invariant arrays do not transform. A custom tensor with another transformation law must be mapped to these supported forms or rejected explicitly; arbitrary NumPy dtypes and executable transformation functions are not interchange semantics.

## Shared draft definitions

The `proposal:` namespace and `draft-1` version below are part of this proposed component, not already approved registry terms. Their metadata cannot be redefined locally.

| Definition | Level/body/type | Interpretation |
| --- | --- | --- |
| `proposal:coordinate` | Atom / 1 / point3, angstroms | Complete Cartesian target in the referenced frame; omission is unconstrained. |
| `proposal:sequence_identity` | Residue / 1 / component, none | Exact requested chemical component on a structural or logical residue; omission is unconstrained. It is independent of observed reference identity. |
| `proposal:sequence_probability` | Residue / 1 / component-parameterized real, none | Partial probabilities over canonical-polymer-28 below; omission is unconstrained. |

The fixed canonical-polymer-28 domain is `ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL A C G U DA DC DG DT`. It is defined once here; files need not repeat 28 domain or axis rows. Each actually referenced component requires its `chem_comp` declaration. Another alphabet, including noncanonical components, uses a separately versioned custom definition with an explicit domain.

Each specified probability is in [0,1]. Specified probabilities sum to at most one, and a fully specified distribution sums to one (absolute numerical tolerance 1e-6). Zero explicitly excludes that component. Unconstrained candidates may share the remaining mass without an implicit uniform distribution or renormalization. Unknown values remain unresolved; inapplicable candidates cannot receive mass. Required execution must resolve unknown applicability/value states and produce a valid distribution under its declared model policy.

An exact identity fixes a one-hot distribution. Coexisting explicitly specified probabilities must agree with it (same tolerance); conflicting values are errors, not silently overridden. A fixed identity outside the probability domain is also a conflict. The reference sequence is not an exact-identity condition. In the compact example, ALA=0.7 and GLY=0 leave 0.3 for other unconstrained candidates; no identity condition is present.

## Existing restraints and scientific profiles

Use existing ModelCIF distance restraints where their endpoint, unit and bound semantics fit. Use protocol/data associations to establish their condition role. Do not duplicate an authoritative distance in a custom annotation. Existing QA, energy and experimental categories keep their meanings.

Other source annotations are representable through custom versioned definitions and domains, as detailed in [API coverage](annotation-coverage.md). An interoperable profile must supply operational definitions for terms such as solvent accessibility, secondary structure, CATH classifications and interaction roles; integer storage codes alone are insufficient. Shared registry adoption of those definitions is a separate scientific review, not a limitation of the generic carrier schema. The validators check structural and stated shared-term rules; they do not certify arbitrary custom scientific calculations or production conditioning equivalence.
