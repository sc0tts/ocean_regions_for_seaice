#!/bin/bash

# gen_all_ncs.sh

# generate netCDF iles for all grid/res combinations

for proj in psn pss e2n e2s; do
  for res in 25 12.5 6.25 3.125; do
    python create_seaice_region_netcdfs.py ${proj}${res}
  done
done
