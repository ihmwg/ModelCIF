# AtomWorks and RFD4 ModelCIF compatibility plan

Two claims must be tested separately: (1) producing a valid ModelCIF model record and (2) preserving the scientific meaning of a declared input-annotation exchange profile. A generic CIF parser or an unchanged filename is insufficient evidence for either.

Keep StandardAnnotation, ConditionBase and native annotated CIF/BinaryCIF as supported interfaces. Implement the ModelCIF mapping as an optional adapter with declared coverage; no checkpoint conversion, retraining or model architecture change is implied. Native legacy aliases and positional fields remain reader compatibility concerns. Do not bulk-rewrite prepared datasets before the adapter has passed representative round trips.

## AtomWorks responsibilities

- Add an explicit ModelCIF import/export layer around the existing array representation. Retain model/entity/software/protocol/data/feature/associated-file metadata in a structured companion object. `keep_cif_block` or extra-category hooks are useful building blocks, but retaining raw categories after an edit can leave invalid references.
- Build mappings from original atom_site IDs and label residue/entity identifiers to arrays before filtering, assembly generation, cropping or renumbering. Rebuild references from the final emitted IDs on export. Preserve one-to-many assembly correspondence and report unrepresentable removals. Do not write idx0/idx1 as cross-file identity.
- Reuse the current loader's remapping through unique atom_array_index after filtering. Its removal of annotation rows for removed atoms needs an explicit execution-profile loss policy: disappearing required task subjects cannot silently change the task. This local index remap does not supply cross-artifact identity or assembly-copy lineage.
- Collapse atom-broadcast residue annotations only after consistency checks. Handle model scope, alternate locations and chains/entity instances explicitly. Reuse ModelCIF features; token and molecule groups require membership and context, not only a label.
- Produce complete model/entity/chemistry metadata and parent links for the declared output profile, including multi-model cases. The inspected writer creates a fresh CIF block, accepts extra_categories, and writes entity categories only on its single-structure path. It also emits implementation-specific entry/atom fields; a strict standard export must filter, map or separately declare those fields.
- Reuse the existing Biotite CIF/BinaryCIF path if helpful; python-modelcif can supply ModelCIF authoring semantics. Neither is a required replacement for AtomWorks internals. Extend python-modelcif readers/dumpers for accepted new categories or maintain a tested temporary adapter before upstream support.
- Provide a strict exchange-reader mode. The existing native loader can warn and skip malformed non-system categories; required exchange inputs must fail before execution. Preserve optional unknown content only while references remain valid; after edits, remap it using declared semantics or report invalidation. If native and projected values coexist, specify the authoritative representation and reject conflicts.

## RFD4 responsibilities

- Capture authored task inputs and effective conditions after default generation and consistency transforms as distinct data artifacts linked by protocol steps. FinalizeSequenceConditioning can imply sequence identities from token type, atomization or non-backbone coordinate constraints. Report this information in benchmark inputs.
- Enforce permitted information in the data actually supplied to the consumer. Disabling a conditioning mask does not hide the source identity or coordinates still present in atom_site. Build and validate the benchmark input projection rather than assuming all tools ignore unconditioned fields.
- Translate C_SEQ `<M>` and coordinate NaN into explicit state. Hotspot false is no hotspot conditioning, not an explicit negative interaction; probability zero excludes an identity while NaN leaves it unspecified. C_IDX defaults to true. Map each condition independently and record materialized defaults.
- Export absolute targets and independent rigid groups with their saved group-local Cartesian targets. C_CRDGRP is membership authority; whole-group renaming may preserve targets, while membership changes require revalidation. Reserved -1/0 group IDs and the int16 implementation limit are not standard semantics. Record any materialization from live coordinates.
- Keep exact component identity and custom chemistry; the current annotation preset permits custom ligands that reuse CCD codes. A standards adapter must detect such conflicts and provide unambiguous component definitions/identifiers rather than silently treating them as canonical CCD chemistry.
- Define portable index-offset relations and future topology before claiming support for unindexed motifs or expandable segments. Include external component identities and partial probability semantics before claiming sequence-probability interchange. Interaction labels need explicit partners/context and operational definitions independent of training sampling recipes.
- Export protocol steps, software/checkpoint hashes, configuration, seed, effective budgets and selected models. Retain source-to-output correspondence for unindexed insertions and motif targets. Reuse ma_qa_metric* for applicable results, ma_energy_estimates* for energies, and ma_experimental_validation for experimental evidence.
- Save sufficient evidence for independent evaluation. Keep generation/evaluation failures and unsupported tasks in attempt accounting. Missing inference context must not become zero violations; record not_evaluated. A prepared-dataset manifest separates deterministic preparation from sample-time crops/rotations/tensors.

