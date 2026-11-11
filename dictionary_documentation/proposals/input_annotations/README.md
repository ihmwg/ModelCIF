# Incorporating Annotated CIF into ModelCIF

We propose a ModelCIF annotation module incorporating the data contract used by AtomWorks and RFD4-Proteina. It enables seamless tool pipelines, meaningful cross-tool benchmarking and exchangeable preprocessed datasets. Both libraries would implement one standardized representation through their normal annotation/I/O APIs. Older Annotated CIF files may be converted; their field names, layout and permanent backward compatibility are not requirements.

**Discussion proposal for ModelCIF Working Group review.** New `ma_annotation_*` names are provisional. This PR changes no released dictionary and removes no existing ModelCIF content.

## Scope and proposed addition

Standardize atom, residue, chain, molecule, token and system annotations; 0/1/2-body operands; typed scalar and shaped values; categorical domains, defaults and states; sparse relations; coordinate/index groups; logical design sites/expandable segments; and source-to-output correspondence. The standard describes data and scientific semantics, not executable Python methods. Required conditions must be interpreted before execution; unsupported required conditions must fail explicitly.

- [Module and item definitions](annotation-module.md): complete target scope, a concrete proposed layout for the worked annotations, keys/types/parents and interpretation rules.
- [Worked CIF](worked-annotations.cif): an illustrative workflow, existing selections and two rigid-point targets plus partial sequence probabilities. It is a parseable example fragment, not a complete deposition or a released schema.
- [API coverage](annotation-coverage.md): compact mappings for all 59 inventoried annotations, the generic API requirements and unresolved scientific choices.

## Relationship to issue #31 and the published standard

[Issue #31](https://github.com/ihmwg/ModelCIF/issues/31) proposed controlled-vocabulary changes and was [resolved in ModelCIF 1.4.8](https://github.com/ihmwg/ModelCIF/issues/31#issuecomment-3511891347). Those changes are present in the 1.4.9 dictionary used here. The exact published method name is **`structure validation`**; the issue text originally proposed `structural validation`.

| Existing item | Published values reused without change |
| --- | --- |
| `_ma_protocol_step.method_type` | `backbone generation`, `sequence design`, `structure validation` |
| `_ma_data.content_type` | `intermediate backbone`, `intermediate sequence`, and the broadened `input structure` meaning |

This proposal supplies annotation data consumed by those steps. It uses `ma_data`/data groups/protocols and existing software/parameter records, atom/residue/entity-instance features, and applicable spatial restraints. Quality assessments, energies and experimental results remain in their existing categories. In the example, annotation data use the existing `other` content type with explicit details; a dedicated content-type value can be considered during review.

Unlike the vocabulary-only change in #31, this addition needs category descriptions, item types/keys/parents, scientific rules and example CIF records. The item descriptions follow the style of [category proposal #29](https://github.com/ihmwg/ModelCIF/issues/29), with a concrete example alongside the full intended scope.

## Integration and exchange requirements

AtomWorks can retain its registry, StandardAnnotation/AtomArrayPlus APIs and efficient arrays while implementing canonical ModelCIF I/O and metadata lifecycle. RFD4 can retain ConditionBase and model conditioning while recording authored and effective inputs, inferred conditions, derived reference values and provenance. A versioned converter may rewrite older files; converted datasets require updated versions/checksums and dependent manifests. Equivalent effective inputs must be verified.

Interchange requires stable subject references and remapping or explicit invalidation after structural edits, including assembly copies, insertions and deletions. Default/false/zero/unknown semantics must be defined per annotation. Shared scientific definitions and namespaced custom terms use the same representation; retaining a custom term does not establish execution support.

Prepared-data profiles specify source/CCD versions, recipes, licenses, examples, splits, checksums and relevant token/tensor axes. Benchmark profiles specify permitted effective inputs, budgets, evaluator settings and all-attempt accounting. A mask alone does not conceal identity or coordinates still present in a supplied structure. Large associated resources must have standard-defined interpretation, rather than a mandatory private annotation payload. Investigation-level metadata should be coordinated with the existing ModelCIF discussion.

The complete architecture and coverage should be agreed before implementation is staged. The concrete records here illustrate two annotation families; additional domain, topology, grouping and correspondence items remain in scope and require item-level completion. Full DDL2 assembly, production readers/writers, CIF/BinaryCIF performance and independent interoperability tests follow that design work. No full-module conformance or working-group acceptance is claimed.

## Standards references

- [Published dictionary and release history](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/)
- [Published protocol method values](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.method_type.html)
- [ModelCIF usage guide](https://github.com/ihmwg/ModelCIF/blob/fece26d1cbeba07866fbbb5becad057c49d40805/dictionary_documentation/documentation.md)
- [Tauriello et al., ModelCIF Update (2026)](https://doi.org/10.1016/j.jmb.2026.169658)
