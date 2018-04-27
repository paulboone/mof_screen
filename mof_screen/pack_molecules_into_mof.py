import argparse
import os
import re
import sys

from angstrom.molecule import Cell
from angstrom.geometry import Plane

def pack_molecules_into_mof(mof_name, gas_path, output_name, num_molecules, tolerance, supercell):

    cell = Cell(supercell)
    cell.calculate_vertices()
    pts = cell.vertices


    # would typically use vertices of (0,1,3), (2,4,5), (0,3,2), (1,6,4), (0,1,2), (3,5,6)
    # but only need the second in each pair because the planes are parallel. Since the first plane
    # will always have d = 0, we only need the second plane to define the triclinic bounds.
    # We can then bound the box using each plane twice, one where the plane > 0 and one where
    # the plane < d. Since we are normalizing the plane coefficients so that d is equal to the
    # appropriate unit cell lengths, d should be in units of angstroms. We can then add a tolerance
    # by just using plane > 1 or plane < d - 1 (for a one angstrom tolerance).


    plane_coefficients = []

    p = Plane(pts[2], pts[4], pts[5])
    n = p.d / cell.b # normalize by length of b
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + tolerance, a, b, c, d - tolerance]

    p = Plane(pts[1], pts[6], pts[4])
    n = p.d / cell.a # normalize by length of a
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + tolerance, a, b, c, d - tolerance]

    p = Plane(pts[3], pts[5], pts[6])
    n = p.d / cell.c # normalize by length of c
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + tolerance, a, b, c, d - tolerance]

    s = """
    tolerance %10.5f

    output %s
    filetype xyz

    structure %s.xyz
      number 1
      fixed 0 0 0 0 0 0
    end structure

    structure %s
      number %d

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f
    end structure
    """ % (tolerance, output_name, mof_name, gas_path, num_molecules, *plane_coefficients)

    return s


def cmdline():
    parser = argparse.ArgumentParser("./pack_co2s_into_mof.py")
    parser.add_argument('filename', help="Path to LAMMPS log output file")
    args = parser.parse_args()

    _, mof_name = os.path.splitext(args.filename)

    with open(args.filename, 'r') as f:
        packmol = pack_molecule_into_mof(f)
