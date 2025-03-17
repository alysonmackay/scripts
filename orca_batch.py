import os
 
suffix = "_test" # job type 
input_comment = "this is a test"

xyz_files = ["tmpd_i_opt.xyz", "tmpd_f_opt.xyz"]

submit_slurm = True # control sbatch
 
orca_variables = {
        "method": "B3LYP",
        "basis": "def2-TZVP",
        "charge": 0,
        "mult": 1,
        "other": "TightSCF NormalPrint",
	"block": "",
}

slurm_variables = {
        "ntasks": 4,
	"mem": 12,
	"time": "00-12:00",
	"path": "$HOME/scratch",
}

def generate_orca_input(filename, xyz_filename):
    input_content = f"""# {input_comment}
%pal nprocs {slurm_variables['ntasks']}
end
! {orca_variables['method']} {orca_variables['basis']} {orca_variables['other']}
{orca_variables['block']}

* xyzfile {orca_variables['charge']} {orca_variables['mult']} {xyz_filename}\n"""

    with open(filename, 'w') as f:
        f.write(input_content)

input_files_generated = 0

# generating orca input files 
for xyz_filename in xyz_files:
    base_name = xyz_filename.split('.')[0]
    input_filename = f"{base_name}{suffix}.inp"
    slurm_sub = f"{base_name}_sub.sh"
    
    generate_orca_input(input_filename, xyz_filename)
    input_files_generated += 1
print(f"{input_files_generated} ORCA input files generated successfully.") 

slurm_scripts_generated = 0

def generate_slurm_script(filename):
	slurm_content = f"""#!/bin/bash
#
#
#SBATCH --nodes=1
#SBATCH --ntasks={slurm_variables['ntasks']}
#SBATCH --mem={slurm_variables['mem']}
#SBATCH --time={slurm_variables['time']}
#SBATCH --job-name={input_filename}
#
export SCRDIR=/tmp/$USER
mkdir -p $SCRDIR

module load openblas
module load StdEnv/2023 gcc/12.3  openmpi/4.1.5
module load orca/6.0.1
$EBROOTORCA/orca {slurm_variables['path']}/{input_filename} > {slurm_variables['path']}/{base_name}{suffix}.out
rm -fr /tmp/$USER
seff $SLURM_JOBID

echo "Job Complete!" \n""" 

	with open(filename, 'w') as f:
		f.write(slurm_content)

# generating and launching SLURM batch scripts 
for xyz_filename in xyz_files:
    generate_slurm_script(slurm_sub)
    slurm_scripts_generated += 1
    if submit_slurm:
    	os.system('sbatch {slurm_sub}')
if submit_slurm:
    print(f"{slurm_scripts_generated} SLURM submit scripts generated and launched successfully")
else:
    print(f"{slurm_scripts_generated} SLURM submit scripts generated successfully")
