# Running the alchemical transformations

This directory contains the scripts used to run the SOMD2 alchemical free energy simulations reported in the manuscript. They were copied directly from our HPC and only the SLURM directives were removed. Apart from that, they are a historical snapshot of how the calculations were run. This means there is a lot of duplicated and redundant code across directories, which has been kept on purpose. The only other changes are a corrected system name in `compound_7_to_5/submit_calcs_pcsk9_standard_morph_non_alchemate.sh` (the bound leg of `7_reconnected_to_5` was mislabelled) corrected units (picoseconds, not seconds) in the `--equib_time`/`--prod_time` help text of the `somd2_api_runner_*.py` scripts, and a fix to the ring-breaking scripts `compound_7_to_5/run_alchemate_full_workflow_dmr.py`, `compound_7_to_5/run_alchemate_full_workflow_dmr_reverse.py` and `compound_35_to_25/run_alchemate_full_workflow_dmr.py`. These now pass the Morse-modified system to `SimulationContext`, as `compound_17_to_5/run_alchemate_full_workflow_dmr.py` already did, instead of reloading the unmodified `.bss` file.

## Prerequisites

- The perturbable `.bss` input files in [`../01_prepare_inputs/alchemical_somd2_run_files`](../01_prepare_inputs/alchemical_somd2_run_files). See [`../01_prepare_inputs/README.md`](../01_prepare_inputs/README.md).
- The two Apptainer images `pcsk9_fep_v1.0.sif` and `pcsk9_fep_v2.0-scaffold-hop.sif` in [`../docker`](../docker). See [`../docker/README.md`](../docker/README.md).
- An NVIDIA GPU. All runs use `apptainer run --nv`.

## Layout

```
02_run_prepared_inputs/
├── compound_X_to_Y/      # one directory per transformation in the manuscript
│   ├── submit_*.sh       # entry point: loops over free/bound legs and 3 replicates
│   └── *.py              # SOMD2 / alchemate run script called by the submit script
└── somd2_extensions/     # modified SOMD2 source files bind-mounted into the v1.0 container
```

Every submit script runs the free and bound legs, each with 3 replicates, for 10 ns of production (`--prod_time 10000`) after 250 ps of equilibration (`--equib_time 250`). The Python scripts load their inputs through relative paths (`../../01_prepare_inputs/...`), so you have to run them from inside their own `compound_X_to_Y` directory:

```bash
cd compound_17_to_19
bash submit_calcs_pcsk9_standard_morph.sh
```

## Run script types

| Script | Container | Description |
|---|---|---|
| `somd2_api_runner_*multi_conf*.py` | `v1.0` + `somd2_extensions` | SOMD2 runs with the `standard_morph` lambda schedule and multi-conformational seeding. |
| `run_alchemate_*standard_morph*.py` | `v1.0` (+ `somd2_extensions`) | Replica exchange runs driven by `alchemate`: lambda spacing is first optimised against the replica exchange matrix, then the production run follows. |
| `run_alchemate_full_workflow_dmr*.py` | `v2.0-scaffold-hop` | Same `alchemate` workflow, but for ring-breaking (`ring_break_morph`) or ring-forming (`reverse_ring_break_morph`, `*_reverse.py`) transformations. These use hard and soft Morse potential restraints (`--de_strength 50`). |

[`somd2_extensions`](somd2_extensions) contains modified copies of SOMD2's `config/_config.py` and `runner/_runner.py`, which the submit scripts bind-mount over the files in the `v1.0` container. The `multi_conformational_seeding` options themselves are already part of SOMD2 in the `v1.0` container, in both the standard (`Runner`) and replica exchange (`RepexRunner`) runners. The modified files differ from the container's copies as follows:

- `runner/_runner.py` fixes a bug in the container's `Runner`, which never creates the system for a new (non-restart) λ window and so fails before it starts. Every non-replica-exchange run (`somd2_api_runner_prod_multi_conf.py`) therefore needs this file mounted. Replica exchange runs do not use `Runner`, so `compound_2_to_7`, which runs with `--use_hrex`, mounts only the config file.
- `config/_config.py` adds four extra λ schedules (`dmr_ring_break_morph_restraints_only`, `dmr_ring_break_morph_restraints_ang_tor_only`, `restraints_on_no_morph` and `restraints_off_morphed`). None of the scripts in this repository use them, so mounting this file does not change any run reported here.

## Transformations

Some transformations were split into several steps through intermediate states. Each step has its own `.bss` input.

| Directory | Submit script(s) | Steps (system names) |
|---|---|---|
| `compound_2_to_7` | `submit_calcs_pcsk9.sh` | `2_to_7_twisted` (HREX) |
| `compound_17_to_19` | `submit_calcs_pcsk9_standard_morph.sh` | `17_to_19` |
| `compound_17_to_22` | `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `17_to_22_unmap_ole_h` |
| `compound_17_to_25` | `submit_calcs_pcsk9.sh` | `17_to_25` |
| `compound_25_to_29` | `submit_calcs_pcsk9_standard_morph.sh` | `25_to_29` |
| `compound_22_to_18` | `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `22_to_18_unmap_ole_h` |
| `compound_18_to_17` | `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `18_redo_to_18_no_ole_unmap_ole_h` → `18_no_ole_to_17_unmap_ole_h` |
| `compound_5_to_6` | `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `5_to_5_no_ole_unmap_ole_h` → `5_no_ole_to_6_alt_conf_unmap_ole_h` |
| `compound_17_to_5` | `submit_calcs_pcsk9_dmr.sh` → `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `17_to_17_rb_only` (ring break) → `17_rb_only_to_17_rb_no_ole` → `17_rb_no_ole_to_5` |
| `compound_35_to_25` | `submit_calcs_pcsk9_dmr_rb.sh` → `submit_calcs_pcsk9_dmr_sm.sh` | `35_to_25_corrected_rb_step1` (ring break) → `35_to_25_corrected_rb_step2` |
| `compound_7_to_5` | `submit_calcs_pcsk9_dmr_s1.sh` → `submit_calcs_pcsk9_dmr_s2.sh` → `submit_calcs_pcsk9_standard_morph_non_alchemate.sh` | `7_to_7_rb` (ring break) → `7_rb_to_7_reconnected` (ring formation) → `7_reconnected_to_5` |

All system names have a `compound_` prefix and a `_free_leg` or `_bound_leg` suffix.

Note that `compound_35_to_25/run_alchemate_full_workflow_standard_morph.py` (step 2, a standard morph) writes its output to `dynamics_alchemate_dmr/`, even though it is not a ring-breaking run. The directory name was kept as it was in the original runs.