import argparse
import sire as sr
import somd2 as sd
import os
from shutil import copy2


def get_user_input():
    parser = argparse.ArgumentParser(description="Simulation parameters")
    parser.add_argument(
        "--equib_time", type=int, required=True, help="Equilibration time in seconds"
    )
    parser.add_argument(
        "--prod_time", type=int, required=True, help="Production time in seconds"
    )
    parser.add_argument("--system_name", type=str, required=True, help="System name")
    parser.add_argument(
        "--replicate",
        type=int,
        required=False,
        help="Replicate to run. If not provided, all replicates will be run",
    )
    parser.add_argument(
        "--use_hrex",
        action="store_true",
        help="Whether to run a Hamiltonian replica exchange simulation",
    )

    parser.add_argument(
        "--use_rest2",
        action="store_true",
        help="Whether to run a REST2 simulation, needs to be used with --use_hrex",
    )

    args = parser.parse_args()
    return (
        args.equib_time,
        args.prod_time,
        args.system_name,
        args.replicate,
        args.use_hrex,
        args.use_rest2,
    )


if __name__ == "__main__":
    equib_time, prod_time, system_name, repl, hrex, rest2 = get_user_input()
    print(f"Equilibration Time: {equib_time} picoseconds")
    print(f"Production Time: {prod_time} picoseconds")
    print(f"System name: {system_name}")
    print(f"Replicate: {repl}")
    print(f"Hamiltonian Replica Exchange: {hrex}")
    print(f"REST2: {rest2}")

    if rest2 and not hrex:
        raise ValueError("REST2 can only be used with Hamiltonian Replica Exchange")

    sire_system = sr.stream.load(f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss")

    # DYANMICS PARAMETERS
    if repl is None:
        repls = [1, 2, 3]
    else:
        repls = [repl]

    for repl in repls:

        equil_time = f"{equib_time}ps"
        run_time = f"{prod_time}ps"

        base_name = f"{system_name}_{run_time}_{equil_time}_no_ghosts_11_lam_multi_conf_repl_{repl}"

        if hrex:
            work_dir = f"dynamics_hrex/{base_name}"
            if rest2:
                work_dir = f"dynamics_rest2/{base_name}"
        else:
            work_dir = f"dynamics_std/{base_name}"

        # check if work_dir exists, if not create it
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        else:
            print(f"Directory {work_dir} already exists, cleaning it!")
            os.system(f"rm -r {work_dir}")

        config = sd.config.Config()

        ### SOMD2 CONFIGURATION
        config.log_level = "debug"
        config.log_file = "output.log"
        config.runtime = run_time
        config.cutoff_type = "PME"
        config.cutoff = "14A"
        config.timestep = "4fs"
        config.lambda_schedule = "standard_morph"
        config.equilibration_time = equil_time

        config.energy_frequency = "2ps"
        config.frame_frequency = "100ps"
        config.checkpoint_frequency = "500ps"
        config.output_directory = work_dir
        config.ghost_modifications = False
        config.multi_conformational_seeding = True
        config.multi_conformational_seeding_lambda_threshold = 0.50
        config.save_energy_components = False
        config.shift_delta = f"2.25A"
        config.shift_coulomb = f"1A"
        config.num_lambda = 11
        if hrex:
            config.replica_exchange = True

            runner = sd.runner.RepexRunner(config=config, system=sire_system)
        else:
            runner = sd.runner.Runner(config=config, system=sire_system)

        runner.run()

        try:
            print("Copying topology files")
            copy2(f"{work_dir}/system0.prm7", f"{work_dir}/system0.parm7")
            copy2(f"{work_dir}/system1.prm7", f"{work_dir}/system1.parm7")
        except FileNotFoundError:
            print("Could not find the topology files to copy")
            pass
