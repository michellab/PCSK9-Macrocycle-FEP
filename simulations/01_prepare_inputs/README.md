# Parametrising raw .sdf molecules with OpenFF NAGL

## Environment Setup

The conda environment used for this project was built following the official OpenFF Toolkit installation instructions:
https://docs.openforcefield.org/projects/toolkit/en/stable/installation.html

To reproduce the exact environment (linux-64 only), use the provided spec file:

```bash
conda create --name openff-toolkit --file openff_toolkit_spec_file.txt
```

This will recreate the environment with the exact package versions and builds used originally.

**Notes:**
- This spec file is platform-specific (linux-64) and will not work on macOS or Windows.
- Requires the same conda channels used originally (see file header) to still be accessible.
- Activate the environment after creation:

```bash
conda activate openff-toolkit
```

Following this, use this environment with the `parametrise_raw_inputs_with_nagl.ipynb` notebook to rebuild the parametrised ligand files.

---

# Rebuilding perturbable alchemical SOMD2 files

## Environment Setup

This step requires a separate environment containing Sire and BioSimSpace, used to generate the perturbable, alchemical input files used by SOMD2. Both were installed from source at specific commits to ensure exact reproducibility, since the pre-built conda packages originally used are no longer available (see notes below).

### 1. Install Sire

```bash
conda create -n openbiosim-pcsk9-repro "python<3.12"
conda activate openbiosim-pcsk9-repro

# Build dependencies
conda install cmake pip-requirements-parser
conda install gcc gxx   # Linux; use clang/clangxx on macOS

# setuptools must be pinned below v82, since pkg_resources (removed in
# setuptools>=82) is required by this version of Sire's build script.
# See "Known issues" below for details.
conda install "setuptools<81"

conda install "sysroot_linux-64>=2.28"

# Clone and check out the exact commit
git clone https://github.com/OpenBioSim/sire
cd sire
git checkout 52402fb

# Compile and install, resolving BioSimSpace's dependencies at the same time
python setup.py --install-bss-deps --skip-dep sysroot_linux-64 install
```

This checks out Sire at commit [`52402fb`](https://github.com/openbiosim/sire/commit/52402fb) (originally packaged as `2025.4.0.dev`, build `py311h0666ab4_18`) and compiles it from source.

### 2. Install BioSimSpace from source

```bash
conda activate openbiosim-pcsk9-repro
git clone https://github.com/openbiosim/biosimspace.git
cd biosimspace
git checkout 8d7eb9c3
cd python
pip install -e .
```

This checks out commit [`8d7eb9c3`](https://github.com/openbiosim/biosimspace/commit/8d7eb9c3), corresponding to BioSimSpace version `2025.2.0.dev0+31.g8d7eb9c3`, and installs it in editable mode into the `openbiosim-pcsk9-repro` environment.

### 3. Verify the installation

```bash
python -c "import BioSimSpace, sire; print('BioSimSpace', BioSimSpace.__version__); print('sire', sire.__revisionid__)"
```

Should yield:
```bash
BioSimSpace 2025.2.0.dev+31.g8d7eb9c3
sire 52402fb
```

**Notes:**
- This installation is Linux-only.
- Sire and BioSimSpace were originally installed as pre-built conda packages (`sire=2025.4.0.dev=py311h0666ab4_18` from the `openbiosim/label/dev` channel, and BioSimSpace pip-installed from source at the commit above). **OpenBioSim's dev channel only retains a rolling window of recent builds, so the exact Sire package is no longer resolvable** — hence building from source at the pinned commit instead.
- **Known issue:** This version of Sire's `setup.py` predates the removal of `pkg_resources` from `setuptools` (removed in setuptools ≥82, late 2025). If your environment's `setuptools` is newer, the build script's dependency-installation step silently fails to install anything and errors with `CondaValueError: too few arguments`. Fix by pinning `setuptools<81` (as above) before running `setup.py`.
- **Known issue:** This version of Sire's build script pins
  `sysroot_linux-64==2.17` in its dependency list, which is too old for the
  glibc symbol versions the pre-built `libOpenMM.so` requires (causing
  `undefined reference to 'powf@GLIBC_2.27'` at the link step — see above).
  Work around this by upgrading the sysroot *and* telling the script to skip
  re-pinning it:

      conda install "sysroot_linux-64>=2.28"
      python setup.py --install-bss-deps --skip-dep sysroot_linux-64 install

Following this, use this environment with the `build_alchemical_somd2_run_files.ipynb` notebook to rebuild the perturbable, alchemical SOMD2 input files.