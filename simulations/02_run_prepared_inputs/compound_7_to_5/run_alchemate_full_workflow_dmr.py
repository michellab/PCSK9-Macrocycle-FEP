from somd2.config import Config
from alchemate.manager import WorkflowManager
from alchemate.context import SimulationContext
from alchemate.steps.preprocessing import OptimizeLambdaProbabilities
from alchemate.steps.base import RunBasicCalculation
from alchemate.logger import setup_logging

import sire as sr
import argparse
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
    parser.add_argument(
        "--de_strength", type=str, required=True, help="DE strength"
    )
    parser.add_argument("--system_name", type=str, required=True, help="System to run")
    parser.add_argument(
        "--replicate",
        type=int,
        required=True,
        help="Replicate to run. If not provided, all replicates will be run",
    )
    parser.add_argument(
        "--bond_strength", type=str, required=False, help="Bond strength"
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
        args.de_strength,
        args.system_name,
        args.replicate,
        args.bond_strength,
        args.overwrite
    )


if __name__ == "__main__":
    (
        equib_time,
        prod_time,
        de_strength,
        system_name,
        replicate,
        bond_strength,
        overwrite
    ) = get_user_input()


sire_system = sr.stream.load(f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss")


hard_restraints, sire_system = sr.restraints.morse_potential(
    sire_system,
    de="150 kcal mol-1",
    auto_parametrise=True,
    direct_morse_replacement=True,
    name="morse_hard"
)
print(hard_restraints)


soft_restraints, _ = sr.restraints.morse_potential(
    sire_system,
    atoms0=hard_restraints[0].atom0(),
    atoms1=hard_restraints[0].atom1(),
    r0=hard_restraints[0].r0(),
    k=f"125 kcal mol-1 A-2",
    auto_parametrise=False,
    direct_morse_replacement=False,
    de=f"{de_strength} kcal mol-1",
    name="morse_soft",
)
print(soft_restraints)
print(f"Sire system type:{type(sire_system)}")

somd2_config = Config()
somd2_config.lambda_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.625, 0.65, 0.657, 0.663, 0.675, 0.7, 0.8, 0.9, 1.0] 

if bond_strength is None:
    somd2_config.output_directory = f"dynamics_alchemate_dmr/{system_name}_k_match_de_{int(de_strength)}_runtime_{int(prod_time)}_repl_{replicate}"
else:
    somd2_config.output_directory = f"dynamics_alchemate_dmr/{system_name}_k_{int(bond_strength)}_de_{int(de_strength)}_repl_{replicate}"
somd2_config.timestep = "2fs"
somd2_config.cutoff = "14A"
somd2_config.cutoff_type = "PME"
somd2_config.lambda_schedule = "ring_break_morph"

# somd2_config.runtime = "5ns"
somd2_config.equilibration_time = f"{equib_time}ps"
somd2_config.equilibration_timestep = "2fs"
somd2_config.equilibration_constraints = True
somd2_config.ghost_modifications = False
somd2_config.num_energy_neighbours = 1

if overwrite:
    somd2_config.overwrite = True

somd2_config.h_mass_factor = 3

somd2_config.energy_frequency = "2ps"
somd2_config.frame_frequency = "100ps"
somd2_config.checkpoint_frequency = "500ps"

somd2_config.rest2_scale = 1

somd2_config.replica_exchange = True
somd2_config.log_level = "debug"

somd2_config.save_energy_components = True
somd2_config.restraints = [hard_restraints, soft_restraints]
somd2_config.timeout = "30 s"
somd2_config.shift_delta = f"2.25A"
somd2_config.shift_coulomb = f"1A"

context = SimulationContext(system=f"../../01_prepare_inputs/alchemical_somd2_run_files/{system_name}.bss", somd2_config=somd2_config)


simulation_workflow = [
    OptimizeLambdaProbabilities(optimization_attempts=10, optimization_target="repex_matrix", optimization_threshold=0.10, optimization_runtime="500ps", vacuum_optimization=False),
    RunBasicCalculation(calculation_runtime=f"{prod_time}ps"),
]

manager = WorkflowManager(context=context, workflow_steps=simulation_workflow)
final_context = manager.execute()