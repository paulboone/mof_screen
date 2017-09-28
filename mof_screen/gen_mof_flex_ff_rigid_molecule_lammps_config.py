
#gen-mof-flex-ff-rigid-molecule-lammps-config.py <molecule> <mof(s)>
# —minimum-box-dimension=<size> default ?
#—num-molecules=<num> default 1

import argparse
import os
import sys

import subprocess

from mof_screen.lammps_interface_wrappers import Parameters, convert_to_lammps_data_file
from mof_screen.pack_molecules_into_mof import pack_molecules_into_mof

def gen_mof_flex_ff_rigid_molecule_lammps_config(molecule_path, mof_path, minimum_box_dimension=12.5, num_molecules=1):
    mof_name, _ = os.path.splitext(os.path.basename(mof_path))
    molecule_name, _ = os.path.splitext(os.path.basename(molecule_path))


    params = Parameters(mof_path)
    params.cutoff = minimum_box_dimension
    params.force_field = "UFF"

    ### GENERATE LAMMPS DATA FILE FOR MOF WITH FORCE_FIELD PARAMS
    convert_to_lammps_data_file(params)

    # smit code always outputs lammps data file with name: data.{mof_name}
    data_filename = "data.%s" % mof_name

    ### GENERATE MOF XYZ FILE FROM LAMMPS DATA FILE
    mof_xyz_filename = "%s.xyz" % mof_name
    subprocess.run("lmp_data_to_xyz.py %s > %s" % (data_filename, mof_xyz_filename), shell=True, check=True)

    ### GENERATE PACKMOL SCRIPT TO PACK MOF WITH N MOLECULES
    packmol_filename = "packmol_%s_%d_%s.txt" % (mof_name, num_molecules, molecule_name)
    with open(data_filename, 'r') as f:
        packmol_script = pack_molecules_into_mof(f, mof_name, molecule_name, num_molecules)
    with open(packmol_filename, 'w') as f:
        f.write(packmol_script)


    ### RUN PACKMOLE TO PACK MOLECULES INTO MOF
    subprocess.run("packmol < %s" % (packmol_filename), shell=True, check=True)


    ### EXTRACT MOLECULE POSITIONS FROM PACKMOLE OUTPUT AND CREATE LAMMPS DATA FILE

def cmdline():
    parser = argparse.ArgumentParser("./gen-mof-flex-ff-rigid-molecule-lammps-config.py")
    parser.add_argument('molecule_path', help="Path to molecule XYZ")
    parser.add_argument('mof_path', help="Path to MOF CIF with P1 symmetry")
    parser.add_argument('--minimum-box-dimension', '-d', default=12.5, help="minimum box dimension (angstroms) of extended unit cell")
    parser.add_argument('--num-molecules', '-n', default=1, help="number of molecules to pack into MOF")
    args = parser.parse_args()

    gen_mof_flex_ff_rigid_molecule_lammps_config(args.molecule_path, args.mof_path,
        minimum_box_dimension=args.minimum_box_dimension,
        num_molecules=args.num_molecules
    )
