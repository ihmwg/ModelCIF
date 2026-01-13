# How to use the ModelCIF dictionary

## Introduction

Computed structure models (CSM) are obtained through computational methods without using experimental data generated for the model.
[ModelCIF](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/) is a data standard designed for the FAIR archiving and storage of CSMs. As extension of the [PDBx/mmCIF format](https://mmcif.wwpdb.org/), it captures not only atomic coordinates, but also metadata and validation results, ensuring reproducibility and facilitating data exchange and reuse.

## PDBx/mmCIF format

PDBx/mmCIF has been the standard format of the [PDB archive](https://www.wwpdb.org/) since 2014. It consists of categories of information represented as tables and key-value pairs.
These categories contain data items that are precisely defined in a dictionary. Data items have explicit data types that define allowed values, and they can have explicit parent/child relationships with one another to link categories.
ModelCIF extends PDBx/mmCIF by defining a dictionary that adds categories and items to capture data specific to CSMs.

The resulting data format is based on the CIF (Crystallographic Information Framework) standard and is typically stored as a human-readable file or as a binary file in the [BinaryCIF format](https://github.com/molstar/BinaryCIF).

The following is an abbreviated example of parts of a PDBx/mmCIF file that define a software tool connected to a citation:

    _software.pdbx_ordinal   1
    _software.name           AlphaFold-Multimer
    _software.classification 'model building'
    _software.citation_id    1
    # ... abbreviated ...
    _citation.id     1
    _citation.year   2021
    _citation.title  'Protein complex prediction with AlphaFold-Multimer.'
    # ... abbreviated ...
    loop_
    _citation_author.citation_id
    _citation_author.name
    _citation_author.ordinal
    1 'Evans, R.' 1
    1 "O'Neill, M." 2
    # ... abbreviated ...

The example above showcases a number of properties of PDBx/mmCIF files:

- The [`software`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/software.html) and [`citation`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/citation.html) categories are provided as key-value pairs.
- The [`citation_author`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/citation_author.html) category uses the `loop_` keyword to define a table with multiple data rows (here two of them are shown).
- The [`_citation_author.citation_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_citation_author.citation_id.html) and [`_software.citation_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_software.citation_id.html) data items have [`_citation.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_citation.id.html) as parent item which connects the 3 categories.
- The data types for the data items are defined in the dictionary. For instance, [`_software.pdbx_ordinal`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_software.pdbx_ordinal.html) must be an integer and [`_software.classification`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Items/_software.classification.html) has a restricted list of allowed values.
- The [`software`](https://mmcif.wwpdb.org/dictionaries/mmcif_pdbx_v50.dic/Categories/software.html) category lists `_software.pdbx_ordinal` as the key data item, which must be provided as a unique value. It also lists `_software.name` and `_software.classification` as mandatory items.
- Quoting of text follows [CIF rules](https://www.iucr.org/resources/cif/spec/version1.1) (e.g. 'Evans, R.' and "O'Neill, M."). These rules also define how data rows in `loop_` structures can span multiple rows, how multi-line strings are defined using the ';' character, how to add comments in lines starting with '#', and how to define inapplicable or unknown data using the special values of '.' and '?', respectively. Generally, only ASCII characters are allowed in CIF files.

In short, an mmCIF file is valid if it contains:

- all mandatory categories for a given dictionary
- all mandatory items for the provided categories
- valid data according to the data types defined in the dictionary
- all categories required to include parent data items for all data provided


## ModelCIF format

A ModelCIF file is a valid PDBx/mmCIF file complemented by additional data describing how the model was generated and validation criteria to facilitate reuse of the model.
The core of ModelCIF consists of one or more modeling protocol steps.
These steps are described in free text and link input and output data with the software used.

### Minimal example

To demonstrate the application of ModelCIF, we modify a valid PDBx/mmCIF file.
For simplicity, we assume that the file includes:

- a single set of model coordinates stored in the [`atom_site`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_site.html) category (with `_atom_site.pdbx_PDB_model_num` = 1)
- a single molecular entity stored in the [`entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity.html) category (with `_entity.id` = 1) which defines the modeled protein
- a single instance of that entity (i.e. a polymer chain to model a monomer) stored in the [`struct_asym`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_asym.html) category (with `_struct_asym.id` = A)
- all PDBx/mmCIF categories to make this a valid PDBx/mmCIF file (here these are the [`atom_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_type.html), [`chem_comp`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/chem_comp.html), [`entity_poly_seq`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_poly_seq.html), [`entity_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_poly.html) and [`pdbx_poly_seq_scheme`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_poly_seq_scheme.html) categories)

We can now describe a modeling procedure using AlphaFold with the following addition to the mmCIF file to turn this into a valid ModelCIF file:

    _citation.id             1
    _citation.title          'Highly accurate protein structure prediction with AlphaFold.'
    _citation.journal_abbrev Nature
    _citation.journal_volume 596
    _citation.page_first     583
    _citation.page_last      589
    _citation.year           2021
    _citation.pdbx_database_id_PubMed 34265844
    _citation.pdbx_database_id_DOI    10.1038/s41586-021-03819-2

    loop_
    _citation_author.citation_id
    _citation_author.name
    _citation_author.ordinal
    1 'Jumper, J.' 1
    1 'Evans, R.' 2
    # ... abbreviated ...

    _software.pdbx_ordinal   1
    _software.name           AlphaFold
    _software.classification 'model building'
    _software.description    'Structure prediction'
    _software.version        2.2.0
    _software.type           package
    _software.location       https://github.com/deepmind/alphafold
    _software.citation_id    1

    loop_
    _ma_software_parameter.parameter_id
    _ma_software_parameter.group_id
    _ma_software_parameter.data_type
    _ma_software_parameter.name
    _ma_software_parameter.value
    _ma_software_parameter.description
    1 1 string model_preset monomer .
    2 1 string db_preset reduced_dbs .
    3 1 string max_template_date 2022-08-04 .
    4 1 boolean run_relax NO .

    _ma_software_group.ordinal_id         1
    _ma_software_group.group_id           1
    _ma_software_group.software_id        1
    _ma_software_group.parameter_group_id 1

    _ma_target_entity.entity_id 1
    _ma_target_entity.data_id   1
    _ma_target_entity.origin    designed

    _ma_target_entity_instance.asym_id   A
    _ma_target_entity_instance.entity_id 1

    _ma_model_list.ordinal_id 1
    _ma_model_list.data_id    2
    _ma_model_list.model_type "Ab initio model"

    loop_
    _ma_data.id
    _ma_data.content_type
    _ma_data.name
    1 target              "Modeling target"
    2 "model coordinates" "Top ranked model"

    loop_
    _ma_data_group.ordinal_id
    _ma_data_group.group_id
    _ma_data_group.data_id
    1 1 1
    2 2 2

    _ma_protocol_step.ordinal_id  1
    _ma_protocol_step.protocol_id 1
    _ma_protocol_step.step_id     1
    _ma_protocol_step.method_type modeling
    _ma_protocol_step.details     "Model generated using AlphaFold (v2.2.0) producing 5 monomer models with 3 recycles each, without model relaxation, using templates (up to Aug. 4 2022), ranked by pLDDT, starting from an MSA with reduced_dbs setting."
    _ma_protocol_step.software_group_id    1
    _ma_protocol_step.input_data_group_id  1
    _ma_protocol_step.output_data_group_id 2

- The [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category describes the modeling steps performed. Here we followed the simplest possible approach of a single step with relevant details described in free text.
- Each protocol step can be connected to groups of software using the [`_ma_protocol_step.software_group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.software_group_id.html) item. This is connected to the [`ma_software_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_software_group.html) category where each software group (identified by [`_ma_software_group.group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_software_group.group_id.html)) consists of software listed in the [`software`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/software.html) category ([`_ma_software_group.software_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_software_group.software_id.html) connected to [`_software.pdbx_ordinal`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_software.pdbx_ordinal.html)).
- Parameters used for each software tool within a software group can be defined in the [`ma_software_parameter`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_software_parameter.html) category (with [`_ma_software_parameter.group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_software_parameter.group_id.html) connected to [`_ma_software_group.parameter_group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_software_group.parameter_group_id.html)).
- Each protocol step can be connected to input and output data using the [`_ma_protocol_step.input_data_group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.input_data_group_id.html) and [`_ma_protocol_step.output_data_group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.output_data_group_id.html) items respectively. These are connected to the [`ma_data_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data_group.html) category where each data group (identified by [`_ma_data_group.group_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data_group.group_id.html)) consists of data listed in the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category ([`_ma_data_group.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data_group.data_id.html) connected to [`_ma_data.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.id.html)).
- Different types of modeling data can be defined and distinguished using the [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) item.
- Data of type "model coordinates" is further defined in the [`ma_model_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_list.html) category ([`_ma_model_list.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_model_list.data_id.html) connected to [`_ma_data.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.id.html)). This links it to the model coordinates in the [`atom_site`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_site.html) category ([`_ma_model_list.ordinal_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_model_list.ordinal_id.html) connected to [`_atom_site.pdbx_PDB_model_num`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_atom_site.pdbx_PDB_model_num.html)).
- Different types of models are distinguished using the [`_ma_model_list.model_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_model_list.model_type.html) item. If the main input for generating the CSM are template structures aligned to the modeling target, we label it as "Homology model" and otherwise as "Ab initio model" or "Other" (with details provided in the [`_ma_model_list.model_type_other_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_model_list.model_type_other_details.html) item).
- Data of type "target" is further defined in the [`ma_target_entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_entity.html) category ([`_ma_target_entity.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_target_entity.data_id.html) connected to [`_ma_data.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.id.html)). This links it to the molecular entities in the [`entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity.html) category ([`_ma_target_entity.entity_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_target_entity.entity_id.html) connected to [`_entity.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_entity.id.html)).
- The origin of a target entity ([`_ma_target_entity.origin`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_target_entity.origin.html)) is either labeled as "designed" as in this example or as "reference database" if there are cross-references to external databases (stored in the [`ma_target_ref_db_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_ref_db_details.html) and [`struct_ref`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref.html) categories).
- The modeled instances of the molecular entities are defined in the [`ma_target_entity_instance`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_entity_instance.html) category which links the model to the [`struct_asym`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_asym.html) category ([`_ma_target_entity_instance.asym_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_target_entity_instance.asym_id.html) connected to [`_struct_asym.id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_struct_asym.id.html)).

The modeling steps and provided data should allow an informed reader to recreate a qualitatively similar model and determine its suitability for specific downstream applications. The preferred level of detail varies significantly depending on the modeling method used. In all cases, a free-text description may suffice, but more granular descriptions are possible to enable programmatic access to certain details. The next sections describe several examples of additional data that can be stored in ModelCIF.


### Adding cross-references for target entities

The origin of the target entities is typically determined by cross-referencing external reference databases.
This makes the model easier to find and provides evidence of the modeled entity's existence.
ModelCIF uses existing PDBx/mmCIF categories to ensure compatibility with existing PDBx/mmCIF-based tools, while also adding a new category that allows for the inclusion of additional information.

Here, we show an example (adapted from [ma-kvko-prsa-005](https://modelarchive.org/doi/10.5452/ma-kvko-prsa-005)) for a modeled polymer entity based on a UniProtKB sequence (accession code Q8CVC6) that covers the residues 22-333 and differs from the original sequence at positions 236 and 279.
We also provide taxonomy information for the source organism and the exact version of the UniProtKB sequence, which is important since sequences can change for a given UniProtKB entry.
In ModelCIF this is captured by the [`ma_target_entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_entity.html), [`entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity.html), [`ma_target_ref_db_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_ref_db_details.html), [`struct_ref`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref.html), [`struct_ref_seq`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref_seq.html), [`struct_ref_seq_dif`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref_seq_dif.html), [`entity_src_nat`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_src_nat.html) categories as follows:

    loop_
    _ma_target_entity.entity_id
    _ma_target_entity.data_id
    _ma_target_entity.origin
    1 1 'reference database'

    loop_
    _entity.id
    _entity.type
    _entity.src_method
    _entity.pdbx_description
    _entity.formula_weight
    _entity.pdbx_number_of_molecules
    1 polymer nat 'Streptococcus mutans PrsA-IDR-NG variant' 39482.720 2

    loop_
    _entity_src_nat.entity_id
    _entity_src_nat.pdbx_src_id
    _entity_src_nat.pdbx_ncbi_taxonomy_id
    _entity_src_nat.pdbx_organism_scientific
    1 1 210007 'Streptococcus mutans serotype c (strain ATCC 700610 / UA159)'

    loop_
    _struct_ref.id
    _struct_ref.entity_id
    _struct_ref.db_name
    _struct_ref.db_code
    _struct_ref.pdbx_db_accession
    _struct_ref.pdbx_align_begin
    _struct_ref.pdbx_seq_one_letter_code
    1 1 UNP PRSA_STRMU Q8CVC6 22
    ;CSKTNQNSKIATMKGDTITVADFYNEVKNSTASKQAVLSLLVSKVFEKQYGDKVSDKEVTKAYNEAAKYY
    GDSFSSALASRGYTKEDYKKQIRSEKLIEYAVKEEAKKEITDASYKSAYKDYKPEVTAQVIQLDSEDKAK
    SVLEEAKADGADFAKIAKDNTKGDKTEYSFDSGSTNLPSQVLSAALNLDKDGVSDVIKASDSTTYKPVYY
    IVKITKKTDKNADWKAYKKRLKEIIVSQKLNDSNFRNAVIGKAFKKANVKIKDKAFSEILSQYAAASGSG
    SSGSTTTTTAASSAATTAADDQTTAAETTAAE
    ;

    loop_
    _struct_ref_seq.align_id
    _struct_ref_seq.ref_id
    _struct_ref_seq.seq_align_beg
    _struct_ref_seq.seq_align_end
    _struct_ref_seq.db_align_beg
    _struct_ref_seq.db_align_end
    1 1 1 312 22 333

    loop_
    _struct_ref_seq_dif.pdbx_ordinal
    _struct_ref_seq_dif.align_id
    _struct_ref_seq_dif.seq_num
    _struct_ref_seq_dif.db_mon_id
    _struct_ref_seq_dif.mon_id
    _struct_ref_seq_dif.details
    1 1 236 VAL ILE .
    2 1 279 SER ASN .

    loop_
    _ma_target_ref_db_details.target_entity_id
    _ma_target_ref_db_details.db_name
    _ma_target_ref_db_details.db_name_other_details
    _ma_target_ref_db_details.db_code
    _ma_target_ref_db_details.db_accession
    _ma_target_ref_db_details.seq_db_isoform
    _ma_target_ref_db_details.seq_db_align_begin
    _ma_target_ref_db_details.seq_db_align_end
    _ma_target_ref_db_details.ncbi_taxonomy_id
    _ma_target_ref_db_details.organism_scientific
    _ma_target_ref_db_details.seq_db_sequence_version_date
    _ma_target_ref_db_details.seq_db_sequence_checksum
    _ma_target_ref_db_details.is_primary
    1 UNP . PRSA_STRMU Q8CVC6 . 22 333 210007
    'Streptococcus mutans serotype c (strain ATCC 700610 / UA159)'
    2003-03-01 666CA84A5633C54E .


### Adding accompanying data

To keep data file sizes manageable and allow any type of data to be stored with models, ModelCIF provides metadata definitions that support the description of one or more associated files.
The associated files may contain large intermediate results, such as multiple sequence alignments (MSAs) or quality estimates for residue pairs.
A variety of generic file formats are permitted for these files and are captured in the [`ma_entry_associated_files`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_entry_associated_files.html) and [`ma_associated_archive_file_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_associated_archive_file_details.html) categories.

The following example is taken from ModelArchive where by convention all accompanying data is stored in a single ZIP file and large quality estimates such as AlphaFold's PAE matrices are stored in an accompanying file. For this entry ([ma-kvko-prsa-005](https://modelarchive.org/doi/10.5452/ma-kvko-prsa-005)) the MSA used for modeling was stored as an additional output and linked to the modeling protocol using the [`_ma_associated_archive_file_details.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_associated_archive_file_details.data_id.html) item. The result looks as follows:

    loop_
    _ma_entry_associated_files.id
    _ma_entry_associated_files.entry_id
    _ma_entry_associated_files.file_url
    _ma_entry_associated_files.file_type
    _ma_entry_associated_files.file_format
    _ma_entry_associated_files.file_content
    1 ma-kvko-prsa-005 https://modelarchive.org/api/projects/ma-kvko-prsa-005?type=materials_procedures__accompanying_data_file_name
    archive zip 'archive with multiple files'

    loop_
    _ma_associated_archive_file_details.id
    _ma_associated_archive_file_details.archive_file_id
    _ma_associated_archive_file_details.file_path
    _ma_associated_archive_file_details.file_format
    _ma_associated_archive_file_details.file_content
    _ma_associated_archive_file_details.description
    _ma_associated_archive_file_details.data_id
    1 1 ma-kvko-prsa-005_qa_metrics.cif cif 'QA metrics' 'Predicted aligned error' .
    2 1 ma-kvko-prsa-005.a3m a3m 'multiple sequence alignments' 'MSA for modelling' 9


### Adding data for archiving

Some data is useful to add especially for archival purposes. The following data is supported for depositions in [ModelArchive](https://modelarchive.org/):

- The [`_struct.title`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_struct.title.html) item to provide a name for the model deposition.
- The [`_struct.pdbx_model_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_struct.pdbx_model_details.html) item to provide a model description.
- The [`audit_author`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/audit_author.html) category to store the authors for the model.
- The [`_entity.pdbx_description`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_entity.pdbx_description.html) item to provide meaningful names to the molecular entities.
- Optional: the [`_entry.ma_collection_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_entry.ma_collection_id.html) item to group models as part of a model set.
- Optional: the primary citation in the [`citation`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/citation.html) category (i.e. with `_citation.id` = "primary") refers to the manuscript for which the model was generated.

For example, this is what it looks like in the model that was deposited as [`ma-nmpfamsdb-f000001`](https://modelarchive.org/doi/10.5452/ma-nmpfamsdb-f000001):

    _struct.title 'AlphaFold model for NMPFamsDB Family F000001'
    _struct.pdbx_model_details
    ;Model generated using AlphaFold (v2.0.0) for the "Representative Sequence" of NMPFamsDB Metagenome / Metatranscriptome Family F000001.

    The 5 produced models reached a max. global pLDDT of 72.708 and max. pTM of 0.371.

    See https://bib.fleming.gr/NMPFamsDB/family?id=F000001 for additional details.
    ;

    loop_
    _audit_author.name
    _audit_author.pdbx_ordinal
    'Pavlopoulos, Georgios A.' 1
    'Baltoumas, Fotis A.' 2
    # ... abbreviated ...

    loop_
    _entity.id
    _entity.type
    _entity.src_method
    _entity.pdbx_description
    1 polymer man 'Representative Sequence of NMPFamsDB Family F000001'

    _entry.ma_collection_id ma-nmpfamsdb

    loop_
    _citation.id
    _citation.title
    _citation.journal_abbrev
    _citation.journal_volume
    _citation.page_first
    _citation.page_last
    _citation.year
    _citation.pdbx_database_id_PubMed
    _citation.pdbx_database_id_DOI
    primary 'Unraveling the functional dark matter through global metagenomics.' Nature 622 594 602 2023 37821698 10.1038/s41586-023-06583-7
    2 'Highly accurate protein structure prediction with AlphaFold.' Nature 596 583 589 2021 34265844 10.1038/s41586-021-03819-2


### Adding estimates of model quality

Wherever possible, models from protein structure prediction methods must contain estimates of the expected accuracy of the structure prediction. These estimates are commonly referred to as "model quality" or "model confidence" and are important for determining whether a model can be used for downstream analysis.
These estimates should allow users to evaluate the accuracy of the prediction, both globally and locally.
These values predict the results of similarity metrics, such as the LDDT ([Mariani et al. 2013](https://pubmed.ncbi.nlm.nih.gov/23986568/)) or TM-score ([Zhang et al. 2004](https://pubmed.ncbi.nlm.nih.gov/31571280/)), if they were applied to compare the model with the coordinates of the correct protein structure.
However, these predictions are never perfectly accurate since the correct protein structure is unknown for most modeling results.

The accuracy of quality estimates has increased significantly over the years (see e.g. Fig. 4 in [Haas et al. 2019](https://pubmed.ncbi.nlm.nih.gov/31571280/)).
Estimation methods have developed in parallel with improved structure prediction methods.
Therefore, it is critical to use either a relatively recent, well-benchmarked standalone tool or service or quality estimates provided by the structure prediction method itself.
Note that, by historical convention, the main local quality estimates are often stored in place of B-factors in model coordinate files.
ModelCIF files can properly describe and store any number of quality estimates in the [`ma_qa_metric`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric.html) category and its connected categories.
For example, the following ModelCIF lines can represent the quality estimates available for AlphaFold 3 results:

    loop_
    _ma_qa_metric.id
    _ma_qa_metric.mode
    _ma_qa_metric.name
    _ma_qa_metric.software_group_id
    _ma_qa_metric.type
    _ma_qa_metric.type_other_details
    1 global pLDDT 1 'pLDDT to polymer' .
    2 local pLDDT 1 'pLDDT to polymer' .
    3 per-feature 'ipTM per chain' 1 ipTM .
    4 per-feature-pair 'ipTM per chain pair' 1 ipTM .
    5 per-feature-pair 'min. PAE per chain pair' 1 PAE .
    6 per-feature 'pTM per chain' 1 pTM .
    7 global 'fraction of prediction which is disordered' 1 'normalized score' .
    8 global 'significant number of clashing atoms?' 1 boolean .
    9 global ipTM 1 ipTM .
    10 global pTM 1 pTM .
    11 global 'ranking score' 1 other 'Combined score in range [-100, 1.5] (higher is better)'
    12 per-feature 'pLDDT per atom' 1 'pLDDT to polymer' .
    13 local-pairwise 'contact probability per token pair' 1 'contact probability' .
    14 local-pairwise 'PAE per token pair' 1 PAE .

The [`_ma_qa_metric.type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_qa_metric.type.html) item has a restricted list of allowed values that represent commonly used quality metrics.
This makes it possible to compare scores from different methods.
For example, many methods use a type of predicted LDDT score that is either directly comparable or only needs to be rescaled from a range of 0 to 1 to a range of 0 to 100.

The [`_ma_qa_metric.mode`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_qa_metric.mode.html) item distinguishes the granularity of the scores which are then listed in separate ModelCIF categories:

| `_ma_qa_metric.mode` | Category containing the scores |
|----------------------|--------------------------------|
| global | [`ma_qa_metric_global`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_global.html) |
| local | [`ma_qa_metric_local`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_local.html) |
| local-pairwise | [`ma_qa_metric_local_pairwise`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_local_pairwise.html) |
| per-feature | [`ma_qa_metric_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_feature.html) |
| per-feature-pair | [`ma_qa_metric_feature_pairwise`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_feature_pairwise.html) |
| dihedral | [`ma_qa_metric_dihedral`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_dihedral.html) |

For the example above (adapted from [ma-csp-msp2-255](https://modelarchive.org/doi/10.5452/ma-csp-msp2-255)), this is how some of the global and local scores would look like:

    loop_
    _ma_qa_metric_global.metric_id
    _ma_qa_metric_global.metric_value
    _ma_qa_metric_global.model_id
    _ma_qa_metric_global.ordinal_id
    1 85.02 1 1
    7 0.0 1 2
    8 0.0 1 3
    9 0.32 1 4
    10 0.61 1 5
    11 0.38 1 6

    loop_
    _ma_qa_metric_local.ordinal_id
    _ma_qa_metric_local.label_asym_id
    _ma_qa_metric_local.label_comp_id
    _ma_qa_metric_local.label_seq_id
    _ma_qa_metric_local.metric_id
    _ma_qa_metric_local.metric_value
    _ma_qa_metric_local.model_id
    1 A MET 1 2 32.55 1
    2 A GLY 2 2 56.67 1
    # ... abbreviated ...

    loop_
    _ma_qa_metric_feature.ordinal_id
    _ma_qa_metric_feature.model_id
    _ma_qa_metric_feature.feature_id
    _ma_qa_metric_feature.metric_id
    _ma_qa_metric_feature.metric_value
    1 1 4820 3 0.12
    2 1 4821 3 0.49
    3 1 4822 3 0.49
    4 1 4820 6 0.89
    5 1 4821 6 0.87
    6 1 4822 6 0.89
    7 1 1 12 31.68
    # ... abbreviated ...


    loop_
    _ma_qa_metric_local_pairwise.ordinal_id
    _ma_qa_metric_local_pairwise.label_asym_id_1
    _ma_qa_metric_local_pairwise.label_asym_id_2
    _ma_qa_metric_local_pairwise.label_comp_id_1
    _ma_qa_metric_local_pairwise.label_comp_id_2
    _ma_qa_metric_local_pairwise.label_seq_id_1
    _ma_qa_metric_local_pairwise.label_seq_id_2
    _ma_qa_metric_local_pairwise.metric_id
    _ma_qa_metric_local_pairwise.metric_value
    _ma_qa_metric_local_pairwise.model_id
    1 A A MET MET 1 1 13 1.0 1
    2 A A MET GLY 1 2 13 1.0 1
    # ... abbreviated ...
    384401 A A MET MET 1 1 14 0.8 1
    384402 A A MET GLY 1 2 14 4.0 1
    # ... abbreviated ...

    loop_
    _ma_qa_metric_feature_pairwise.ordinal_id
    _ma_qa_metric_feature_pairwise.feature_id_1
    _ma_qa_metric_feature_pairwise.feature_id_2
    _ma_qa_metric_feature_pairwise.metric_id
    _ma_qa_metric_feature_pairwise.metric_value
    _ma_qa_metric_feature_pairwise.model_id
    2 4820 4821 4 0.12 1
    3 4820 4822 4 0.12 1
    # ... abbreviated ...
    11 4820 4821 5 26.42 1
    12 4820 4822 5 26.49 1
    # ... abbreviated ...

Traditionally, local scores were defined for each residue of a polymer.
However, with the advent of co-folding methods such as AlphaFold 3, ModelCIF introduced per-feature scores to offer greater flexibility.
These scores can be used to define granularity at the level of atoms, residues, and entity instances (e.g., a single polymer chain or small molecule), and they can also mix different granularities.
For instance, AlphaFold 3's PAE scores require pairwise scores between residues and atoms when a model contains both polymers and non-polymers.
To handle per-feature scores, we need to define the granularity of features in the [`ma_feature_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_feature_list.html) category and then further define the individual selections in the [`ma_atom_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_atom_feature.html), [`ma_entity_instance_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_entity_instance_feature.html) and [`ma_poly_residue_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_poly_residue_feature.html) categories. The following illustrative example selects an atom, a residue and a polymer chain from a given set of coordinates defined in the [`atom_site`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_site.html) category:

    loop_
    _atom_site.group_PDB
    _atom_site.id
    _atom_site.type_symbol
    _atom_site.label_atom_id
    _atom_site.label_alt_id
    _atom_site.label_comp_id
    _atom_site.label_asym_id
    _atom_site.label_entity_id
    _atom_site.label_seq_id
    _atom_site.pdbx_PDB_ins_code
    _atom_site.Cartn_x
    _atom_site.Cartn_y
    _atom_site.Cartn_z
    _atom_site.occupancy
    _atom_site.B_iso_or_equiv
    _atom_site.auth_seq_id
    _atom_site.auth_comp_id
    _atom_site.auth_asym_id
    _atom_site.pdbx_PDB_model_num
    ATOM 1 N N . MET A 1 1 ? 24.144 -19.210 17.374 1.00 31.67 1 MET A 1
    ATOM 2 C CA . MET A 1 1 ? 23.813 -20.144 16.276 1.00 35.87 1 MET A 1
    ATOM 3 C C . MET A 1 1 ? 23.006 -19.369 15.258 1.00 40.70 1 MET A 1
    ATOM 4 O O . MET A 1 1 ? 22.076 -18.680 15.664 1.00 39.21 1 MET A 1
    ATOM 5 C CB . MET A 1 1 ? 23.011 -21.353 16.781 1.00 33.69 1 MET A 1
    ATOM 6 C CG . MET A 1 1 ? 23.903 -22.358 17.505 1.00 29.21 1 MET A 1
    ATOM 7 S SD . MET A 1 1 ? 22.949 -23.712 18.252 1.00 26.20 1 MET A 1
    ATOM 8 C CE . MET A 1 1 ? 24.289 -24.766 18.863 1.00 23.86 1 MET A 1
    # ... abbreviated ...

    loop_
    _ma_feature_list.feature_id
    _ma_feature_list.feature_type
    _ma_feature_list.entity_type
    1 atom polymer
    2 residue polymer
    3 'entity instance' polymer

    loop_
    _ma_atom_feature.ordinal_id
    _ma_atom_feature.feature_id
    _ma_atom_feature.atom_id
    1 1 8

    loop_
    _ma_poly_residue_feature.ordinal_id
    _ma_poly_residue_feature.feature_id
    _ma_poly_residue_feature.label_asym_id
    _ma_poly_residue_feature.label_seq_id
    _ma_poly_residue_feature.label_comp_id
    1 2 A 1 MET

    loop_
    _ma_entity_instance_feature.ordinal_id
    _ma_entity_instance_feature.feature_id
    _ma_entity_instance_feature.label_asym_id
    1 3 A

Using the [`_ma_qa_metric.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_qa_metric.data_id.html) item, it is possible to connect quality estimates to data in the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category (with [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "model quality assessment scores") to connect them with protocol steps in the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category.


### Adding reference databases used in modeling

Reference databases used for modeling include sequence databases used for template searches and alignments.
These databases are considered one of the main inputs for ML-based *ab initio* methods such as AlphaFold, where they are used to construct MSAs.
The [`ma_data_ref_db`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data_ref_db.html) category captures this information.
The [`_ma_data_ref_db.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data_ref_db.data_id.html) connects it with the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category (with [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "reference database"). This allows the databases to be defined as input to protocol steps in the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category.
The following example showcases the reference databases used in ColabFold and how they are connected to the protocol step (adapted from [ma-kul-lams-02](https://modelarchive.org/doi/10.5452/ma-kul-lams-02)):

    loop_
    _ma_data.id
    _ma_data.name
    _ma_data.content_type
    1 'Laminin subunit alpha-1 (LN,LE1-2) with mutation Q94R' target
    2 'Top ranked model' 'model coordinates'
    3 UniRef30 'reference database'
    4 'ColabFold DB' 'reference database'

    loop_
    _ma_data_group.ordinal_id
    _ma_data_group.group_id
    _ma_data_group.data_id
    1 1 1
    2 1 3
    3 1 4
    4 2 2

    loop_
    _ma_data_ref_db.data_id
    _ma_data_ref_db.name
    _ma_data_ref_db.location_url
    _ma_data_ref_db.version
    _ma_data_ref_db.release_date
    3 UniRef30 https://wwwuser.gwdg.de/~compbiol/colabfold/uniref30_2202.tar.gz 2022_02 .
    4 'ColabFold DB' https://wwwuser.gwdg.de/~compbiol/colabfold/colabfold_envdb_202108.tar.gz 2021_08 .

    loop_
    _ma_protocol_step.ordinal_id
    _ma_protocol_step.protocol_id
    _ma_protocol_step.step_id
    _ma_protocol_step.method_type
    _ma_protocol_step.details
    _ma_protocol_step.software_group_id
    _ma_protocol_step.input_data_group_id
    _ma_protocol_step.output_data_group_id
    1 1 1 modeling 'Model generated using ColabFold v1.5.2 with AlphaFold producing 5 models with 3 recycles each, with AMBER relaxation, without templates, ranked by pLDDT, starting from an MSA from MMseqs2 (UniRef+Environmental).'
    1 1 2


### Adding template structures

Known structures are commonly used in modeling. In *ab initio* methods these can be provided as additional input structures while for template-based structure prediction, the template structures and the alignment of the modeling target to the template are the main input.
ModelCIF distinguishes the two cases by having the values "template structure" or "input structure" in the [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) item.
For the latter case, a simple list of input structures can be provided using the [`ma_template_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_details.html) and [`ma_template_ref_db_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_ref_db_details.html) categories as in the following example (adapted from [AF-H2Q5N4-F1-v6](https://alphafold.ebi.ac.uk/entry/AF-H2Q5N4-F1) which uses 4 entries from the PDB as input for modeling:

    loop_
    _ma_template_details.ordinal_id
    _ma_template_details.target_asym_id
    _ma_template_details.template_auth_asym_id
    _ma_template_details.template_data_id
    _ma_template_details.template_entity_type
    _ma_template_details.template_id
    _ma_template_details.template_model_num
    _ma_template_details.template_origin
    _ma_template_details.template_trans_matrix_id
    1 A A 2 polymer 1 1 "reference database" 1 
    2 A B 2 polymer 2 1 "reference database" 1 
    3 A B 2 polymer 3 1 "reference database" 1 
    4 A B 2 polymer 4 1 "reference database" 1 

    loop_
    _ma_template_ref_db_details.db_accession_code
    _ma_template_ref_db_details.db_name
    _ma_template_ref_db_details.template_id
    1MP1 PDB 1 
    1MNG PDB 2 
    3LIO PDB 3 
    3LJF PDB 4 

Additional categories are used to define the use of template structures in more detail:

- [`ma_template_trans_matrix`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_trans_matrix.html) records the transformation matrix applied to the structural template before using it for modeling.
- [`ma_template_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_poly.html) records details about the polymeric structural templates used in template-based modeling.
- [`ma_template_poly_segment`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_poly_segment.html) records details about segments of the structural templates used in template-based modeling.
- [`ma_template_non_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_non_poly.html) records details about non-polymeric structural templates used in template-based modeling.
- [`ma_template_branched`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_branched.html) records details about the structural templates for branched polymers used in template-based modeling.
- [`ma_template_coord`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_coord.html) records coordinates for custom, user-provided structural templates used in modeling.
- [`ma_template_customized`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_customized.html) records details for custom, user-provided structural templates used in modeling.

Target-template alignments are defined using the [`ma_alignment_info`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment_info.html), [`ma_alignment_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment_details.html), [`ma_alignment`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment.html), and [`ma_target_template_poly_mapping`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_template_poly_mapping.html) categories.
The [`_ma_alignment_info.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_alignment_info.data_id.html) connects it with the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category (with [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "target-template alignment"). This allows the databases to be defined as input to protocol steps in the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category.
The following example showcases such an alignment (adapted from [ma-denv-03](https://modelarchive.org/doi/10.5452/ma-denv-03)):

    loop_
    _ma_alignment_info.alignment_id
    _ma_alignment_info.data_id
    _ma_alignment_info.software_group_id
    _ma_alignment_info.alignment_length
    _ma_alignment_info.alignment_type
    _ma_alignment_info.alignment_mode
    1 5 1 495 'target-template pairwise alignment' local

    loop_
    _ma_alignment_details.ordinal_id
    _ma_alignment_details.alignment_id
    _ma_alignment_details.template_segment_id
    _ma_alignment_details.target_asym_id
    _ma_alignment_details.score_type
    _ma_alignment_details.score_value
    _ma_alignment_details.percent_sequence_identity
    _ma_alignment_details.sequence_identity_denominator
    1 1 1 A 'HHblits e-value' 3e-188 68.485 'Number of aligned residue pairs (not including the gaps)'

    loop_
    _ma_alignment.ordinal_id
    _ma_alignment.alignment_id
    _ma_alignment.target_template_flag
    _ma_alignment.sequence
    1 1 1 MRCVGIGNRDFVEGLSGATWVDVVLEHGSCVTTMAKNKPTLDIELLKTEVTNPAVLRKLCIEAKISNTTTDSRCPTQGEATLVEEQDANFVCRRTFVDRGWGNGCGLFGKGSLLTCAKFKCVTKLEGKIVQYENLKYSVIVTVHTGDQHQVGNETTEHGTIATITPQAPTSEIQLTDYGALTLDCSPRTGLDFNEMVLLTMKEKSWLVHKQWFLDLPLPWTSGASTSQETWNRQDLLVTFKTAHAKKQEVVVLGSQEGAMHTALTGATEIQTSGTTTIFAGHLKCRLKMDKLTLKGTSYVMCTGSFKLEKEVAETQHGTVLVQVKYEGTDAPCKIPFSTQDEKGVTQNGRLITANPIVTDKEKPVNIETEPPFGESYIVVGAGEKALKLSWFKKGSSIGKMFEATARGARRMAILGDTAWDFGSIGGVFTSVGKLVHQVFGTAYGVLFSGVSWTMKIGIGILLTWLGLNSRSTSLSMTCIAVGMVTLYLGVMVQA
    2 1 2 MRCIGISNRDFVEGVSGGSWVDIVLEHGSCVTTMAKNKPTLDFELIKTEAKHPATLRKYCIEAKLTNTTTASRCPTQGEPSLNEEQDKRFVCKHSMVDRGWGNGCGLFGKGGIVTCAMFTCKKNMEGKVVQPENLEYTIVITPHSGEENAVGNDTGKHGKEIKVTPQSSITEAELTGYGTVTMECSPRTGLDFNEMVLLQMENKAWLVHRQWFLDLPLPWLPGADTQGSNWIQKETLVTFKNPHAKKQDVVVLGSQEGAMHTALTGATEIQMSSGNLLFTGHLKCRLRMDKLQLKGMSYSMCTGKFKVVKEIAETQHGTIVIRVQYEGDGSPCKIPFEIMDLEKRHVLGRLITVNPIVTEKDSPVNIEAEPPFGDSYIIIGVEPGQLKLSWFKKGSSIGQMFETTMRGAKRMAILGDTAWDFGSLGGVFTSIGKALHQVFGAIYGAAFSGVSWTMKILIGVVITWIGMNSRSTSLSVSLVLVGVVTLYLGVMVQA

    loop_
    _ma_target_template_poly_mapping.id
    _ma_target_template_poly_mapping.template_segment_id
    _ma_target_template_poly_mapping.target_asym_id
    _ma_target_template_poly_mapping.target_seq_id_begin
    _ma_target_template_poly_mapping.target_seq_id_end
    1 1 A 1 495


### Adding custom chemical components

All residue and small molecule components found in PDB entries are defined in the [wwPDB chemical component dictionary (CCD)](https://www.wwpdb.org/data/ccd).
Those can readily be used in PDBx/mmCIF and ModelCIF files, but they may not cover all compounds used when building protein-ligand interaction models. For those cases, custom chemical components can be defined within the ModelCIF file by using the [`ma_chem_comp_descriptor`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_chem_comp_descriptor.html) category.
Additionally, these chemical components are labeled in PDBx/mmCIF categories using the [`_chem_comp.ma_provenance`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_chem_comp.ma_provenance.html) and [`_pdbx_entity_nonpoly.ma_model_mode`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_pdbx_entity_nonpoly.ma_model_mode.html) items.
The following example showcases such a custom definition for Ethionamide (adapted from [ma-tbvar3d-15](https://modelarchive.org/doi/10.5452/ma-tbvar3d-15)):

    loop_
    _chem_comp.id
    _chem_comp.type
    _chem_comp.name
    _chem_comp.formula
    _chem_comp.formula_weight
    _chem_comp.ma_provenance
    ALA 'L-peptide linking' ALANINE 'C3 H7 N O2' 89.094 'CCD Core'
    ETH non-polymer Ethionamide 'C8 H10 N2 S' 166.242 'CCD local'
    # ... abbreviated ...

    loop_
    _ma_chem_comp_descriptor.ordinal_id
    _ma_chem_comp_descriptor.chem_comp_id
    _ma_chem_comp_descriptor.chem_comp_name
    _ma_chem_comp_descriptor.type
    _ma_chem_comp_descriptor.value
    _ma_chem_comp_descriptor.software_id
    1 ETH Ethionamide 'IUPAC Name' 2-ethylpyridine-4-carbothioamide 3
    2 ETH Ethionamide 'Canonical SMILES' CCC1=NC=CC(=C1)C(=S)N 4
    3 ETH Ethionamide 'Isomeric SMILES' CCC1=NC=CC(=C1)C(=S)N 4
    4 ETH Ethionamide InChI InChI=1S/C8H10N2S/c1-2-7-5-6(8(9)11)3-4-10-7/h3-5H,2H2,1H3,(H2,9,11) 5
    5 ETH Ethionamide 'InChI Key' AEOCXXJPGCBFJA-UHFFFAOYSA-N 5
    6 ETH Ethionamide 'PubChem CID' 2761171 .

    loop_
    _pdbx_entity_nonpoly.entity_id
    _pdbx_entity_nonpoly.name
    _pdbx_entity_nonpoly.comp_id
    _pdbx_entity_nonpoly.ma_model_mode
    2 Ethionamide ETH implicit


### Adding multiple models

PDBx/mmCIF supports entries with multiple models, which are identified using the [`_atom_site.pdbx_PDB_model_num`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_atom_site.pdbx_PDB_model_num.html)) item.
This is commonly used for NMR ensembles and ModelCIF builds on top of this by allowing individual models to be listed and named in the [`ma_model_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_list.html) category, models to be grouped into annotated clusters in the [`ma_model_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_group.html) and [`ma_model_group_link`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_group_link.html) categories, and representative models to be selected in the [`ma_model_representative`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_representative.html) category.
The following example shows how multiple models from a single AlphaFold run can be stored using these categories:

    loop_
    _ma_model_list.ordinal_id
    _ma_model_list.model_name
    _ma_model_list.data_id
    _ma_model_list.model_type
    1 'Top ranked model (alphafold2_multimer_v3_model_5_seed_000)' 2 'Ab initio model'
    2 '#2 ranked model (alphafold2_multimer_v3_model_2_seed_000)' 3 'Ab initio model'
    3 '#3 ranked model (alphafold2_multimer_v3_model_4_seed_000)' 4 'Ab initio model'
    4 '#4 ranked model (alphafold2_multimer_v3_model_1_seed_000)' 5 'Ab initio model'
    5 '#5 ranked model (alphafold2_multimer_v3_model_3_seed_000)' 6 'Ab initio model'

    loop_
    _ma_model_group.id
    _ma_model_group.name
    _ma_model_group.details
    1 'AlphaFold models' '5 models generated and ranked by AlphaFold 2'

    loop_
    _ma_model_group_link.group_id
    _ma_model_group_link.model_id
    1 1
    1 2
    1 3
    1 4
    1 5

    loop_
    _ma_model_representative.id
    _ma_model_representative.model_group_id
    _ma_model_representative.model_id
    _ma_model_representative.selection_criteria
    1 1 1 'best scoring model'

A cluster of models and its representative can be grouped together or kept separate.
The choice between these two options should be based on how the modeling was carried out and how the representative was chosen.
If the representative is a member of the ensemble (i.e. the best-scoring model), it is recommended that the representative and the ensemble belong to the same group.
If the representative is calculated from the ensemble (i.e. the centroid), it is recommended that the representative be in a different group.

Multiple groups of models are useful for protocols that sample multiple conformational states (e.g. open/closed or active/inactive).
The protocol should include details that affect the sampled state space, such as the protonation state of titratable residues, pH value, ionic strength of the environment, and sampling methodology. If these details differ between model groups, this can be indicated in the annotations of the respective model groups.


### Adding energy estimates

Accurate modeling of multiple conformational states makes it impossible to categorize them as "better" or "worse".
Instead, they occupy different regions of the energy landscape, some of which may correspond to biological states.
In addition to the previously described model quality estimates, ModelCIF introduces new categories that allow different energies to be stored for each conformation.
These categories include conformational free energies, interaction energies, solvation energies, and more.

Energy estimates are captured in the [`ma_energy_estimates`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_energy_estimates.html) and [`ma_energy_estimates_value`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_energy_estimates_value.html) categories.
The type of energy and its unit are well defined in the [`_ma_energy_estimates.energy_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_energy_estimates.energy_type.html) and [`_ma_energy_estimates.unit`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_energy_estimates.unit.html) items.
Using the [`_ma_energy_estimates.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_energy_estimates.data_id.html) item, it is possible to connect quality estimates to data in the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category (with [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "energy estimate") to connect them with protocol steps in the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category.
Separate values for the same energy estimate can be defined for different models identified by the [`_ma_energy_estimates_value.model_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_energy_estimates_value.model_id.html) item and optionally for subsets of the model using the [`_ma_energy_estimates_value.feature_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_energy_estimates_value.feature_id.html) item.
The following example shows how multiple energy estimates are stored using these categories:

    loop_
    _ma_energy_estimates.ordinal_id
    _ma_energy_estimates.energy_type
    _ma_energy_estimates.unit
    _ma_energy_estimates.details
    _ma_energy_estimates.data_id
    1 "folding free energy" "kcal/mol" "Calculated using CHARMM" 1
    2 "solvation energy" "kcal/mol" "Calculated using Poisson Boltzman" 2

    loop_
    _ma_energy_estimates_value.ordinal_id
    _ma_energy_estimates_value.energy_estimates_id
    _ma_energy_estimates_value.model_id
    _ma_energy_estimates_value.feature_id
    _ma_energy_estimates_value.numerical_value
    1 1 1 . -6.52
    2 1 2 . -7.23
    3 1 3 . -6.89
    4 2 3 5 -12.13


### Adding experimental validation

ModelCIF supports the storage of data describing how the modeled system's existence was validated through experiments.
The goal is to provide experimental evidence that supports the biological plausibility of the input.
For example, this could include entities forming a complex with a specific stoichiometry or designed proteins folding properly.
This category is not intended to capture experimental data used in modeling (e.g. via spatial restraints) since such types of data are handled by [IHMCIF](https://github.com/ihmwg/IHMCIF) for deposition in the PDB-IHM branch of the PDB archive.

Experimental validation results are captured in the [`ma_experimental_validation`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_experimental_validation.html) category.
The [`_ma_experimental_validation.method`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_experimental_validation.method.html) item describes the experimental technique used while the [`_ma_experimental_validation.type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_experimental_validation.type.html) item defines the type of evidence.
This category may also include negative evidence (e.g. for models used to distinguish positive and negative results) and this is captured in the [`_ma_experimental_validation.positive_outcome`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_experimental_validation.positive_outcome.html) item.
Using the [`_ma_experimental_validation.data_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_experimental_validation.data_id.html) item, it is possible to connect quality estimates to data in the [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) category (with [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "experimental validation") to connect them with protocol steps in the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category.
The following example shows how multiple experimental results are stored using this category:

    loop_
    _ma_experimental_validation.ordinal_id
    _ma_experimental_validation.method
    _ma_experimental_validation.type
    _ma_experimental_validation.value
    _ma_experimental_validation.positive_outcome
    _ma_experimental_validation.reference_type
    _ma_experimental_validation.reference_doi
    _ma_experimental_validation.reference_url
    _ma_experimental_validation.details
    1 MST 'partial assembly' 5.3e-6 YES 'peer-reviewed article' 10.xxxx/xxxxx .
    'Binding affinity measured using MST, confirming the interaction.'
    2 SPR 'partial assembly' 2.1e-7 YES database . https://www.bindingdb.org
    'SPR was used to determine affinity.'
    3 SAXS 'full assembly' . YES 'conference proceedings' . https://www.structconference.org
    'SAXS data confirm overall shape of the complex.'


### Adding additional details and data for complex protocols

ModelCIF is designed to be flexible enough to cover the rapidly expanding spectrum of modeling studies.
Free text descriptions in various categories allow users to describe protocol steps and the data used in those steps with any level of detail.
For complex protocols, the [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) category can contain multiple protocols, which are then broken down into sequential steps using the [`_ma_protocol_step.protocol_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.protocol_id.html) and [`_ma_protocol_step.step_id`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.step_id.html) items.
The [`_ma_protocol_step.method_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_protocol_step.method_type.html) classifies and distinguishes commonly used modeling steps.

The [`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) item distinguishes types of data used as input or output of the protocol steps.
These types are often connected to additional data provided in separate ModelCIF categories, as described in previous sections.
However, they can also refer to data provided as accompanying data.
For instance, MSAs used as input for modeling ([`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "coevolution MSA") or intermediate data for protein design studies ([`_ma_data.content_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_ma_data.content_type.html) = "intermediate backbone" or "intermediate sequence") are best provided as accompanying data or described in the [`_ma_protocol_step.details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/.html) item for the respective protocol steps.


## ModelCIF support

Tools to handle ModelCIF files:

- [python-modelcif](https://github.com/ihmwg/python-modelcif) to create ModelCIF files
- [PDBx/mmCIF Software Resources](https://mmcif.wwpdb.org/docs/software-resources.html) to read and modify any type of mmCIF file
- [modelcif-converters](https://git.scicore.unibas.ch/schwede/modelcif-converters/) include ModelCIF conversion scripts used for depositions in [ModelArchive](https://modelarchive.org/). These scripts are mostly based on python-modelcif. There is also a ModelCIF validation tool
based on [RCSB's CifCheck](https://github.com/rcsb/cpp-dict-pack) in the repository.

Modeling services and repositories known to contain or produce valid ModelCIF files:
[ModelArchive](https://www.modelarchive.org),
[ModBase](https://modbase.compbio.ucsf.edu),
[Modeller](https://salilab.org/modeller/),
[SWISS-MODEL Repository](https://swissmodel.expasy.org/repository),
[SWISS-MODEL](https://swissmodel.expasy.org/),
[AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/),
[AlphaFold Server](https://alphafoldserver.com/).

## Summary of data categories

### PDBx/mmCIF categories (relevant subset)

Here, we list a subset of PDBx/mmCIF categories which are commonly observed in valid ModelCIF files (e.g. as found in [ModelArchive](https://modelarchive.org/)). Some of these categories are listed as they are required to make the ModelCIF file valid if some other set of data is provided (e.g. atom coordinates in the [`atom_site`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_site.html) category require the [`_atom_site.type_symbol`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_atom_site.type_symbol.html) item to be set which in turn makes it mandatory to have [`_atom_type.symbol`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Items/_atom_type.symbol.html) items set in the [`atom_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_type.html) category).

| Category name                         | Category details                                  |
|---------------------------------------|---------------------------------------------------|
| [`atom_site`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_site.html) | Atomic XYZ coordinates with model quality estimates commonly stored in place of B-factors |
| [`atom_type`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/atom_type.html) | Atom types used |
| [`audit_author`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/audit_author.html) | Authors for the model |
| [`audit_conform`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/audit_conform.html) | ModelCIF dictionary version used |
| [`chem_comp`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/chem_comp.html) | Chemical components used |
| [`citation`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/citation.html) | Citations to manuscript for which the model was generated and to software used |
| [`citation_author`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/citation_author.html) | Authors for the citations |
| [`database_2`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/database_2.html) | Database identifier provided |
| [`entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity.html) | Molecular entities with type and description |
| [`entity_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_poly.html) | Details for polymer entities |
| [`entity_poly_seq`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_poly_seq.html) | Sequences for polymer entities |
| [`entity_src_nat`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entity_src_nat.html) | Source organisms for the molecular entities |
| [`entry`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/entry.html) | Defines ID for the entry and optionally links it to a model set |
| [`pdbx_audit_revision_category`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_audit_revision_category.html) | Categories changed in the revision history |
| [`pdbx_audit_revision_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_audit_revision_details.html) | Details for the revision history |
| [`pdbx_audit_revision_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_audit_revision_group.html) | Content groups changed in the revision history |
| [`pdbx_audit_revision_history`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_audit_revision_history.html) | Revision history for this entry |
| [`pdbx_audit_revision_item`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_audit_revision_item.html) | Data items changed in the revision history |
| [`pdbx_contact_author`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_contact_author.html) | Authors to be contacted about this entry |
| [`pdbx_data_usage`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_data_usage.html) | Licensing and terms of use for the model |
| [`pdbx_database_status`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_database_status.html) | Keeps track of data processing and status of the entry |
| [`pdbx_entity_nonpoly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_entity_nonpoly.html) | Details for non-polymer entities |
| [`pdbx_nonpoly_scheme`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_nonpoly_scheme.html) | Residue level nomenclature mapping for non-polymer entities |
| [`pdbx_poly_seq_scheme`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/pdbx_poly_seq_scheme.html) | Residue level nomenclature mapping for polymer entities |
| [`software`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/software.html) | Software used to create this model |
| [`struct`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct.html) | Information about the modeled structure including name and details for a model deposition |
| [`struct_asym`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_asym.html) | Defines IDs for instances of the molecular entities and implicitly the modeled stoichiometry |
| [`struct_ref`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref.html) | Relates molecular entities to entries in external reference databases |
| [`struct_ref_seq`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref_seq.html) | Relates sequences of modeled entities to sequences in related reference databases |
| [`struct_ref_seq_dif`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/struct_ref_seq_dif.html) | Differences between the modeled entities and sequences in related reference databases |


### ModelCIF categories

| Category name                         | Category details                                  |
|---------------------------------------|---------------------------------------------------|
| [`ma_alignment`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment.html) | Alignments between target and template sequences |
| [`ma_alignment_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment_details.html) | Details for alignments between target and template sequences |
| [`ma_alignment_info`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_alignment_info.html) | Lists used alignments between target and template sequences |
| [`ma_angle_restraints`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_angle_restraints.html) | Computationally determined angle restraints used in modeling |
| [`ma_associated_archive_file_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_associated_archive_file_details.html) | Accompanying data within an associated archive file (zip/gzip) |
| [`ma_atom_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_atom_feature.html) | Selects specific atoms (independent of entity type) for features |
| [`ma_chem_comp_descriptor`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_chem_comp_descriptor.html) | Internal definition of chemical components not defined in the CCD |
| [`ma_coevolution_msa`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_coevolution_msa.html) | Details about MSAs stored in ModelCIF |
| [`ma_coevolution_msa_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_coevolution_msa_details.html) | MSAs stored in ModelCIF (discouraged in favor of storing MSAs in accompanying data) |
| [`ma_coevolution_seq_db_ref`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_coevolution_seq_db_ref.html) | Reference database identifiers for the sequences in the MSAs stored in ModelCIF |
| [`ma_data`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data.html) | Input and output data for the modeling protocol |
| [`ma_data_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data_group.html) | Groups of data used as input or output for individual protocol steps |
| [`ma_data_ref_db`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_data_ref_db.html) | Reference databases used in modeling |
| [`ma_dihedral_restraints`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_dihedral_restraints.html) | Computationally determined dihedral restraints used in modeling |
| [`ma_distance_restraints`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_distance_restraints.html) | Computationally determined distance restraints used in modeling |
| [`ma_energy_estimates`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_energy_estimates.html) | Energy estimates calculated for the models |
| [`ma_energy_estimates_value`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_energy_estimates_value.html) | Values for the energy estimates per model or feature |
| [`ma_entity_instance_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_entity_instance_feature.html) | Selects specific entity instances (independent of entity type) for features |
| [`ma_entry_associated_files`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_entry_associated_files.html) | Associated files of accompanying data |
| [`ma_experimental_validation`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_experimental_validation.html) | Experimental validation for the existence of the modeled system |
| [`ma_feature_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_feature_list.html) | List of features used to select subsets of the model |
| [`ma_model_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_group.html) | Annotated list of model groups |
| [`ma_model_group_link`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_group_link.html) | Connects individual models to a group |
| [`ma_model_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_list.html) | Annotated list of models in the file |
| [`ma_model_representative`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_model_representative.html) | Representative models selected among all models |
| [`ma_poly_residue_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_poly_residue_feature.html) | Selects specific polymer residues for features |
| [`ma_poly_template_library_components`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_poly_template_library_components.html) | Connects individual templates with a library defined in ModelCIF |
| [`ma_poly_template_library_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_poly_template_library_details.html) | Lists polymeric template libraries defined in ModelCIF (discouraged in favor of referencing libraries in ma_data_ref_db) |
| [`ma_poly_template_library_list`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_poly_template_library_list.html) | Lists templates used to build a template library defined in ModelCIF |
| [`ma_protocol_step`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_protocol_step.html) | Lists modeling protocol steps performed |
| [`ma_qa_metric`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric.html) | Metrics used to assess model quality |
| [`ma_qa_metric_dihedral`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_dihedral.html) | Model quality estimate values for individual dihedral angles |
| [`ma_qa_metric_feature`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_feature.html) | Model quality estimate values for individual features (subsets of the model) |
| [`ma_qa_metric_feature_pairwise`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_feature_pairwise.html) | Model quality estimate values for pairs of features |
| [`ma_qa_metric_global`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_global.html) | Model quality estimate values for full models |
| [`ma_qa_metric_local`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_local.html) | Model quality estimate values for individual polymer residues |
| [`ma_qa_metric_local_pairwise`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_qa_metric_local_pairwise.html) | Model quality estimate values for pairs of polymer residues |
| [`ma_restraints`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_restraints.html) | List of computationally determined restraints used in modeling |
| [`ma_restraints_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_restraints_group.html) | Groups of computationally determined restraints used in modeling |
| [`ma_software_group`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_software_group.html) | Groups of software used for individual protocol steps including connection to software parameters used |
| [`ma_software_parameter`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_software_parameter.html) | Software parameters used in the protocol steps |
| [`ma_struct_assembly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_struct_assembly.html) | Structural assemblies modeled (obsolete category; ModelCIF is restricted to a single composition of molecules defined in struct_asym) |
| [`ma_struct_assembly_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_struct_assembly_details.html) | Additional details regarding the structure assembly (obsolete category) |
| [`ma_target_entity`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_entity.html) | Modeled target entities |
| [`ma_target_entity_instance`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_entity_instance.html) | Modeled instances of the molecular entities |
| [`ma_target_ref_db_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_ref_db_details.html) | Relates modeled molecular entities to entries in external databases |
| [`ma_target_template_poly_mapping`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_target_template_poly_mapping.html) | Mappings of the polymeric targets to the structural templates |
| [`ma_template_branched`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_branched.html) | Details about the structural templates for branched polymers used in template-based modeling |
| [`ma_template_coord`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_coord.html) | Coordinates for custom, user-provided structural templates used in modeling |
| [`ma_template_customized`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_customized.html) | Details for custom, user-provided structural templates used in modeling |
| [`ma_template_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_details.html) | Structural templates used in modeling |
| [`ma_template_non_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_non_poly.html) | Details about non-polymeric structural templates used in template-based modeling |
| [`ma_template_poly`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_poly.html) | Details about the polymeric structural templates used in template-based modeling |
| [`ma_template_poly_segment`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_poly_segment.html) | Segments of the structural templates used in template-based modeling |
| [`ma_template_ref_db_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_ref_db_details.html) | Details about structural templates obtained from reference databases |
| [`ma_template_trans_matrix`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_template_trans_matrix.html) | Transformation matrices applied to structural templates before using them for modeling |
