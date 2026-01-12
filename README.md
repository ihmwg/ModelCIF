
# ModelCIF

[ModelCIF](dist/mmcif_ma.dic) provides the data representation for describing 
structural models of macromolecules derived from computational methods. 
ModelCIF is developed and maintained by the [ModelCIF Working Group](http://www.wwpdb.org/task/modelcif).
These models may be derived from already 
existing structural templates (also known as homology modeling or comparative modeling methods) 
or can be obtained from *ab initio* modeling methods.

ModelCIF data standards are used or supported by various model repositories (e.g. [ModelArchive](https://www.modelarchive.org),
[ModBase](https://modbase.compbio.ucsf.edu), [SWISS-MODEL Repository](https://swissmodel.expasy.org/repository),
[AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/)), modeling applications (e.g. 
[Modeller](https://salilab.org/modeller/), [SWISS-MODEL](https://swissmodel.expasy.org/),
[D-I-TASSER](https://aideepmed.com/D-I-TASSER/), [AlphaFold](https://alphafoldserver.com/),
[Boltz](https://github.com/jwohlwend/boltz/), [Chai](https://github.com/chaidiscovery/chai-lab/)),
and visualization software (e.g. [Mol*](https://molstar.org/), [ChimeraX](https://www.cgl.ucsf.edu/chimerax/)).

The [python-modelcif](https://github.com/ihmwg/python-modelcif) library facilitates the programmatic
creation of ModelCIF files and includes convenience classes to streamline this process. A collection
of ModelCIF conversion scripts, mostly based on python-modelcif, as well as a ModelCIF validation tool
based on [RCSB's CifCheck](https://github.com/rcsb/cpp-dict-pack), are available in a dedicated
[modelcif-converters](https://git.scicore.unibas.ch/schwede/modelcif-converters/) code repository
maintained by the ModelArchive team.

[ModelCIF](dist/mmcif_ma.dic) is an extension of the [PDBx/mmCIF](http://mmcif.wwpdb.org) 
dictionary. The [PDBx/mmCIF](http://mmcif.wwpdb.org) dictionary is used by the [wwPDB](http://www.wwpdb.org) to
archive structural models of macromolecules determined using X-ray crystallography, NMR spectroscopy
and cryogenic electron microscopy.

ModelCIF dictionary is distributed in two forms: 
 - ModelCIF dictionary combined with definitions in the parent PDBx/mmCIF dictionary (available at **dist/mmcif_ma.dic**) and 
 - ModelCIF extension separately without the definitions in the parent PDBx/mmCIF dictionary (available at **dist/mmcif_ma_ext.dic**) 

The primary publication about ModelCIF is available at https://doi.org/10.1016/j.jmb.2023.168021.  

*For more details regarding the dictionary, see the 
[ModelCIF dictionary documentation](dictionary_documentation/documentation.md) 
and the [mmCIF resources website](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/).*
