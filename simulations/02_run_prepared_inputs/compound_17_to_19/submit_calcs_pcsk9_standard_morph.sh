#!/bin/bash
prod_time=10000

for system_name in "compound_17_to_19_free_leg" "compound_17_to_19_bound_leg"
do
    for repl in 1 2 3
    do
        apptainer run --nv --bind ../somd2_extensions/src/somd2/config/_config.py:/app/src/somd2/src/somd2/config/_config.py \
        ../../docker/pcsk9_fep_v1.0.sif \
        python run_alchemate_standard_morph_full_workflow.py --equib_time 250 --prod_time $prod_time --system_name $system_name --replicate $repl
    done
done
