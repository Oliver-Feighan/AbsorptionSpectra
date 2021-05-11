# Based on OpenMM example simulation at http://docs.openmm.org/latest/userguide/application.html#a-first-example

import argparse
from pathlib import Path

from simtk.openmm.app import *
from simtk.openmm import * 
from simtk.unit import *
from sys import stdout

parser = argparse.ArgumentParser(description="Run an MM MD workflow using OpenMM software")
parser.add_argument("pdb_path", action="store", type=Path, help="Path to system PDB file")
parser.add_argument("xml_path", action="store", type=Path, help="Path to system XML file")
parser.add_argument("chkpt_path", action="store", type=Path, help="Path to output checkpoint file")
parser.add_argument("-n", "--ncores", action="store", type=int, help="Number of cores to use", dest="ncores", required=True)
args = parser.parse_args()

print(f"Running workflow with {args.ncores} threads")

### START WORKFLOW ###

# Name for output file (extension will be appended)
output_name = "workflow_result"
result_dir_path = Path.cwd() / "output"
result_dir_path.mkdir(exist_ok=True)

pdb_path = args.pdb_path.resolve()
xml_path = args.xml_path.resolve()
assert pdb_path.exists()
assert xml_path.exists()

chkpt_path = args.chkpt_path.resolve()
assert chkpt_path.exists()

print(f"Reading system coordinates from {pdb_path}")

# Set-up OpenMM system

pdb = PDBFile(str(pdb_path))
#forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')

# PME with a nonbonded cutoff of 1nm seems standard in the literature. See e.g. https://pubs.rsc.org/no/content/articlehtml/2015/cp/c4cp05647g
# https://pubs.rsc.org/en/content/articlehtml/2021/cp/d0cp06582j
#system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
#        nonbondedCutoff=1*nanometer)
system = XmlSerializer.deserialize(xml_path.read_text())

# Set up simulation

integrator = LangevinMiddleIntegrator(300*kelvin, 1/picosecond, 0.0005*picoseconds)
simulation = Simulation(pdb.topology, system, integrator, platform=Platform.getPlatformByName('CPU'), platformProperties={'Threads':str(args.ncores)})
#simulation.context.getPlatform().setPropertyValue(simulation.context, 'Threads', args.ncores)
simulation.context.setPositions(pdb.positions)
simulation.minimizeEnergy()

# Equilibration
result_output_path = result_dir_path / (output_name + "_EnergyAndTemp.csv")
simulation.reporters.append(StateDataReporter(str(result_output_path), 100, step=True,
        potentialEnergy=True, kineticEnergy=True, totalEnergy=True, temperature=True,
        separator=','))

chkpt_output_path = chkpt_path / (output_name + "_checkpnt.chk")
simulation.reporters.append(CheckpointReporter(str(chkpt_output_path), 1000))
simulation.step(20000)

# Production workflow
pdb_output_path = result_dir_path / (output_name + "_traj_structures.pdb")
simulation.reporters.append(PDBReporter(str(pdb_output_path), 2000))
simulation.step(100000)







