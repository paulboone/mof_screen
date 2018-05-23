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

## Examples:

One-off:

```
cd examples/CO2_IRMOF-1/
gen_mof_flex_ff_rigid_molecule_lammps_config IRMOF-1.cif CO2 -n 10
cp ../../mof_screen_co2.lammps ./ && bash modify_lammps.sh ./mof_screen_co2.lammps
lmp_serial < mof_screen_co2.lammps
```

Or to generate a batch of config files:

* make sure you have a directory called 'core-mof-1.0-ddec' with the actual ddec mofs in it.
* create a directory in this dir
* edit mofs.txt to contain the mofs you want to test and the # of CO2s per mof
* from the directory, run `../generate_configs.sh < ../mofs.txt`

## example seds for converting XYZ atom indices to atom strings

```
# ATOTIM + CO2:
sed 's/^1/V/g;s/^2/H/g;s/^3/C/g;s/^4/O/g;s/^5/O/g;s/^6/C/g' ./npt-eq.dump.0.xyz

# FIQCEN (HKUST-1) + CO2:
sed 's/^1/Cu/g;s/^2/H/g;s/^3/C/g;s/^4/O/g;s/^5/O/g;s/^6/C/g' ./npt-eq.dump.0.xyz

# EDUSIF(IRMOF-1) + CO2:
sed 's/^1/O/g;s/^2/C/g;s/^3/H/g;s/^4/Zn/g;s/^5/O/g;s/^6/O/g;s/^7/C/g' ./npt-eq.dump.0.xyz

# UGEPEB + CO2:
sed 's/^1/Cu/g;s/^2/H/g;s/^3/C/g;s/^4/N/g;s/^5/O/g;s/^6/O/g;s/^7/O/g;s/^8/C/g' ./npt-eq.dump.0.xyz

# VONBUW + CO2:
sed 's/^1/Zn/g;s/^2/H/g;s/^3/C/g;s/^4/C/g;s/^5/N/g;s/^6/O/g;s/^7/O/g;s/^8/O/g;s/^9/C/g' ./npt-eq.dump.0.xyz

# ZIF-8 + CO2:
sed 's/^1/Zn/g;s/^2/H/g;s/^3/C/g;s/^4/C/g;s/^5/N/g;s/^6/O/g;s/^7/C/g' ./npt-eq.dump.0.xyz
```
