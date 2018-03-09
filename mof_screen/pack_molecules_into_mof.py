import argparse
import os
import re
import sys

def pack_molecules_into_mof(lammps_data_file, mof_name, gas_path, output_name, num_molecules):

    found_x = False; found_y = False; found_z = False
    for line in lammps_data_file:
        print(line)
        if re.match(r"^.+ xlo xhi", line, re.IGNORECASE):
            xlo, xhi, _, _ = line.strip().split()
            xlo = float(xlo); xhi = float(xhi)
            found_x = True
        if re.match(r"^.+ ylo yhi", line, re.IGNORECASE):
            ylo, yhi, _, _ = line.strip().split()
            ylo = float(ylo); yhi = float(yhi)
            found_y = True
        if re.match(r"^.+ zlo zhi", line, re.IGNORECASE):
            zlo, zhi, _, _ = line.strip().split()
            zlo = float(zlo); zhi = float(zhi)
            found_z = True

        if found_x and found_y and found_z:
            break

    if not (found_x and found_y and found_z):
        print("Could not find xlo/xhi ylo/yhi zlo/zhi in file!")
        sys.exit(1)

    s = """
    tolerance 2.0

    output %s
    filetype xyz

    structure %s.xyz
      number 1
      fixed 0 0 0 0 0 0
    end structure

    structure %s
      number %d
      inside box %10.5f %10.5f %10.5f %10.5f %10.5f %10.5f
    end structure
    """ % (output_name, mof_name, gas_path, num_molecules, xlo, ylo, zlo, zhi, yhi, zhi)

    return s, (xlo, xhi, ylo, yhi, zlo, zhi)


def cmdline():
    parser = argparse.ArgumentParser("./pack_co2s_into_mof.py")
    parser.add_argument('filename', help="Path to LAMMPS log output file")
    args = parser.parse_args()

    _, mof_name = os.path.splitext(args.filename)

    with open(args.filename, 'r') as f:
        packmol = pack_molecule_into_mof(f)
