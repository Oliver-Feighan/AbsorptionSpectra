#!/bin/bash
#PBS -N openmm
#PBS -o openmm.out
#PBS -e openmm.err
#PBS -l select=1:ncpus=24:mem=16G
#PBS -l walltime=24:00:00

ENV_NAME="openmm"
INPUT_SCRIPT="${PBS_O_WORKDIR}/run_workflow.py"
PDB_PATH="${PBS_O_WORKDIR}/cla_in_ether.pdb"
XML_PATH="${PBS_O_WORKDIR}/cla_in_ether_System.xml"
TMP_RESULT_DIR="${TMPDIR}/output"
RESULT_DIR="${PBS_O_WORKDIR}/output"

# Job information
echo "Host:    $(hostname)"
echo "Time:    $(date)"
echo "Dir:     $(pwd)"
echo "Job ID:  ${PBS_JOBID}"
echo "NCPUS:   ${NCPUS}"
echo "Nodelist:"
echo "  $(cat "${PBS_NODEFILE}" | uniq)"

# Setup shell for conda
# (based on conda initialize section of .bashrc, see e.g. https://erictleung.com/conda-in-subshell-script)
CONDA_SETUP="$(conda shell.bash hook)"
eval "${CONDA_SETUP}"

conda activate ${ENV_NAME}

echo "Conda env:  ${ENV_NAME}"
echo "Python:     $(which python)"
echo "Job script: ${ENTOS_SCRIPT}"
echo "Result dir: ${RESULT_DIR}"

echo -e "\n[Running job script]\n"

mkdir -p ${RESULT_DIR}

python ${INPUT_SCRIPT} ${PDB_PATH} ${XML_PATH} ${RESULT_DIR} -n ${NCPUS}

echo -e "\n[Job script finished]\n"

echo -e "Copying job script results to ${RESULT_DIR}\n"
cp -v ${TMP_RESULT_DIR}/* ${RESULT_DIR}/
