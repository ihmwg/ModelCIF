# AtomWorks and RFD4 ModelCIF compatibility plan

Two claims must be tested separately: (1) producing a valid ModelCIF model record and (2) preserving the scientific meaning of a declared input-annotation exchange profile. A generic CIF parser or an unchanged filename is insufficient evidence for either.

## AtomWorks responsibilities

- Add an explicit ModelCIF import/export layer around the existing array representation. Retain model/entity/software/protocol/data/feature/associated-file metadata in a structured companion object. `keep_cif_block` or extra-category hooks are useful building blocks, but retaining raw categories after an edit can leave invalid references.
- Build mappings from original atom_site IDs and label residue/entity identifiers to arrays before filtering, assembly generation, cropping or renumbering. Rebuild references from the final emitted IDs on export. Preserve one-to-many assembly correspondence and report unrepresentable removals. Do not write idx0/idx1 as cross-file identity.
- Collapse atom-broadcast residue annotations only after consistency checks. Handle model scope, alternate locations and chains/entity instances explicitly. Reuse ModelCIF features; token and molecule groups require membership and context, not only a label.
- Produce complete model/entity/chemistry metadata and parent links for the declared output profile, including multi-model cases. The inspected writer creates a fresh CIF block, accepts extra_categories, and writes entity categories only on its single-structure path. It also emits implementation-specific entry/atom fields; a strict standard export must filter, map or separately declare those fields.
- Reuse the existing Biotite CIF/BinaryCIF path if helpful; python-modelcif can supply ModelCIF authoring semantics. Neither is a required replacement for AtomWorks internals. Extend python-modelcif readers/dumpers for accepted new categories or maintain a tested temporary adapter before upstream support.

## RFD4 responsibilities

- Capture authored task inputs and effective conditions after default generation and consistency transforms as distinct data artifacts linked by protocol steps. FinalizeSequenceConditioning can imply sequence identities from token type, atomization or non-backbone coordinate constraints. Report this information in benchmark inputs.
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

## Tooling and release distinction

The ModelCIF repository distributes a combined dictionary (dist/mmcif_ma.dic) and extension-only dictionary (dist/mmcif_ma_ext.dic). Pin the chosen assembly; do not combine independently latest parent and extension versions without validation. python-modelcif supplies authoring/reading infrastructure, while the ModelArchive converter/validator ecosystem supplies conversion and CifCheck-based validation. Tool support for a newly accepted category requires its own implementation work. Generic unknown-category retention and semantic support are different capabilities.

The draft PR supplies a candidate data model and bounded checks, not production AtomWorks/RFD4 adapters. The broader manifests and mapping profiles still need their own scientific/schema review. No code changes to AtomWorks or RFD4 are claimed by this proposal.

## Evidence

AtomWorks a0c63a8f77e76aba93857f444d02092354972c45: src/atomworks/io/utils/standard_annotations/{base,serialization}.py; src/atomworks/io/utils/io_utils.py; src/atomworks/ml/conditions/{base,definitions}.py.
RFD4-Proteina 68058693cb88762a8aaf806571e13b291ce6318a: src/rfproteina/conditions.py; src/rfproteina/transforms/{sequence_conditioning,internal_coords}.py; src/rfproteina/utils/{parse_presets,standard_annotations}.py.
The findings are scoped source inspection; runtime compatibility tests are implementation gates rather than completed evidence.
