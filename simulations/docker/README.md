# Docker images
2 Docker images were used to run the alchemical free energy simulations described in the
manuscript, published to Docker Hub under
[`akalpokas/pcsk9_fep`](https://hub.docker.com/repository/docker/akalpokas/pcsk9_fep/general):

| Tag                  | Used for                                              |
|----------------------|--------------------------------------------------------|
| `v1.0`                | Transformations that **DID NOT INVOLVE** bond-creation or annihiliation |
| `v2.0-scaffold-hop`   | Transformations that **INVOLVED** bond-creation or annihiliation  |

Simulations were run via [Apptainer](https://apptainer.org/) and the instructions below convert each Docker image directly into an Apptainer `.sif` file.


## Pulling and converting the images

Pull each tag and convert it directly to a `.sif` container image:

```bash
apptainer pull pcsk9_fep_v1.0.sif docker://akalpokas/pcsk9_fep:v1.0
apptainer pull pcsk9_fep_v2.0-scaffold-hop.sif docker://akalpokas/pcsk9_fep:v2.0-scaffold-hop
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

## Long-term availability

The built `.sif` files for both tags are also archived alongside the tagged release of this repository on Zenodo
(DOI: <!-- TODO: add once archived -->), in case the images are no longer available on Docker Hub.