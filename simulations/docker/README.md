# Container images
2 container images were used to run the alchemical free energy simulations described in the
manuscript:

| Tag                   | Used for                                                                | Image ID / registry digest |
|-----------------------|-------------------------------------------------------------------------|----------------------------|
| `v1.0`                | Transformations that **DID NOT INVOLVE** bond creation or annihilation | `sha256:2453c4b87220f7a5bc90618784dcf07696877ab6ed0f8133b6bedb7e01ba8c47` |
| `v2.0-scaffold-hop`   | Transformations that **INVOLVED** bond creation or annihilation        | `sha256:1241ea4e05f58fd76d1add07ae857cb53d08fdd9a0e026381adda6ba415b5209` |

Both are `linux/amd64` images. Simulations were run via [Apptainer](https://apptainer.org/), so the
submit scripts in [`../02_run_prepared_inputs`](../02_run_prepared_inputs) expect the following files
in this directory:

```
pcsk9_fep_v1.0.sif
pcsk9_fep_v2.0-scaffold-hop.sif
```

The images can be obtained from the Zenodo archive (recommended) or from Docker Hub.

## Option 1: Zenodo archive (recommended)

The Zenodo record of this repository (DOI: <!-- TODO: add once archived -->) contains both images
as `docker save` archives, placed in this directory:

| File                                        | Image                                    |
|---------------------------------------------|------------------------------------------|
| `pcsk9_fep_v1.0.docker.tar.gz`              | `akalpokas/pcsk9_fep:v1.0`               |
| `pcsk9_fep_v2.0-scaffold-hop.docker.tar.gz` | `akalpokas/pcsk9_fep:v2.0-scaffold-hop`  |

These archives are not part of the GitHub repository. If you cloned from GitHub, download them from
Zenodo into this directory.

First, check that the downloads are intact, from this directory:

```bash
sha256sum -c SHA256SUMS
```

Then convert each archive to an Apptainer `.sif` file:

```bash
apptainer build pcsk9_fep_v1.0.sif docker-archive://pcsk9_fep_v1.0.docker.tar.gz
apptainer build pcsk9_fep_v2.0-scaffold-hop.sif docker-archive://pcsk9_fep_v2.0-scaffold-hop.docker.tar.gz
```

Or load them into Docker:

```bash
docker load -i pcsk9_fep_v1.0.docker.tar.gz
docker load -i pcsk9_fep_v2.0-scaffold-hop.docker.tar.gz
```

## Option 2: Docker Hub

The images are also published to Docker Hub under
[`akalpokas/pcsk9_fep`](https://hub.docker.com/repository/docker/akalpokas/pcsk9_fep/general).
Pull each image by its digest, which identifies the exact image used in the manuscript even if a tag
is later moved, and convert it directly to a `.sif` file:

```bash
apptainer pull pcsk9_fep_v1.0.sif docker://akalpokas/pcsk9_fep@sha256:2453c4b87220f7a5bc90618784dcf07696877ab6ed0f8133b6bedb7e01ba8c47
apptainer pull pcsk9_fep_v2.0-scaffold-hop.sif docker://akalpokas/pcsk9_fep@sha256:1241ea4e05f58fd76d1add07ae857cb53d08fdd9a0e026381adda6ba415b5209
```

## Verifying the containers

```bash
apptainer exec pcsk9_fep_v1.0.sif python -c "import somd2, sire; print('somd2', somd2.__version__); print('sire', sire.__version__)"
```

Should yield:
```bash
somd2 0.1+95.geef3abb
sire 2026.1.0.dev
```

```bash
apptainer exec pcsk9_fep_v2.0-scaffold-hop.sif python -c "import somd2, sire; print('somd2', somd2.__version__); print('sire', sire.__version__)"
```

Should yield:
```bash
somd2 2026.2.0.dev+12.g196237b
sire 2026.2.0.dev
```

## Running with Docker instead of Apptainer

The submit scripts use Apptainer. To run a script with Docker instead, you need two settings that
Apptainer and SLURM normally provide:

- `--gpus all`, to give the container access to the GPU (needs the NVIDIA Container Toolkit).
- `-e CUDA_VISIBLE_DEVICES=0` (or the devices you want to use). SOMD2 stops with
  `CUDA_VISIBLE_DEVICES not set` if this variable is missing. On an HPC cluster, SLURM sets it.

Docker also does not mount the current directory or replace the image's entrypoint, so mount the
repository and the `somd2_extensions` files yourself. For example, from
`02_run_prepared_inputs/compound_2_to_7`:

```bash
docker run --rm --gpus all -e CUDA_VISIBLE_DEVICES=0 --entrypoint "" \
    -v "$(realpath ../..)":/work/simulations \
    -v "$(realpath ../somd2_extensions/src/somd2/config/_config.py)":/app/src/somd2/src/somd2/config/_config.py \
    -w /work/simulations/02_run_prepared_inputs/compound_2_to_7 \
    akalpokas/pcsk9_fep:v1.0 \
    python somd2_api_runner_new_multi_conf_seed.py --equib_time 250 --prod_time 10000 \
    --system_name compound_2_to_7_twisted_free_leg --use_hrex --replicate 1
```
