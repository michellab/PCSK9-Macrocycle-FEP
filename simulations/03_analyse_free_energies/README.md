# Analysing the free energy simulations

This directory contains a script and example run directory used to analyse free energy simulations reported in the manuscript. The script analyses the raw free energy data using the 3 different reported methods:
1. Full (no data discarded)
2. Rapid (first 1ns discarded, 1-5ns kept, the rest is discarded)
3. Auto-equilibration (same as full, but equilibration detection and decorrelation are applied)

## Prerequisites

- Use the `openbiosim-pcsk9-repro` conda environment installed previously or the latest `devel` BioSimSpace version in order to run the analysis script.

## Usage

Pass the script a leg directory containing one `repl_*` subdirectory per replicate, each holding the `energy_traj_*.parquet` file of every lambda window. To analyse the example ring-breaking free leg (`c17_to_c5_ring_break_free`, 3 replicates of 10 ns), run the following from this directory:

```bash
conda activate openbiosim-pcsk9-repro
python analyse_convergence.py c17_to_c5_ring_break_free
```

All replicates must have the same sampling time, otherwise the script stops with an error. The simulation temperature (`TEMPERATURE`, 300 K) and the time window of each method (`STRATEGIES`) are set at the top of the script.

## Outputs

The final forward and backward ΔG of each method and the average discarded time per replicate are printed to the terminal. The following files are written next to the leg directory, prefixed with its name (e.g. `c17_to_c5_ring_break_free_convergence.pdf`):

| File | Description |
|---|---|
| `*_convergence.pdf`, `*_convergence.png` | Forward/backward convergence plot with one panel per method, showing each replicate and the mean ± SD across replicates. |
| `*_summary_statistics.csv` | Mean and standard deviation across replicates of the final forward and backward ΔG (kcal/mol) for each method. |
| `*_convergence_data.csv` | Forward and backward ΔG (kcal/mol) and their errors at each data fraction, for each replicate and method. |
| `*_discard_metrics.csv` | Time discarded by equilibration detection for each replicate and lambda window. |