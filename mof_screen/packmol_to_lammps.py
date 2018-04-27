import sys

def packmol_to_lammps(xyz_data, charges, masses, atoms_per_molecule, relative_bonds, relative_angles):
    """
    Takes successive molecules, i.e. groups of atoms_per_molecule atoms from the XYZ data...
    Then for each atom in a molecule, create a tuple consisting of:
    - atom number
    - molecule number
    - atom type
    - charge
    - coords x,y,z
    """
    atoms = []
    bonds = []
    angles = []

    atom_num = 1
    bond_num = 1
    angle_num = 1

    num_bond_types = len(set([b[0] for b in relative_bonds]))
    num_angle_types = len(set([b[0] for b in relative_angles]))

    if len(xyz_data) % atoms_per_molecule:
        print("WARNING: number of atoms is not evenly divisible by the atoms per molecule!")
    num_molecules = len(xyz_data) // atoms_per_molecule


    for molecule_num in range(1, num_molecules + 1):
        starting_atom_num = atom_num
        molecule = xyz_data[(molecule_num - 1) * atoms_per_molecule:molecule_num * atoms_per_molecule]

        for i, atom in enumerate(molecule):
            atom_type, x, y, z = atom
            atom_tuple = (str(atom_num), str(molecule_num), atom_type, str(charges[i]), x, y, z)
            atoms += [" ".join(atom_tuple)]
            atom_num += 1

        for bond in relative_bonds:
            bond_type, atom1, atom2 = bond
            atom1 = starting_atom_num + atom1 - 1
            atom2 = starting_atom_num + atom2 - 1
            bond_tuple = (str(bond_num), str(bond_type), str(atom1), str(atom2))
            bonds += [" ".join(bond_tuple)]
            bond_num += 1

        for angle in relative_angles:
            angle_type, atom1, atom2, atom3 = angle
            atom1 = starting_atom_num + atom1 - 1
            atom2 = starting_atom_num + atom2 - 1
            atom3 = starting_atom_num + atom3 - 1
            angle_tuple = (str(angle_num), str(angle_type), str(atom1), str(atom2), str(atom3))
            angles += [" ".join(angle_tuple)]
            angle_num += 1


    return generate_lammps_data_file(masses, atoms, bonds, angles, num_bond_types, num_angle_types)

def generate_lammps_data_file(masses, atoms, bonds, angles, num_bond_types, num_angle_types):
    """
    Generates a LAMMPS data file from the passed geometry information. This data file is not complete
    and is expected to be loaded after another data file which defines the box boundaries, etc.
    """
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
%d bond types
%d angle types
0 dihedral types
0 improper types
""" % (len(masses), num_bond_types, num_angle_types)


    s += "\n\n Masses\n\n" + "\n".join(mass_lines)
    s += "\n\n Atoms\n\n" + "\n".join(atoms)
    if bonds:
        s += "\n\n Bonds\n\n" + "\n".join(bonds)
    if angles:
        s += "\n\n Angles\n\n" + "\n".join(angles)

    return s
