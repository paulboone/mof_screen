
#gen-mof-flex-ff-rigid-molecule-lammps-config.py <molecule> <mof(s)>
# —minimum-box-dimension=<size> default ?
#—num-molecules=<num> default 1

import argparse
import os
import math
import pkg_resources
import random
import sys
import subprocess

from mof_screen.lammps_interface_wrappers import Parameters, cif_to_ff_lammps_data
from mof_screen import pack_molecules_into_mof
from mof_screen import packmol_to_lammps

def gen_mof_flex_ff_rigid_molecule_lammps_config(mof_path, gas_name, minimum_box_dimension=12.5, molecules_per_unit_cell=1):
    mof_name, _ = os.path.splitext(os.path.basename(mof_path))

    params = Parameters(mof_path)
    params.cutoff = minimum_box_dimension
    params.force_field = "UFF4MOF"

    ### GENERATE LAMMPS DATA FILE FOR MOF WITH FORCE_FIELD PARAMS
    num_types, supercell_params, supercell, atom_types = cif_to_ff_lammps_data(params)
    num_unitcells = supercell[0]*supercell[1]*supercell[2]
    num_molecules = math.floor(molecules_per_unit_cell * num_unitcells)
    atom_types_string = " ".join(atom_types)
    print("supercell, num_unitcells, molecules_per_unit_cell: ", supercell, num_unitcells, molecules_per_unit_cell)
    print("num_molecules: ", num_molecules)


    # smit code always outputs lammps data file with name: data.{mof_name}; move this
    mof_lammps_data_file = "%s.data" % mof_name
    os.rename("data.%s" % mof_name, mof_lammps_data_file)

    os.makedirs("tmp", exist_ok=True)
    os.rename("in.%s" % mof_name, "tmp/in.%s" % mof_name)

    if gas_name is None:
        ### output LAMMPS modification script
        with open("modify_lammps.sh", 'w') as f:
            random_seed = random.randint(0, 999999999)
            modify_lammps_script = """#!/bin/bash
if [ -z "$1" ]; then echo "USAGE: ./modify_lammps.sh <config.lammps>" && exit 1; fi
sed -iorig -e 's|^variable frameworkDataFile string .*$|variable frameworkDataFile string %s|' $1
sed -i -e 's|^variable randomSeed equal \d*.*$|variable randomSeed equal %d|' $1
sed -i -e 's|^dump_modify \([a-zA-Z0-9]*\) element .*$|dump_modify \\1 element %s|' $1
""" % tuple([mof_lammps_data_file, random_seed, atom_types_string])
            f.write(modify_lammps_script)
        return

    if gas_name == "CO2":
        gas_lammps_data_file = "CO2.data"
        charges = [-0.35, 0.7, -0.35]
        masses = [15.999, 12.011]
        rel_bonds = [(1,1,2),(1,2,3)]
        rel_angles = [(1,1,2,3)]
    elif gas_name == "N2":
        gas_lammps_data_file = "N2.data"
        charges = [0.0, 0.0]
        masses = [14.007]
        rel_bonds = [(1,1,2)]
        rel_angles = []
    elif gas_name == "N2pc":
        gas_lammps_data_file = "N2pc.data"
        charges = [-0.482, 0.964, -0.482]
        masses = [14.007, 1e-10]
        rel_bonds = [(1,1,3), (2,1,2), (2,2,3)]
        rel_angles = []
    else:
        print("Please only use CO2 / N2 / N2pc")
        os.exit(1)

    gas_path = pkg_resources.resource_filename(__name__, "%s.xyz" % gas_name)

    ### output LAMMPS modification script
    with open("modify_lammps.sh", 'w') as f:
        random_seed = random.randint(0, 999999999)
        modify_lammps_script = """#!/bin/bash
if [ -z "$1" ]; then echo "USAGE: ./modify_lammps.sh <config.lammps>" && exit 1; fi
sed -i orig -e 's|^variable frameworkDataFile string .*$|variable frameworkDataFile string %s|' $1
sed -i ''   -e 's|^variable gasDataFile string .*$|variable gasDataFile string %s|' $1
sed -i ''   -e 's|^variable mofAtoms equal \d*.*$|variable mofAtoms equal %d|' $1
sed -i ''   -e 's|^variable mofBonds equal \d*.*$|variable mofBonds equal %d|' $1
sed -i ''   -e 's|^variable mofAngles equal \d*.*$|variable mofAngles equal %d|' $1
sed -i ''   -e 's|^variable mofDihedrals equal \d*.*$|variable mofDihedrals equal %d|' $1
sed -i ''   -e 's|^variable mofImpropers equal \d*.*$|variable mofImpropers equal %d|' $1
sed -i ''   -e 's|^variable randomSeed equal \d*.*$|variable randomSeed equal %d|' $1
""" % tuple([mof_lammps_data_file, gas_lammps_data_file] + num_types + [random_seed])
        f.write(modify_lammps_script)


    ### GENERATE MOF XYZ FILE FROM LAMMPS DATA FILE
    mof_xyz_filename = "%s.xyz" % mof_name
    subprocess.run("lmp_data_to_xyz.py %s > %s" % (mof_lammps_data_file, mof_xyz_filename), shell=True, check=True)

    ### GENERATE PACKMOL SCRIPT TO PACK MOF WITH N MOLECULES
    packmol_filename = "%s_%d_%s.packmol.txt" % (mof_name, num_molecules, gas_name)
    packed_xyz_filename = "mof_w_molecules.xyz"
    packmol_script = pack_molecules_into_mof(mof_name, gas_path, packed_xyz_filename,
                                    num_molecules, 4.0, 2.0, supercell_params)
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

        atoms_per_molecule = len(charges)
        molecule_lammps_data_file_contents = packmol_to_lammps(xyz_data, charges, masses, atoms_per_molecule, rel_bonds, rel_angles)
        with open(gas_lammps_data_file, 'w') as wf:
            wf.write(molecule_lammps_data_file_contents)

    # archive files not needed to run simulation
    os.rename(packed_xyz_filename, "tmp/%s" % packed_xyz_filename)
    os.rename(mof_xyz_filename, "tmp/%s" % mof_xyz_filename)
    os.rename(packmol_filename, "tmp/%s" % packmol_filename)


def cmdline():
    parser = argparse.ArgumentParser("./gen_mof_flex_ff_rigid_molecule_lammps_config.py")
    parser.add_argument('mof_path', help="Path to MOF CIF with P1 symmetry")
    parser.add_argument('--gas_name', help="name of gas: CO2/N2/N2pc")
    parser.add_argument('--minimum-box-dimension', '-d', default=12.5, help="minimum box dimension (angstroms) of extended unit cell")
    parser.add_argument('--molecules-per-unit-cell', '-n', default=1.0, help="number of molecules per unit cell to pack into MOF")
    args = parser.parse_args()

    gen_mof_flex_ff_rigid_molecule_lammps_config(args.mof_path, args.gas_name,
        minimum_box_dimension=args.minimum_box_dimension,
        molecules_per_unit_cell=float(args.molecules_per_unit_cell)
    )
