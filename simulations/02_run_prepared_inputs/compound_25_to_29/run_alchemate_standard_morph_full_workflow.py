from somd2.config import Config
from alchemate.manager import WorkflowManager
from alchemate.context import SimulationContext
from alchemate.steps.preprocessing import OptimizeLambdaProbabilities
from alchemate.steps.base import RunBasicCalculation
from alchemate.logger import setup_logging

import sire as sr
import argparse
import os
from shutil import copy2


def get_user_input():
    parser = argparse.ArgumentParser(description="Simulation parameters")
    parser.add_argument(
        "--equib_time",
        type=int,
        required=True,
        help="Equilibration time in picoseconds",
    )
    parser.add_argument(
        "--prod_time", type=int, required=True, help="Production time in picoseconds"
    )
    parser.add_argument("--system_name", type=str, required=True, help="System to run")
    parser.add_argument(
        "--replicate",
        type=int,
        required=True,
        help="Replicate to run. If not provided, all replicates will be run",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output directory if it exists"
    )

    args = parser.parse_args()
    return (
        args.equib_time,
        args.prod_time,
        args.system_name,
        args.replicate,
        args.overwrite
    )


if __name__ == "__main__":
    (
        equib_time,
        prod_time,
        system_name,
        replicate,
        overwrite
    ) = get_user_input()


sire_system = sr.stream.load(f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss")

somd2_config = Config()
somd2_config.lambda_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

somd2_config.rest2_scale = 1

somd2_config.output_directory = f"dynamics_alchemate/{system_name}_repl_{replicate}"
somd2_config.timestep = "2fs"
somd2_config.cutoff = "14A"
somd2_config.cutoff_type = "PME"
somd2_config.lambda_schedule = "standard_morph"

somd2_config.multi_conformational_seeding = False
somd2_config.multi_conformational_seeding_lambda_threshold = 0.67
somd2_config.equilibration_time = f"{equib_time}ps"
somd2_config.equilibration_timestep = "1fs"
somd2_config.equilibration_constraints = True
somd2_config.ghost_modifications = False

if overwrite:
    somd2_config.overwrite = True

somd2_config.h_mass_factor = 3

somd2_config.energy_frequency = "2ps"
somd2_config.frame_frequency = "100ps"
somd2_config.checkpoint_frequency = "500ps"


somd2_config.replica_exchange = True
somd2_config.log_level = "debug"

somd2_config.save_energy_components = True
somd2_config.num_energy_neighbours = 1
somd2_config.timeout = "30 s"
somd2_config.charge_difference = 0
somd2_config.shift_delta = f"2.25A"
somd2_config.shift_coulomb = f"1A"


context = SimulationContext(system=f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss", somd2_config=somd2_config)

setup_logging(log_path=f"{context.somd2_config.output_directory}/alchemate.log")

simulation_workflow = [
    OptimizeLambdaProbabilities(optimization_attempts=10, optimization_target="repex_matrix", optimization_threshold=0.10, optimization_runtime="500ps", vacuum_optimization=False),
    RunBasicCalculation(calculation_runtime=f"{prod_time}ps"),
]

manager = WorkflowManager(context=context, workflow_steps=simulation_workflow)
final_context = manager.execute()