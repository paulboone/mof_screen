
#gen-mof-flex-ff-rigid-molecule-lammps-config.py <molecule> <mof(s)>
# —minimum-box-dimension=<size> default ?
#—num-molecules=<num> default 1

import argparse
import os
import sys

import subprocess

from mof_screen.lammps_interface_wrappers import Parameters, convert_to_lammps_data_file
from mof_screen import pack_molecules_into_mof
from mof_screen import packmol_to_lammps

def gen_mof_flex_ff_rigid_molecule_lammps_config(molecule_path, mof_path, datafile_path, minimum_box_dimension=12.5, num_molecules=1):
    mof_name, _ = os.path.splitext(os.path.basename(mof_path))
    molecule_name, _ = os.path.splitext(os.path.basename(molecule_path))

    params = Parameters(mof_path)
    params.cutoff = minimum_box_dimension
    params.force_field = "UFF"

    ### GENERATE LAMMPS DATA FILE FOR MOF WITH FORCE_FIELD PARAMS
    num_types = convert_to_lammps_data_file(params)
    print(len(num_types))
    ### output LAMMPS modification script
    with open("modify_lammps.sh", 'w') as f:
        modify_lammps_script = """#!/bin/bash
if [ -z "$1" ]; then echo "USAGE: ./modify_lammps.sh <config.lammps>" && exit 1; fi
sed -i orig -e 's/^variable mofAtoms equal \d*.*$/variable mofAtoms equal %d/' $1
sed -i ''   -e 's/^variable mofBonds equal \d*.*$/variable mofBonds equal %d/' ./mof_screen.lammps
sed -i ''   -e 's/^variable mofAngles equal \d*.*$/variable mofAngles equal %d/' ./mof_screen.lammps
sed -i ''   -e 's/^variable mofDihedrals equal \d*.*$/variable mofDihedrals equal %d/' ./mof_screen.lammps
sed -i ''   -e 's/^variable mofImpropers equal \d*.*$/variable mofImpropers equal %d/' ./mof_screen.lammps
""" % tuple(num_types)
        f.write(modify_lammps_script)

    # smit code always outputs lammps data file with name: data.{mof_name}
    data_filename = "data.%s" % mof_name

    ### GENERATE MOF XYZ FILE FROM LAMMPS DATA FILE
    mof_xyz_filename = "%s.xyz" % mof_name
    subprocess.run("lmp_data_to_xyz.py %s > %s" % (data_filename, mof_xyz_filename), shell=True, check=True)

    ### GENERATE PACKMOL SCRIPT TO PACK MOF WITH N MOLECULES
    packmol_filename = "packmol_%s_%d_%s.txt" % (mof_name, num_molecules, molecule_name)
    packed_xyz_filename = "mof_w_molecules.xyz"
    with open(data_filename, 'r') as f:
        packmol_script, box_dims = pack_molecules_into_mof(f, mof_name, molecule_name, packed_xyz_filename, num_molecules)
    with open(packmol_filename, 'w') as f:
        f.write(packmol_script)

    ### RUN PACKMOLE TO PACK MOLECULES INTO MOF
    subprocess.run("packmol < %s" % (packmol_filename), shell=True, check=True)

    ### EXTRACT MOLECULE POSITIONS FROM PACKMOLE OUTPUT AND CREATE LAMMPS DATA FILE
    with open(packed_xyz_filename, 'r') as f:
        f.readline()
        f.readline()
        xyz_data = []
        for row in f:
            row_list = row.strip().split()
            if int(row_list[0]) > 100:
                row_list[0] = str(int(row_list[0]) - 100)
                xyz_data.append(row_list)

        charges = [-0.35,0.7,-0.35]
        masses = [15.999, 12.011]
        rel_bonds = [(1,2),(2,3)]
        rel_angles = [(1,2,3)]
        molecule_lammps_data_file = packmol_to_lammps(xyz_data, charges, masses, 3, rel_bonds, rel_angles, box_dims[0:2], box_dims[2:4], box_dims[4:6])
        with open(datafile_path, 'w') as wf:
            wf.write(molecule_lammps_data_file)


def cmdline():
    parser = argparse.ArgumentParser("./gen_mof_flex_ff_rigid_molecule_lammps_config.py")
    parser.add_argument('molecule_path', help="Path to molecule XYZ")
    parser.add_argument('mof_path', help="Path to MOF CIF with P1 symmetry")
    parser.add_argument('output_file', help="Path to output file")
    parser.add_argument('--minimum-box-dimension', '-d', default=12.5, help="minimum box dimension (angstroms) of extended unit cell")
    parser.add_argument('--num-molecules', '-n', default=1, help="number of molecules to pack into MOF")
    args = parser.parse_args()

    gen_mof_flex_ff_rigid_molecule_lammps_config(args.molecule_path, args.mof_path, args.output_file,
        minimum_box_dimension=args.minimum_box_dimension,
        num_molecules=int(args.num_molecules)
    )
