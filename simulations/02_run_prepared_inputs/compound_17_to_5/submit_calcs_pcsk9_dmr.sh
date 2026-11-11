#!/bin/bash
prod_time=10000
de_strength=50

for system_name in "compound_17_to_17_rb_only_free_leg" "compound_17_to_17_rb_only_bound_leg"
do
    for repl in 1 2 3
    do
        apptainer run --nv ../../docker/pcsk9_fep_v2.0-scaffold-hop.sif \
        python run_alchemate_full_workflow_dmr.py --equib_time 250 --prod_time $prod_time --de_strength $de_strength --system_name $system_name --replicate $repl
    done
done
