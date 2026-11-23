# PCSK9-Macrocycle-FEP

Data and scripts to reproduce the alchemical free energy calculations reported in:

**Alchemical Free Energy Methods Reproduce Scaffold Modifications in a Macrocyclic Peptide PCSK9 Series**
Audrius Kalpokas¹ [ORCID: 0000-0002-4579-070X], Mark Mackey² [ORCID: 0000-0001-5131-7583], Julien Michel¹* [ORCID: 0000-0003-0360-1760]

¹ EaStCHEM School of Chemistry, The University of Edinburgh, Edinburgh, EH9 3FJ, United Kingdom
² Cresset, New Cambridge House, Bassingbourn Rd, Litlington, SG8 0SS, United Kingdom
\* Corresponding author: [julien.michel@ed.ac.uk](mailto:julien.michel@ed.ac.uk)

Preprint: https://chemrxiv.org/doi/full/10.26434/chemrxiv.15011937/v1

---

## Citation

If you use this repository, please cite the manuscript:

```bibtex
@article{
doi:10.26434/chemrxiv.15011937/v1,
author = {Audrius Kalpokas  and Mark Mackey  and Julien Michel },
title = {Alchemical Free Energy Methods Reproduce Scaffold Modifications in a Macrocyclic Peptide PCSK9 Series},
journal = {ChemRxiv},
volume = {2026},
number = {1110},
pages = {},
year = {2026},
doi = {10.26434/chemrxiv.15011937/v1},
URL = {https://chemrxiv.org/doi/abs/10.26434/chemrxiv.15011937/v1},
eprint = {https://chemrxiv.org/doi/pdf/10.26434/chemrxiv.15011937/v1},
}
```

This repository is archived on Zenodo together with the container images used to run the simulations (DOI: <!-- TODO: add once archived -->). The GitHub repository does not contain the container images, so use the Zenodo record to get them (see [`simulations/docker/README.md`](simulations/docker/README.md)). The GitHub repository may be a few commits ahead of the Zenodo record.

---

## A note on reproducibility vs. general use

This repository provides and pins exact package versions, docker images, conda builds, and git commit
hashes throughout, including source builds of Sire and BioSimSpace at
specific historical commits. This is done to let anyone
reproduce the precise environment used in the associated
publication.

**This is not the recommended way to use the OpenBioSim stack for your own
work.** If you're interested in peptide or general biomolecular modelling
with Sire, BioSimSpace, or related tools, you should install the latest
stable (or `devel`) releases rather than following the pinned instructions
here — these provide bug fixes, performance improvements, and features that
didn't exist at the time this paper was written. See:

- [Sire installation instructions](https://github.com/openbiosim/sire#installation)
- [BioSimSpace installation instructions](https://github.com/openbiosim/biosimspace#installation)
- [SOMD2 installation instructions](https://github.com/openbiosim/somd2#installation)

The pinned setup exists purely for reproducibility purposes.

---

## Repository structure
```markdown
├── data/                          # Raw `.sdf` and `.pdb` input structures used to build
│                                   # perturbable systems (`.bss`) for the SOMD2 engine
│   ├── ligands/                   # Macrocycle ligand structures (`.sdf`)
│   └── proteins/                  # PCSK9 protein structure (`.pdb`)
├── simulations/                   # Instructions for running the transformations
│                                   # described in the manuscript
│   ├── docker/
│   │   └── README.md              # Instructions for retrieving the Docker images
│   │                               # used to run simulations
│   ├── 01_prepare_inputs/         # Build perturbable systems from data/
│   │   ├── parametrised_ligands/  # OpenFF/NAGL-parametrised ligands (`.prm7`/`.rst7`/`.pdb`)
│   │   └── campaign.json          # Edges: ligand pairs, atom mappings, ring-breaking flags
│   ├── 02_run_prepared_inputs/    # Run SOMD2 free energy simulations
│   │   ├── compound_X_to_Y/       # Run and submit scripts for each transformation
│   │   └── somd2_extensions/      # Modified SOMD2 source files bind-mounted into the container
│   ├── 03_analyse_free_energies/  # Compute free energy estimates from simulation output,
│   │                               # with an example leg (`c17_to_c5_ring_break_free/`)
│   └── plotting/                  # Data and scripts for reproducing key figures
└── LICENSE                        # Code license (MIT)
```

---

## Requirements

- Apptainer (as used for the manuscript) or Docker, and an NVIDIA GPU — see [`simulations/docker/README.md`](simulations/docker/README.md)
- Conda environment for running analysis & plotting scripts

---

## Quickstart

```bash
git clone https://github.com/michellab/PCSK9-Macrocycle-FEP.git
cd PCSK9-Macrocycle-FEP
```

1. **Get the container images** — download them from the Zenodo record or pull them from Docker Hub, as described in [`simulations/docker/README.md`](simulations/docker/README.md).
2. **Prepare inputs** — follow instructions in [`simulations/01_prepare_inputs`](simulations/01_prepare_inputs) to build perturbable systems from `data/`.
3. **Run simulations** — follow instructions in [`simulations/02_run_prepared_inputs`](simulations/02_run_prepared_inputs).
4. **Analyse free energies** — follow instructions in [`simulations/03_analyse_free_energies`](simulations/03_analyse_free_energies).
5. **Reproduce manuscript figures** — follow instructions in [`simulations/plotting/overall_performance`](simulations/plotting/overall_performance). The post-processed results are included, so the figures can be regenerated without rerunning any simulation.

---

## Data availability

Raw ligand (`data/ligands/*.sdf`) and protein (`data/proteins/*.pdb`) input structures, along with the post-processed free energy results used to generate the manuscript figures (`simulations/plotting/`), are provided directly in this repository. The container images used to run the simulations are archived in the Zenodo record of this repository.

---

## License

Code in this repository (scripts in `simulations/`, including `simulations/plotting/`) is released under the **MIT License** (see [`LICENSE`](LICENSE)).

---

## Contact

Questions about this repository or the manuscript can be raised by opening an issue or directed to the corresponding author, Julien Michel ([julien.michel@ed.ac.uk](mailto:julien.michel@ed.ac.uk)).
