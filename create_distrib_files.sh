#!/bin/bash

# create_distrib_file.sh

# move and rename the non-netCDF files for distribution

thisdir="$PWD"

distrib_basedir=nsidc0780_files
distrib_dir=${thisdir}/${distrib_basedir}
mkdir -p ${distrib_dir}

nh_shp_basedir=NSIDC-0780_SeaIceRegions_NH_v1.0
shnasa_shp_basedir=NSIDC-0780_SeaIceRegions_SH-NASA_v1.0
shrh_shp_basedir=NSIDC-0780_SeaIceRegions_SH-RH_v1.0

nh_shp_dir=${distrib_dir}/${nh_shp_basedir}
shnasa_shp_dir=${distrib_dir}/${shnasa_shp_basedir}
shrh_shp_dir=${distrib_dir}/${shrh_shp_basedir}

# Copy and rename .txt and .csv files
cp -av seaice_regions_nh.txt ${distrib_dir}/NSIDC-0780_SeaIceRegions_NH_v1.0.txt
cp -av seaice_regions_nh.csv ${distrib_dir}/NSIDC-0780_SeaIceRegions_NH_v1.0.csv

cp -av intermed/seaice_regions_sh_orig.txt ${distrib_dir}/NSIDC-0780_SeaIceRegions_SH-NASA_v1.0.txt
cp -av intermed/seaice_regions_sh_orig.csv ${distrib_dir}/NSIDC-0780_SeaIceRegions_SH-NASA_v1.0.csv

cp -av intermed/seaice_regions_sh_RH.txt ${distrib_dir}/NSIDC-0780_SeaIceRegions_SH-RH_v1.0.txt
cp -av intermed/seaice_regions_sh_RH.csv ${distrib_dir}/NSIDC-0780_SeaIceRegions_SH-RH_v1.0.csv


# Create Shapefile subdirectories and .zip file

# NH
mkdir -p ${nh_shp_dir}
for ext in cpg dbf prj shp shx; do
  cp -av seaice_regions_nh.${ext} ${nh_shp_dir}/${nh_shp_basedir}.${ext}
done
cd ${nh_shp_dir}
zip -r ${nh_shp_basedir}.zip ./*.{cpg,dbf,prj,shp,shx}
mv ${nh_shp_basedir}.zip ${distrib_dir}/
cd ${thisdir}

# SH-NASA
mkdir -p ${shnasa_shp_dir}
for ext in cpg dbf prj shp shx; do
  cp -av intermed/seaice_regions_sh_orig.${ext} ${shnasa_shp_dir}/${shnasa_shp_basedir}.${ext}
done
cd ${shnasa_shp_dir}
zip -r ${shnasa_shp_basedir}.zip ./*.{cpg,dbf,prj,shp,shx}
mv ${shnasa_shp_basedir}.zip ${distrib_dir}/
cd ${thisdir}

# SH-RH
mkdir -p ${shrh_shp_dir}
for ext in cpg dbf prj shp shx; do
  cp -av intermed/seaice_regions_sh_RH.${ext} ${shrh_shp_dir}/${shrh_shp_basedir}.${ext}
done
cd ${shrh_shp_dir}
zip -r ${shrh_shp_basedir}.zip ./*.{cpg,dbf,prj,shp,shx}
mv ${shrh_shp_basedir}.zip ${distrib_dir}/
cd ${thisdir}

echo "Finished with $0"
