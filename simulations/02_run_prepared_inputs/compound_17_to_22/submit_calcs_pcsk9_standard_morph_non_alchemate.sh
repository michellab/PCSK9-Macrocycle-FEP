#!/bin/bash
prod_time=10000

for system_name in "compound_17_to_22_unmap_ole_h_free_leg" "compound_17_to_22_unmap_ole_h_bound_leg"
do
    for repl in 1 2 3
    do
        apptainer run --nv --bind ../somd2_extensions/src/somd2/runner/_runner.py:/app/src/somd2/src/somd2/runner/_runner.py \
        --bind ../somd2_extensions/src/somd2/config/_config.py:/app/src/somd2/src/somd2/config/_config.py \
        ../../docker/pcsk9_fep_v1.0.sif \
        python somd2_api_runner_prod_multi_conf.py --equib_time 250 --prod_time $prod_time --system_name $system_name --replicate $repl
    done
done

