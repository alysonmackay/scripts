import os

suffix = "_test"
input_comment = "this is a test"

xyz_files = ["tmpd_i_opt.xyz", "tmpd_f_opt.xyz"]

# define common variables 
common_settings = {
        "method": "B3LYP",
        "basis": "def2-TZVP",
        "charge": 0,
        "multiplicity": 1,
        "extra_options": "TightSCF",
}

# define parameters of SLURM submission 
slurm_settings = {
        "ntasks": 4,
	"mem": 12,
	"time": "00-12:00",
	"path": "$HOME/scratch",
}

# creating input files 
def generate_orca_input(filename, xyz_filename):
    """
    Generates an ORCA input file using the common settings, referencing an XYZ file.
    """
    input_content = f"""# {input_comment}
%pal nprocs {slurm_settings['ntasks']} end
! {common_settings['method']} {common_settings['basis']} {common_settings['extra_options']}

* xyzfile {common_settings['charge']} {common_settings['multiplicity']} {xyz_filename}\n"""

    # Write content to file
    with open(filename, 'w') as f:
        f.write(input_content)

input_files_generated = 0

# Generate input files based on the xyz_files list
for xyz_filename in xyz_files:
    base_name = xyz_filename.split('.')[0]
    input_filename = f"{base_name}{suffix}.inp"
    slurm_sub = f"{base_name}_sub.sh"
    
    generate_orca_input(input_filename, xyz_filename)
    input_files_generated += 1
print(f"{input_files_generated} ORCA input files generated successfully.") 

slurm_scripts_generated = 0

# creating slurm submit scripts 
def generate_slurm_script(filename):
	"""
	Generates a SLURM submit script using the default SLURM settings 

	"""
	slurm_content = f"""#!/bin/bash
#
#
#SBATCH --nodes=1
#SBATCH --ntasks={slurm_settings['ntasks']}
#SBATCH --mem={slurm_settings['mem']}
#SBATCH --time={slurm_settings['time']}
#SBATCH --job-name={input_filename}
#
export SCRDIR=/tmp/$USER
mkdir -p $SCRDIR

module load openblas
module load StdEnv/2023 gcc/12.3  openmpi/4.1.5
module load orca/6.0.1
$EBROOTORCA/orca {slurm_settings['path']}/{input_filename} > {slurm_settings['path']}/{base_name}{suffix}.out
rm -fr /tmp/$USER
seff $SLURM_JOBID

echo "Job Complete!" \n""" 

	# Write content to file
	with open(filename, 'w') as f:
		f.write(slurm_content)

# Generate and launch SLURM batch scripts 
for xyz_filename in xyz_files:
    generate_slurm_script(slurm_sub)
    slurm_scripts_generated += 1
    os.system('sbatch {slurm_sub}')
print(f"{slurm_scripts_generated} SLURM submit scripts generated and launched successfully")
