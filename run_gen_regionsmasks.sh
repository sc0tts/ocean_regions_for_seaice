#!/bin/bash
set -e  # Quit upon any script errors

# run_gen_regionsmasks.sh

suffix=$1
if [ -z $suffix ]; then
  echo "Usage: ./$0 <suffix>"
  echo "  Eg:  ./$0 nh"
  echo "  or:  ./$0 sh_orig"
  echo "  or:  ./$0 sh_RH"
  exit 1
fi

if [[ "$suffix" == *"nh"* ]]; then
  h=n
elif [[ "$suffix" == *"sh"* ]]; then
  h=s
fi

for projid in ps${h} e2${h}; do
  for res in 25 12.5 6.25 3.125; do
    ./gen_regionsmask.sh seaice_regions_${suffix}.shp ${projid}${res}
  done
done

echo "Finished $0"

<<SKIP_NH
for projid in pss e2s; do
  for res in 25 12.5 6.25 3.125; do
    ./gen_regionsmask.sh seaice_regions_nh.shp ${projid}${res}
  done
done
SKIP_NH

<<SKIP_SH_ORIG
for projid in pss e2s; do
  for res in 25 12.5 6.25 3.125; do
    ./gen_regionsmask.sh seaice_regions_sh_orig.shp ${projid}${res}
  done
done
SKIP_SH_ORIG

<<SKIP_SH_RH
for projid in pss e2s; do
  for res in 25 12.5 6.25 3.125; do
    ./gen_regionsmask.sh seaice_regions_sh_RH.shp ${projid}${res}
  done
done
SKIP_SH_RH
