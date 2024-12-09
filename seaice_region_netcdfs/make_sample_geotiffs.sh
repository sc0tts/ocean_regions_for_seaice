#!/bin/bash

# make_sample_geotiffs.sh

# Create geotiffs from 25km .dat files make by make_dotdat_links.sh

fn_dat=./e2n_fields/seaice_regions_nh_e2n25.dat
fn_pgm=./seaice_regions_e2n25.pgm
fn_nc=./seaice_regions_e2n25.nc
xdim=720
ydim=720
convert -extract ${xdim}x${ydim} -size ${xdim}x${ydim} -depth 8 gray:${fn_dat} ${fn_pgm}
gdal_translate -q -of netcdf -a_srs epsg:6931 -a_ullr -9000000 9000000 9000000 -9000000 -a_nodata 255 ${fn_pgm} ${fn_nc}
rm -v ${fn_pgm}
ncdump -h ${fn_nc} > ${fn_nc}.txt


fn_dat=./psn_fields/seaice_regions_nh_psn25.dat
fn_pgm=./seaice_regions_psn25.pgm
fn_nc=./seaice_regions_psn25.nc
xdim=304
ydim=448
convert -extract ${xdim}x${ydim} -size ${xdim}x${ydim} -depth 8 gray:${fn_dat} ${fn_pgm}
gdal_translate -q -of netcdf -a_srs epsg:3411 -a_ullr -3850000 5850000 3750000 -5350000 -a_nodata 255 ${fn_pgm} ${fn_nc}
rm -v ${fn_pgm}
ncdump -h ${fn_nc} > ${fn_nc}.txt


fn_dat=./e2s_fields/seaice_regions_sh_orig_e2s25.dat
fn_pgm=./seaice_regions_e2s25.pgm
fn_nc=./seaice_regions_e2s25.nc
xdim=720
ydim=720
convert -extract ${xdim}x${ydim} -size ${xdim}x${ydim} -depth 8 gray:${fn_dat} ${fn_pgm}
gdal_translate -q -of netcdf -a_srs epsg:6932 -a_ullr -9000000 9000000 9000000 -9000000 -a_nodata 255 ${fn_pgm} ${fn_nc}
rm -v ${fn_pgm}
ncdump -h ${fn_nc} > ${fn_nc}.txt

fn_dat=./pss_fields/seaice_regions_sh_orig_pss25.dat
fn_pgm=./seaice_regions_pss25.pgm
fn_nc=./seaice_regions_pss25.nc
xdim=316
ydim=332
convert -extract ${xdim}x${ydim} -size ${xdim}x${ydim} -depth 8 gray:${fn_dat} ${fn_pgm}
gdal_translate -q -of netcdf -a_srs epsg:3412 -a_ullr -3950000 4350000 3950000 -3950000 -a_nodata 255 ${fn_pgm} ${fn_nc}
rm -v ${fn_pgm}
ncdump -h ${fn_nc} > ${fn_nc}.txt

