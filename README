
Process for Generating Region masks

1) Generate CSV file of vertices for NH regions: 

   seaice_regions_nh.csv

   These vertices are essentially those in a prior .csv file:
       Region_vertices_definitions_updated_20211112_nh.csv 
   ...but with the Central Arctic region specifically identified as region 1

2) Create a .txt file from this .csv file:

   python csv_to_inittxt.py seaice_regions_nh.csv seaice_regions_nh.txt

3) Create shapefile(s) -- on the latlon grid -- from this .txt file

   python gen_shapefile.py seaice_regions_nh.txt seaice_regions_nh.shp

4) Create rasterized .nc file, and extract quadrants, stitch them togheter,
   and add a landmask

   Eg:
     ./gen_regionsmask.sh seaice_regions_nh.shp psn12.5
     ./gen_regionsmask.sh seaice_regions_nh.shp e2n12.5

   or run all with:
     ./run_gen_regionsmasks.sh

5) Create the .png files by running a macro in ImageJ:

   Open ImageJ
   Go to Plugins->Macros->Run...  and choose
     create_pngs_nh.ijm

-------------------

6) Try SH, "sh_orig" regions
  
   python csv_to_inittxt.py seaice_regions_sh_orig.csv seaice_regions_sh_orig.txt

7) Create shapefile(s)

   python gen_shapefile.py seaice_regions_sh_orig.txt seaice_regions_sh_orig.shp

8) Create rasterized .nc file, and extract quadrants, stitch them togheter,
   and add a landmask

   Eg:
     ./gen_regionsmask.sh seaice_regions_sh_orig.shp pss12.5
     ./gen_regionsmask.sh seaice_regions_sh_orig.shp e2s12.5

   or run all with:
     ./run_gen_regionsmasks.sh sh_orig

9) Create the .png files by running a macro in ImageJ:

   Open ImageJ
   Go to Plugins->Macros->Run...  and choose
     create_pngs_sh_orig.ijm

-------------------

10) Try SH, "sh_RH" regions
  
   python csv_to_inittxt.py seaice_regions_sh_RH.csv seaice_regions_sh_RH.txt

11) Create shapefile(s)

   python gen_shapefile.py seaice_regions_sh_RH.txt seaice_regions_sh_RH.shp

12) Create rasterized .nc file, and extract quadrants, stitch them togheter,
   and add a landmask

   Eg:
     ./gen_regionsmask.sh seaice_regions_sh_RH.shp pss12.5
     ./gen_regionsmask.sh seaice_regions_sh_RH.shp e2s12.5

   or run all with:
     ./run_gen_regionsmasks.sh sh_RH

13) Create the .png files by running a macro in ImageJ:

   Open ImageJ
   Go to Plugins->Macros->Run...  and choose
     create_pngs_sh_RH.ijm

