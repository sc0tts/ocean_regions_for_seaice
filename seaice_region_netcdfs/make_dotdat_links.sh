#!/bin/bash

# make_dotdat_links.sh

# Create subdirs and symbolic links for raw .dat files

for proj in psn pss e2n e2s; do
  dat_dir=./${proj}_fields
  mkdir -p ${dat_dir}

  cd ${dat_dir}
  for fn in ../../seaice_regions_?h*_${proj}*.dat; do
    ln -s "$fn" .
  done

  cd ..
done
