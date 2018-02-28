# MOF Screen Helper

## Installation Instructions

Prerequisites:
* install python3
* [install packmol](http://m3g.iqm.unicamp.br/packmol/userguide.shtml#comp) and make sure packmol
is in your path (i.e. added to the PATH environment variable).


Then:

```
# this is to override the lammps_interface unversioned setup.py
pip install "networkx == 1.11"

pip install -r requirements.txt
pip install ./
```

## Usage:

```
gen_mof_flex_ff_rigid_molecule_lammps_config --help
```
