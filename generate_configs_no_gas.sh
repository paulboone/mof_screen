#!/usr/bin/env bash
# usage: generate_configs.sh mofs.txt 1
# where mofs.txt contains a list of mof_name (in the core database) and number of mofs to use
# i.e:
# ZIF-8 19
# UGEPEB01 10
# VONBUW 10
# ...etc...
#
# currently directories are hardcoded, so create a directory in this directory, cd into it, and
# run this command from there.
#
# To look at failures, run `grep -e ^Exception -e "^.*Error" */gen_config.log > fail_summary`
# from the fails directory.
#
filename=$1
num_per_mof=$2
exec 3<$filename
mkdir -p fails
while IFS='$\n' read -u 3 -r line; do
  mof=${line% *}
  num=${line#* }
  for i in `seq 1 ${num_per_mof}`; do
    mkdir -p $mof.$i
    cd $mof.$i
    if [ -e ../../core-mof-1.0-ddec/${mof}.cif ]; then
      results="${mof}.$i"
      cp ../../core-mof-1.0-ddec/${mof}.cif ./$mof.cif
    else
      results="${mof}.${i} (using $(cd ../../core-mof-1.0-ddec/ && ls -1 ${mof}_*.cif))"
      cp ../../core-mof-1.0-ddec/${mof}_*.cif ./$mof.cif
    fi;

    if gen_mof_flex_ff_rigid_molecule_lammps_config ./$mof.cif -n $num &> gen_config.log; then
      mv gen_config.log ./tmp
      cp ../../mof_screen_nogas.lammps ./ && bash modify_lammps.sh ./mof_screen_nogas.lammps
      sed -e "s|^#SBATCH --job-name=*.*$|#SBATCH --job-name=$mof.$i|" ../../screen.slurm > screen.slurm
      results="$results: OK"
      echo "$results"
      cd ..
    else
      results="$results: FAILED"
      echo "$results"
      cd ..
      mv $mof.$i ./fails/
      break
    fi

  done
done
