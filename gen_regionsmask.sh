#!/bin/bash

set -e

# gen_arctic_regions_psn12.5.sh <grid_name>

# Usage:
#  ./gen_arctic_regions_psn12.5.sh <shp_latlon_fn> psn25
# eg
#  ./gen_arctic_regions_psn12.5.sh regions_20211003 psn25

# shp_latlon_fn is the shapefile of the regions in latlon projection (epsg 4326)

# latlon_res=0.05       # latlon resolution, in degrees
latlon_res=0.01       # latlon resolution, in degrees
attrname=Sea_ID  # name of the attribute to 'rasterize' from the shapefile

# Check for a cmdline argument
if [ -z "$1" ]; then
  echo "Usage: ./gen_arctic_regions_.sh <shp_latlon_fn> <grid_name>"
  exit
fi

# Check that input file is a shapefile
if [[ ! $1 == *".shp" ]]; then
  echo "Input fname must be shapefile: $1"
  exit
fi

shp_latlon_fn=$1
echo "shpfname:  ${shp_latlon_fn}"

# the 'layername' is the basename of the shapefile
layername=${shp_latlon_fn/%.shp}
echo "layername: ${layername}"

# Parse the grid_name
grid_name="$2"
if [ -z "$grid_name" ]; then
  echo "No grid_name given"
  echo " Usage:"
  echo "   ./gen_arctic_regions.sh <shp_latlon_fn> <grid_name>"
  echo " eg"
  echo "   ./gen_arctic_regions_.sh seaice_regions_nh.shp psn25"
  exit
fi

# Parse grid_name for projid and gridres
projid=${grid_name:0:3}
gridres=${grid_name#"$projid"}
if [ "$projid" == "psn" ]; then
  echo "projid: ${projid}"
  hem=nh
  epsgcode=3411
  t_left=-3850000
  t_right=3750000
  t_top=5850000
  t_bottom=-5350000
  lat_min=30
  lat_max=90
elif [ "$projid" == "pss" ]; then
  echo "projid: ${projid}"
  hem=sh
  epsgcode=3412
  t_left=-3950000
  t_right=3950000
  t_top=4350000
  t_bottom=-3950000
  lat_min=-90
  lat_max=-30
elif [ "$projid" == "e2n" ]; then
  echo "projid: ${projid}"
  hem=nh
  epsgcode=6931
  t_left=-9000000
  t_right=9000000
  t_top=9000000
  t_bottom=-9000000
  lat_min=30
  lat_max=90
elif [ "$projid" == "e2s" ]; then
  echo "projid: ${projid}"
  hem=sh
  epsgcode=6932
  t_left=-9000000
  t_right=9000000
  t_top=9000000
  t_bottom=-9000000
  lat_min=-90
  lat_max=-30
else
  echo "projid not recognized: ${projid}"
  exit 1
fi

# Note:
#   gridres is a string, e.g. "25" or "3.125"
#   grid_res is an integer, e.g.  25000 or 3125
if [ "$gridres" == "25" ]; then
  grid_res=25000
elif [ "$gridres" == "12.5" ]; then
  grid_res=12500
elif [ "$gridres" == "6.25" ]; then
  grid_res=6250
elif [ "$gridres" == "3.125" ]; then
  grid_res=3125
else
  echo "Grid_res not recognized: ${gridres}"
  exit
fi

echo "Creating grid for:"
echo "  grid_name: ${grid_name}"
echo "  projid:    ${projid}"
echo "  grid_res:  ${grid_res}"

# We will create netCDF versions of the translated data
#  Note: we could also create tif versions if we wanted to
nc_latlon_fn=./${layername}.nc

# Rasterize the LatLon region map into 1/10th degree grid
if [ ! -f ${nc_latlon_fn} ]; then
  echo "Creating netCDF latlon version of translated data: ${nc_latlon_fn}"
  gdal_rasterize -tr $latlon_res $latlon_res -te -180 ${lat_min} 180 ${lat_max} -ot Byte -a ${attrname} -l ${layername} ${shp_latlon_fn} ${nc_latlon_fn}
else
  echo "Using existing: ${nc_latlon_fn}"
fi

# Now, create four quadrants of the North polar projection
# Note: we can't do this initially because gdal can't handle polar projections

# Arctic
# Create four quadrants that can be patched together into one
nc_reproj_basename=./${layername}_${grid_name}
nc_reproj_UL=${nc_reproj_basename}_UL.nc
nc_reproj_UR=${nc_reproj_basename}_UR.nc
nc_reproj_LR=${nc_reproj_basename}_LR.nc
nc_reproj_LL=${nc_reproj_basename}_LL.nc

echo "UL fn: ${nc_reproj_UL}"

# For PSN
# Overall target extents for NH Polar Stereo grid are:
#   -te -3850000 -5350000 3750000 5850000

# UL extents are: left 0 0 top
gdalwarp -of netcdf -t_srs EPSG:${epsgcode} -tr ${grid_res} ${grid_res} -te $t_left 0 0 $t_top -overwrite -dstnodata 0 -r near ${nc_latlon_fn} ${nc_reproj_UL}

# UR extents are: 0 0 right top
gdalwarp -of netcdf -t_srs EPSG:${epsgcode} -tr ${grid_res} ${grid_res} -te 0 0 $t_right $t_top -overwrite -dstnodata 0 -r near ${nc_latlon_fn} ${nc_reproj_UR}

# LR extents are: 0 bottom right 0
gdalwarp -of netcdf -t_srs EPSG:${epsgcode} -tr ${grid_res} ${grid_res} -te 0 $t_bottom $t_right 0 -overwrite -dstnodata 0 -r near ${nc_latlon_fn} ${nc_reproj_LR}

# LL extents are: left bottom 0 0
gdalwarp -of netcdf -t_srs EPSG:${epsgcode} -tr ${grid_res} ${grid_res} -te $t_left $t_bottom 0 0 -overwrite -dstnodata 0 -r near ${nc_latlon_fn} ${nc_reproj_LL}

# Stitch together the four quadrants into one, using Python
# Note: the python code assumes the quadrants are:
#   netCDF files
#   with the same basename
#   and extensions of UL UR LR LL
echo "Calling stitch_quads.py with: ${nc_reproj_basename} ${grid_name}"
python stitch_quads.py ${nc_reproj_basename} ${grid_name}

# Remove temporary files after stitching them together
# rm temp_[LU][LR].dat

# Overwrite with land values
# stiched_dat_fn=${nc_reproj_basename}.dat
# stiched_dat_fn=${nc_reproj_basename}_${grid_name}.dat
stiched_dat_fn=${nc_reproj_basename}.dat
withland_fn=${nc_reproj_basename}_withland.dat
echo "python add_landmask.py ${grid_name} ${stiched_dat_fn} ${withland_fn}"
python add_landmask.py ${grid_name} ${stiched_dat_fn} ${withland_fn}
