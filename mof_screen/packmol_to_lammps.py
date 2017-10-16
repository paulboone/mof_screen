import sys

3
[[0,1],[1,2]]
[0,1,2]

def packmol_to_lammps(xyz_data, charges, masses, atoms_per_molecule, relative_bonds, relative_angles, xb, yb, zb):
    bond_type = 1
    angle_type = 1

    atoms = []
    bonds = []
    angles = []

    atom_num = 1
    bond_num = 1
    angle_num = 1
    if len(xyz_data) % atoms_per_molecule:
        print("WARNING: number of atoms is not evenly divisible by the atoms per molecule!")
    num_molecules = len(xyz_data) // atoms_per_molecule


    for molecule_num in range(1, num_molecules + 1):
        starting_atom_num = atom_num
        molecule = xyz_data[(molecule_num - 1) * atoms_per_molecule:molecule_num * atoms_per_molecule]
        print(xyz_data, molecule)
        for i, atom in enumerate(molecule):
            print(i,atom)
            atom_id, x, y, z = atom
            atom_tuple = (str(atom_num), str(molecule_num), atom_id, str(charges[i]), x, y, z)
            atoms += [" ".join(atom_tuple)]
            atom_num += 1

        for bond in relative_bonds:
            abs_bond = [str(starting_atom_num + i - 1) for i in bond]
            bond_tuple = (str(bond_num), str(bond_type), *abs_bond)
            bonds += [" ".join(bond_tuple)]
            bond_num += 1

        for angle in relative_angles:
            abs_angle = [str(starting_atom_num + i - 1) for i in angle]
            angle_tuple = (str(angle_num), str(angle_type), *abs_angle)
            angles += [" ".join(angle_tuple)]
            angle_num += 1

    mass_lines = [" ".join([str(i + 1),str(t)]) for i, t in enumerate(masses)]

    s = ""
    s += "# lammps data file generated from mof_screen/packmol_to_lammps.py\n"
    s += "%s atoms\n" % len(atoms)
    s += "%s bonds\n" % len(bonds)
    s += "%s angles" % len(angles)
    s += """
0 dihedrals
0 impropers
%d atom types
1 bond types
1 angle types
0 dihedral types
0 improper types
""" % len(masses)

    s += "%.5f %10.5f xlo xhi\n" % xb
    s += "%.5f %10.5f ylo yhi\n" % yb
    s += "%.5f %10.5f zlo zhi\n" % zb

    s += "\n\n Masses\n\n" + "\n".join(mass_lines)
    s += "\n\n Atoms\n\n" + "\n".join(atoms)
    s += "\n\n Bonds\n\n" + "\n".join(bonds)
    s += "\n\n Angles\n\n" + "\n".join(angles)

    return s
