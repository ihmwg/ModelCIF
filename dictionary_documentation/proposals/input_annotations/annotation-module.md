# A unified ModelCIF annotation module

**Design proposal for working-group review, not a released dictionary.** This document defines the intended scope of the proposal. The existing five-category DDL2 component and its 25 checks exercise a small subset; they do not implement the module described here.

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

Whole-API support requires both schema expressiveness and tested mappings. The accompanying coverage matrix assigns all 59 inventoried entries to a target representation and records unresolved semantics. It is a scoped inventory, not proof that every plugin or registry entry has been enumerated.

## Proposed dictionary structure

The names below are provisional. Exact category boundaries and reuse of existing categories require working-group review. The important commitments are the relationships and complete coverage, not a fixed number of tables. General `ma_annotation_*` naming is preferable to `ma_input_annotation_*` because provenance and reference geometry also occur on intermediate and output data.

1. **Definitions and domains.** A proposed `ma_annotation_definition` describes a stable definition reference/version, name, semantic level, body order, scalar type, units, pair symmetry, transformation rule and default policy. Associated domain and axis records describe categorical meanings and shaped values. These records carry declarative data, never executable default functions. Shared scientific terms are published and versioned with ModelCIF guidance; custom terms use the same representation with a distinct namespace.
2. **Annotation sets and assignments.** A proposed `ma_annotation_set` links to `ma_data.id` and identifies authored, effective or derived data. `ma_annotation` identifies a definition, its set, purpose, state and whether interpretation is required for execution. A separate ordered operand relation links each assignment to its subjects. Zero-body values have no local operands. Sets are linked to producing/consuming steps through existing data groups and protocols.
3. **Subjects and membership.** A proposed `ma_annotation_subject` gives a subject its semantic level and context, with a reference to an existing ModelCIF feature when it has structural support. Reuse `ma_atom_feature`, `ma_poly_residue_feature` and `ma_entity_instance_feature`. Their `feature_type` describes the selection representation; it need not become a second enumeration of semantic levels. A token can select several atoms while remaining one token operand. Molecules/tokens require a grouping definition/version and explicit membership; ordered membership needs explicit positions. Chain instances must remain distinct across assembly copies. Proposed membership records supplement existing feature selections only where order or nesting is needed.
4. **Values and axes.** Proposed typed value records store scalars or elements of declared shapes. Use explicit element indices/axis labels and per-element state. Do not hide ordinary annotations in JSON strings, dynamically invented dictionary item names or uninterpretable binary blobs. A sequence probability is keyed by chemical component, not a private channel number. Sparse scalar pairs and sparse array elements need distinct omission rules. Scalar versus shaped value is independent of body order. CIF and BinaryCIF encode the same logical records; measure layout and compression before selecting a default implementation.
5. **Frames.** Proposed frame records preserve model placement or independent rigid placement. Point targets transform by rotation and translation; direction/displacement vectors rotate without translation. An annotation definition specifies which rule applies. Reuse existing transformation categories where their meaning and parent references fit. RFD4 group-local coordinates remain Cartesian points. Frame/group renaming is not a change of geometry; membership changes require revalidation.
6. **Design sites and relations.** Add typed logical position/segment records for subjects that do not yet have coordinates or fixed length. Link to entity/sequence records when available; do not create fake atom_site rows. Relations describe order, chain/molecule context, known relative offsets, segment bounds and anchors. A realization protocol produces concrete residues/atoms and correspondence. These are in scope for the full design module; isolated coordinate-free task documents also require an explicit ModelCIF application profile and validation review.
7. **Correspondence.** Add or reuse a structured relation between data-scoped source and destination subjects, including generated/deleted subjects and one-to-many assembly copies. Reference the responsible protocol step and exact artifact identity. Source strings such as a contig label may remain descriptive but cannot be the only global key. Unrecognized metadata must be remapped or explicitly invalidated after structural edits.

This design does not require a new category for every annotation class. It requires a reusable data model plus scientifically defined terms. Conversely, values already represented faithfully by ModelCIF restraints, QA, energy or experimental-validation categories should use those categories with an unambiguous API mapping, rather than acquire a competing copy.

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

## Changes needed in the current draft

- Broaden definition scope beyond four feature types and the four illustrated terms; retain all six API levels with explicit membership.
- Separate semantic subject level from ModelCIF feature selection type. Cover coordinate-free/future subjects through logical design-site records.
- Replace the scalar/coordinate-only value design with typed shape/axis support and element states. Keep frame semantics explicit rather than treating every shape-(3) array as a point.
- Cover output reference geometry and provenance; prefer a general annotation namespace while continuing to reuse existing results categories.
- Include index offsets, variable segments and correspondence in the agreed module scope, not as permanent private escape hatches.
- Supply a complete built-in term crosswalk and publish unresolved scientific choices. Model-specific interaction defaults and ambiguous centroid definitions need clarification, not merely storage as integers.
- Treat the existing five-category component as partial implementation evidence. Its checks must not be presented as validation of this broader design.

## Implementation and acceptance

Agree the full architecture and coverage matrix before choosing the first implementation slice. Land dictionary changes and reference implementations in reviewable stages within that architecture. Staging is an implementation sequence, not a division into permanent file standards.

AtomWorks should expose ModelCIF-aware parsing/writing through its normal I/O APIs, keep StandardAnnotation/AtomArrayPlus and add definition mappings, subject identity and metadata lifecycle. RFD4 should retain ConditionBase and conditioning transforms, register its scientific vocabulary, and save authored/effective/derived annotation sets and protocol provenance. A versioned migration converter may replace historical fields, sentinels and layout; a permanent legacy reader or dual writer is not required. Accepted ModelCIF output becomes the canonical path once the declared coverage passes validation. Preserving the effective model inputs should avoid checkpoint conversion or retraining; verify this with equivalent conditioned inputs before claiming migration equivalence.

Migration must preserve task meaning rather than old bytes. Converted dataset releases receive new versions and checksums, retain source-to-output provenance, and update dependent manifests; ambiguous old defaults or source labels must be reported instead of invented. Changes to Python names or helpers are acceptable where they make the standardized semantics clearer, while retaining useful array operations.

Acceptance covers all inventoried terms plus fixtures for all API levels, shaped values, custom definitions and sparse pairs; exact state/default semantics; roundtrips and supported structural edits; and independent implementation tests. Full dictionary assembly and CIF/BinaryCIF validation remain required. A complete generic module does not assert that every model supports every condition. Each execution implementation publishes its support set and fails before silently altering an unsupported task.

The three demonstrations remain pipeline preservation, controlled cross-tool benchmarking and exchange of prepared datasets. Benchmark inputs must contain only permitted information after preparation, and all scheduled attempts remain in accounting. ModelCIF-associated large-data resources are acceptable when their shape, axes, provenance and interpretation are defined by the same standard; they must not be a mandatory private Annotated CIF fallback.

Request working-group agreement on this integrated scope, then review typed category additions, term definitions and representative files together with python-modelcif implementers and independent consumers. No existing ModelCIF categories or the protein-design additions from #31 need removal. Adoption, namespace assignment and release remain working-group decisions.
