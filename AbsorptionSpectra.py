import os
import re
import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt

def run_qcore(chrom):
	qcore_path = os.environ["qcore_path"]

	json_run = subprocess.run(f"{qcore_path} -f json -s \" res := bchla(structure({chrom.to_qcore_string()}))\"",
		shell=True,
		stdout=subprocess.PIPE,
		executable="/bin/bash",
		universal_newlines=True)

	result = json.loads(json_run.stdout)["res"]

	return result

class Chromophore():
	def __init__(self):
		self.elem = []
		self.xyz = []
		self.n_atoms = 0

	def to_qcore_string(self):
		assert(len(self.elem) == len(self.xyz))
		result = "xyz = ["

		for i in range(self.n_atoms):
			result += f"[{self.elem[i]}, {np.array2string(self.xyz[i], separator=', ')[1:-1]}]"

			if i != self.n_atoms-1:
				result += ","

		
		result += "]"

		return result

	def append(self, elem : str, xyz : np.array):
		self.elem.append(elem)
		self.xyz.append(xyz)
		self.n_atoms += 1

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
	energies = []

	for frame in range(len(start_lines)):
		frame_chromophore = Chromophore()

		for enum, line in enumerate(frame_lines[start_lines[frame]+1:end_lines[frame]]):
			elem = re.findall(r'\S+', line)[-1]
			xyz = np.array([float(x) for x in re.findall(r'\d*\.\d*', line)[:3]])

			frame_chromophore.append(elem, xyz)

		chromophores[f"frame_{frame}"] = frame_chromophore
		energies.append(run_qcore(frame_chromophore)["excitation_energy"])

	plt.hist(energies)
	plt.show()


