import os
import re
import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

class Chromophore():
	def __init__(self, name):
		self.elem = []
		self.xyz = []
		self.n_atoms = 0
		self.name = name
		self.excitation_energy = None
		self.transition_dipole = None

	def to_qcore_string(self):
		assert(len(self.elem) == len(self.xyz))
		result = "xyz = ["

		for i in range(self.n_atoms):
			result += f"[{self.elem[i]}, {np.array2string(self.xyz[i], separator=', ')[1:-1]}]"

			if i != self.n_atoms-1:
				result += ","

		
		result += "]"

		return result

	def to_xyz_file(self):
		assert(len(self.elem) == len(self.xyz))
		file = open(f"frames/{self.name}.xyz", 'w')

		print(f"{self.n_atoms}", file=file)
		print(f"", file=file)

		for i in range(self.n_atoms):
			print(f"{self.elem[i]} {np.array2string(self.xyz[i], separator=' ')[1:-1]}", file=file)

		file.close()


	def append(self, elem : str, xyz : np.array):
		self.elem.append(elem)
		self.xyz.append(xyz)
		self.n_atoms += 1

class single_result():
	def __init__(self, name, energy, transition_dipole):
		self.name = name
		self.energy = energy
		self.transition_dipole = transition_dipole

def run_qcore(chrom : Chromophore):
	qcore_path = os.environ["qcore_path"]

	json_run = subprocess.run(f"{qcore_path} -f json -s \" {chrom.name} := bchla(structure({chrom.to_qcore_string()}))\"",
		shell=True,
		stdout=subprocess.PIPE,
		executable="/bin/bash",
		universal_newlines=True)

	result = json.loads(json_run.stdout)

	return single_result(chrom.name, result[chrom.name]["excitation_energy"], result[chrom.name]["transition_dipole"])

def grep_lines(match_str):
	grep_run = subprocess.run(f"grep -n \"{match_str}\" neutral_result_traj_structures.pdb",
						 shell=True,
						 stdout=subprocess.PIPE,
						 executable="/bin/bash")

	return [int(re.findall(r'\d+', x)[0]) - 1 for x in grep_run.stdout.decode("utf-8").split("\n")[:-1]]


if __name__ == '__main__':
	frame_lines = list(open("neutral_result_traj_structures.pdb"))

	start_lines = grep_lines("MODEL")
	end_lines = grep_lines("TER     138      CLA A   1")

	assert(len(start_lines) == len(end_lines))

	chromophores = {}

	for frame in range(len(start_lines)):
		frame_chromophore = Chromophore(f"frame_{frame}")

		for enum, line in enumerate(frame_lines[start_lines[frame]+1:end_lines[frame]]):
			elem = re.findall(r'\S+', line)[-1]
			xyz = np.array([float(x) for x in re.findall(r'\d*\.\d*', line)[:3]])

			frame_chromophore.append(elem, xyz)

		chromophores[f"frame_{frame}"] = frame_chromophore

	for chrom in list(chromophores.values()):
		chrom.to_xyz_file()

	with ProcessPoolExecutor(max_workers=30) as pool:
		results = list(pool.map(run_qcore, list(chromophores.values())))

	for i in results:
		chromophores[i.name].excitation_energy = i.energy
		chromophores[i.name].transition_dipole = i.transition_dipole

	for i in chromophores.keys():
		print(chromophores[i].excitation_energy)







