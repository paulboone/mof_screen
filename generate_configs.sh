#!/usr/bin/env bash
# usage: generate_configs.sh < mofs.txt
# where mofs.txt contains a list of mof_name (in the core database) and number of mofs to use
# i.e:
# ZIF-8 19
# UGEPEB01 10
# VONBUW 10
# ...etc...
#
# currently directories are hardcoded, so create a directory in this directory, cd into it, and
# run this command from there.

set -e

while IFS='$\n' read -r line; do
  mof=${line% *}
  num=${line#* }

  mkdir -p $mof
  cd $mof
  if [ -e ../../core-mof-1.0-ddec/${mof}.cif ]; then
    echo "${mof}.cif"
    cp ../../core-mof-1.0-ddec/${mof}.cif ./$mof.cif
  else
    echo "$(cd ../../core-mof-1.0-ddec/ && ls -1 ${mof}_*.cif)"
    cp ../../core-mof-1.0-ddec/${mof}_*.cif ./$mof.cif
  fi;

  gen_mof_flex_ff_rigid_molecule_lammps_config ./$mof.cif CO2 -n $num > gen_config.log
  mv gen_config.log ./tmp
  cp ../../mof_screen_co2.lammps ./ && bash modify_lammps.sh ./mof_screen_co2.lammps
  sed -e "s|^#SBATCH --job-name=*.*$|#SBATCH --job-name=$mof|" ../../screen.slurm > screen.slurm

  cd ..
done
