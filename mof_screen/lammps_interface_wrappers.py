from lammps_interface.lammps_main import LammpsSimulation
from lammps_interface.structure_data import from_CIF, write_CIF


class Parameters:
    def __init__(self, cif):
        # File options
        self.cif_file = cif
        self.output_cif = True
        self.output_raspa = False

        # Force field options
        self.force_field = 'UFF'
        self.mol_ff = None
        self.h_bonding = False
        self.dreid_bond_type = 'harmonic'
        self.fix_metal = False

        # Simulation options
        self.minimize = False
        self.bulk_moduli = False
        self.thermal_scaling = False
        self.npt = False
        self.nvt = False
        self.cutoff = 12.5
        self.replication = None
        self.orthogonalize = False
        self.random_vel = False
        self.dump_dcd = 0
        self.dump_xyz = 0
        self.dump_lammpstrj = 0
        self.restart = False

        # Parameter options
        self.tol = 0.4
        self.neighbour_size = 5
        self.iter_count = 10
        self.max_dev = 0.01
        self.temp = 298.0
        self.pressure = 1.0
        self.nprodstp = 200000
        self.neqstp = 200000

        # Molecule insertion options
        self.insert_molecule = ""
        self.deposit = 0

    def show(self):
        for v in vars(self):
            print('%-15s: %s' % (v, getattr(self, v)))

def cif_to_ff_lammps_data(params):
    sim = LammpsSimulation(params)
    sim.options.mol_ff = "UFF"
    cell, graph = from_CIF(params.cif_file)

    sim.set_cell(cell)
    supercell = sim.cell.minimum_supercell(sim.options.cutoff)

    sim.set_graph(graph)
    sim.split_graph()
    sim.assign_force_fields()
    sim.compute_simulation_size()
    sim.merge_graphs()
    if params.output_cif:
        print("CIF file requested...")
        write_CIF(graph, cell)

    sim.write_lammps_files()

    smit_atom_types = sim.unique_atom_types
    atom_types = [v[1]['element'] for k,v in smit_atom_types.items()]

    return [[len(sim.unique_atom_types), len(sim.unique_bond_types), len(sim.unique_angle_types),
            len(sim.unique_dihedral_types), len(sim.unique_improper_types)], sim.cell.get_params(), supercell, atom_types]
