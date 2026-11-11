import argparse
import sire as sr
import somd2 as sd
import os
from shutil import copy2
from loguru import logger


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

    parser.add_argument(
        "--restart",
        action="store_true",
        help="Whether to restart the simulation from a previous checkpoint",
    )

    parser.add_argument(
        "--extend_time",
        type=int,
        required=False,
        help="Time to extend the simulation by",
    )

    args = parser.parse_args()
    return (
        args.equib_time,
        args.prod_time,
        args.system_name,
        args.replicate,
        args.use_hrex,
        args.use_rest2,
        args.restart,
        args.extend_time,
    )


if __name__ == "__main__":
    equib_time, prod_time, system_name, repl, hrex, rest2, restart, extend_time = get_user_input()
    print(f"Equilibration Time: {equib_time} picoseconds")
    print(f"Production Time: {prod_time} picoseconds")
    print(f"System name: {system_name}")
    print(f"Replicate: {repl}")
    print(f"Hamiltonian Replica Exchange: {hrex}")
    print(f"REST2: {rest2}")
    print(f"Restart: {restart}")
    print(f"Extend Time: {extend_time}")

    if extend_time is not None:
        if restart is False:
            logger.error(
                "You cannot extend the production time if you are not restarting the simulation!"
            )
            raise ValueError("Restart must be True to extend production time.")

        new_prod_time = prod_time + extend_time
        logger.info(
            f"Extending production time by {extend_time} ps to {new_prod_time} ps"
        )

    if rest2 and not hrex:
        raise ValueError("REST2 can only be used with Hamiltonian Replica Exchange")

    sire_system = sr.stream.load(f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss")
    ref_system = sire_system.clone()
    ref_system = sr.morph.link_to_reference(ref_system)


    # DYANMICS PARAMETERS
    if repl is None:
        repls = [1, 2, 3]
    else:
        repls = [repl]

    for repl in repls:

        equil_time = f"{equib_time}ps"
        run_time = f"{prod_time}ps"

        base_name = f"{system_name}_{run_time}_{equil_time}_multi_conf_standard_morph_repl_{repl}"

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
            logger.info(
                f"Directory {work_dir} already exists, cleaning it in the next step!"
            )

        # check if work_dir exists, if not create it
        if not restart:
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
            else:
                os.system(f"rm -r {work_dir}")

        config = sd.config.Config()

        if restart:
            config.restart = True
            if extend_time is not None:
                config.runtime = f"{new_prod_time}ps"
            else:
                config.runtime = run_time
        else:
            config.runtime = run_time

        ### SOMD2 CONFIGURATION
        config.log_level = "debug"
        config.log_file = "output.log"
        config.cutoff_type = "PME"
        config.cutoff = "14A"
        config.timestep = "4fs"
        config.equilibration_time = equil_time
        config.shift_delta="2.25A"
        config.shift_coulomb="1A"

        config.energy_frequency = "2ps"
        config.frame_frequency = "100ps"
        config.checkpoint_frequency = "500ps"
        config.output_directory = work_dir
        config.ghost_modifications = True
        config.multi_conformational_seeding = True
        config.save_energy_components = True
        config.ghost_modifications=False
        config.lambda_schedule = "standard_morph"
        config.lambda_values = [
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
        ]
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