## Incremental implementation gates

1. Valid existing ModelCIF outputs: a single protein, a ligand/custom-component complex and a multi-model output; parent links and chemistry pass independent validation. No new annotation claim required yet.
2. Direct input subset: exact sequence, absolute coordinates and rigid-group coordinates, round-tripped through two implementations; verify reordered atoms, renamed groups and transformed frames preserve intent. Unsupported required types fail before execution.
3. Transformation coverage: assembly expansion, cropping, residue/atom insertion/deletion and indexing changes have explicit mappings or declared unsupported behavior. Test legacy alias conflicts, defaults, false/zero states and implied sequence conditions.
4. Three use-case demonstrations: two tools consume the same prepared example; a multi-tool pipeline preserves task intent; an independent evaluator reproduces scores and all-attempt denominators. Declare the supported annotation subset and pinned dictionary/profile versions.
5. Upstream dictionary and python-modelcif support: complete dictionary assembly/DDL2 validation, CIF and BinaryCIF tests, documentation and release coordination. Only then claim the corresponding full exchange profile.

The first annotation gate covers existing polymer residue identity and atom coordinate targets, including independent rigid groups. It does not cover all current RFD4 conditions. Keep token/molecule membership, index-offset relations, noncanonical/probability vocabularies, interaction partners and variable-length topology visible in the coverage report. Do not fabricate structural models for coordinate-free tasks. Scope task identity by the task artifact/data, and use model references only for subjects that belong to an actual structural model.

## Performance acceptance

Compare native CIF, native BinaryCIF and the proposed mapping on identical annotation content: file bytes, parse/write time, peak memory and rows. The point-target pilot requires assignment and payload rows and may require new feature rows; this can amplify a per-atom field considerably. Reuse feature definitions across compatible annotations, preserve sparse relations, and keep model-specific tensors in associated artifacts where appropriate. Do not infer runtime or compressed-size performance from row counts alone. A production default should wait for measured results.

## Tooling and release distinction

The ModelCIF repository distributes a combined dictionary (dist/mmcif_ma.dic) and extension-only dictionary (dist/mmcif_ma_ext.dic). Pin the chosen assembly; do not combine independently latest parent and extension versions without validation. python-modelcif supplies authoring/reading infrastructure, while the ModelArchive converter/validator ecosystem supplies conversion and CifCheck-based validation. Tool support for a newly accepted category requires its own implementation work. Generic unknown-category retention and semantic support are different capabilities.

The draft PR supplies a candidate data model and bounded checks, not production AtomWorks/RFD4 adapters. The broader manifests and mapping profiles still need their own scientific/schema review. No code changes to AtomWorks or RFD4 are claimed by this proposal.

## Evidence

AtomWorks d922a471381dd0f8bccaf78c384a6b56b6f8e391 (local re-review; initial inventory used a0c63a8f77e76aba93857f444d02092354972c45): src/atomworks/io/utils/standard_annotations/{base,serialization}.py; src/atomworks/io/utils/io_utils.py; src/atomworks/io/parser.py; src/atomworks/ml/conditions/{base,definitions}.py. The current pyproject.toml, rather than older contributor text, specifies Python >=3.12 and Biotite 2.0.0; pin the actual release dependency set for adapter tests.
RFD4-Proteina 68058693cb88762a8aaf806571e13b291ce6318a: src/rfproteina/conditions.py; src/rfproteina/transforms/{sequence_conditioning,internal_coords}.py; src/rfproteina/utils/{parse_presets,standard_annotations}.py.
The findings are scoped source inspection; runtime compatibility tests are implementation gates rather than completed evidence.
