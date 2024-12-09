"""
create_seaice_region_netcdfs.py

Create netCDF versions of the region masks
One file per grid which includes:
    - rasterized region mask
    - rasterized region mask with surface mask
Note: Southern hemisphere has four versions, including original and RH

    python create_nisev6_valid_anc.py [<hem> [<maskdir>]]

Sample usage:
    python create_nisev6_valid_anc.py north ./ease2_nisemasks/

    outputs:  nisev6_validmasks_from_oldnise_north.nc

    python create_nisev6_valid_anc.py south ./ease2_nisemasks/

    outputs:  nisev6_validmasks_from_oldnise_south.nc
"""

import os
import numpy as np
import xarray as xr
import datetime as dt


def xwm(m='exiting in xwm()'):
    raise SystemExit(m)


def get_flag_labels(hem, varname, vals_arr):
    # Given a list of values, return a string
    # with a label for each value in the array
    flag_str = "ocean_no_region_specified"

    for val in vals_arr:
        if hem == 'north':
            if val == 1:
                flag_str += ' central_arctic'
            elif val == 2:
                flag_str += ' beaufort_sea'
            elif val == 3:
                flag_str += ' chukchi_sea'
            elif val == 4:
                flag_str += ' east_siberian_sea'
            elif val == 5:
                flag_str += ' laptev_sea'
            elif val == 6:
                flag_str += ' kara_sea'
            elif val == 7:
                flag_str += ' barents_sea'
            elif val == 8:
                flag_str += ' east_greenland_sea'
            elif val == 9:
                flag_str += ' baffin_bay_and_labrador_seas'
            elif val == 10:
                flag_str += ' gulf_of_st_lawrence'
            elif val == 11:
                flag_str += ' hudson_bay'
            elif val == 12:
                flag_str += ' canadian_archipelago'
            elif val == 13:
                flag_str += ' bering_sea'
            elif val == 14:
                flag_str += ' sea_of_okhotsk'
            elif val == 15:
                flag_str += ' sea_of_japan'
            elif val == 16:
                flag_str += ' bohai_and_yellow_seas'
            elif val == 17:
                flag_str += ' baltic_sea'
            elif val == 18:
                flag_str += ' gulf_of_alaska'
        elif hem == 'south' and 'NASA' in varname:
            if val == 1:
                flag_str += ' weddell_sea'
            elif val == 2:
                flag_str += ' indian_ocean'
            elif val == 3:
                flag_str += ' south_pacific_ocean'
            elif val == 4:
                flag_str += ' ross_sea'
            elif val == 5:
                flag_str += ' amundsen_and_bellingshausen_seas'
        elif hem == 'south' and 'RH' in varname:
            if val == 1:
                flag_str += ' weddell_sea'
            elif val == 2:
                flag_str += ' kinghaakonVII_sea'
            elif val == 3:
                flag_str += ' east_antarctica'
            elif val == 4:
                flag_str += ' ross_and_amundsen_seas'
            elif val == 5:
                flag_str += ' amundsen_and_bellingshausen_seas'
        else:
            xwm(f'Could not parse varname: {varname}')

        if val == 30:
            flag_str += ' land'
        elif val == 32:
            flag_str += ' fresh_free_water'
        elif val == 33:
            flag_str += ' ice_on_land'
        elif val == 34:
            flag_str += ' floating_ice_shelf'
        elif val == 35:
            flag_str += ' ocean_disconnected'
        elif val == 40:
            flag_str += ' off_earth'

    return flag_str


def get_gridid_info(gridid):
    # Return the crs for this gridid
    if gridid[:3] == 'psn':
        grid_str = 'NSIDC Polar Stereo Northern Hemisphere'
        xleft = -3850000
        xright = 3750000
        yup = 5850000
        ydown = -5350000
        crs_dict = {
            'grid_mapping_name': "polar_stereographic",
            'straight_vertical_longitude_from_pole': -45.,
            'false_easting': 0.,
            'false_northing': 0.,
            'latitude_of_projection_origin': 90.,
            'standard_parallel': 70.,
            'long_name': 'CRS definition',
            'longitude_of_prime_meridian': 0.,
            'semi_major_axis': 6378137.,
            'inverse_flattening': 298.257223563,
            'spatial_ref': 'PROJCS[\"WGS 84 / NSIDC Sea Ice Polar Stereographic North\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Polar_Stereographic\"],PARAMETER[\"latitude_of_origin\",70],PARAMETER[\"central_meridian\",-45],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",SOUTH],AXIS[\"Northing\",SOUTH],AUTHORITY[\"EPSG\",\"3413\"]]',  # noqa
            'GeoTransform': "-3850000 25000 0 5850000 0 -25000 ",
        }
    elif gridid[:3] == 'pss':
        grid_str = 'NSIDC Polar Stereo Southern Hemisphere'
        xleft = -3950000
        xright = 3950000
        yup = 4350000
        ydown = -3950000
        crs_dict = {
            'grid_mapping_name': "polar_stereographic",
            'straight_vertical_longitude_from_pole': 0.,
            'false_easting': 0.,
            'false_northing': 0.,
            'latitude_of_projection_origin': -90.,
            'standard_parallel': -70.,
            'long_name': 'CRS definition',
            'longitude_of_prime_meridian': 0.,
            'semi_major_axis': 6378137.,
            'inverse_flattening': 298.257223563,
            'spatial_ref': 'PROJCS[\"WGS 84 / NSIDC Sea Ice Polar Stereographic South\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Polar_Stereographic\"],PARAMETER[\"latitude_of_origin\",-70],PARAMETER[\"central_meridian\",0],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",NORTH],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"3976\"]]',  # noqa
            'GeoTransform': '-3850000 25000 0 5850000 0 -25000 ',
        }
    elif gridid[:3] == 'e2n':
        grid_str = 'EASE 2.0 Northern Hemisphere'
        xleft = -9000000
        xright = 9000000
        yup = 9000000
        ydown = -9000000
        crs_dict = {
            'grid_mapping_name': 'lambert_azimuthal_equal_area',
            'false_easting': 0.,
            'false_northing': 0.,
            'latitude_of_projection_origin': 90.,
            'longitude_of_projection_origin': 0.,
            'long_name': 'CRS definition',
            'longitude_of_prime_meridian': 0.,
            'semi_major_axis': 6378137.,
            'inverse_flattening': 298.257223563,
            'spatial_ref': 'PROJCS[\"WGS 84 / NSIDC EASE-Grid 2.0 North\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Lambert_Azimuthal_Equal_Area\"],PARAMETER[\"latitude_of_center\",90],PARAMETER[\"longitude_of_center\",0],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",SOUTH],AXIS[\"Northing\",SOUTH],AUTHORITY[\"EPSG\",\"6931\"]]',  # noqa
            'GeoTransform': '-9000000 25000 0 9000000 0 -25000 ',
        }
    elif gridid[:3] == 'e2s':
        grid_str = 'EASE 2.0 Southern Hemisphere'
        xleft = -9000000
        xright = 9000000
        yup = 9000000
        ydown = -9000000
        crs_dict = {
            'grid_mapping_name': 'lambert_azimuthal_equal_area',
            'false_easting': 0.,
            'false_northing': 0.,
            'latitude_of_projection_origin': -90.,
            'longitude_of_projection_origin': 0.,
            'long_name': 'CRS definition',
            'longitude_of_prime_meridian': 0.,
            'semi_major_axis': 6378137.,
            'inverse_flattening': 298.257223563,
            'spatial_ref': 'PROJCS[\"WGS 84 / NSIDC EASE-Grid 2.0 South\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Lambert_Azimuthal_Equal_Area\"],PARAMETER[\"latitude_of_center\",-90],PARAMETER[\"longitude_of_center\",0],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",NORTH],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"6932\"]]',  # noqa
            'GeoTransform': '-9000000 25000 0 9000000 0 -25000 ',
        }
    else:
        xwm(f'Cannon get crs_dict from gridid: {gridid}')

    return xleft, xright, yup, ydown, crs_dict, grid_str


def get_gridres(gridid):
    # Determine the grid resolution from the gridid
    if '3.125' in gridid:
        res = 3125
        res_str = '3.125km'
    elif '6.25' in gridid:
        res = 6250
        res_str = '6.25km'
    elif '12.5' in gridid:
        res = 12500
        res_str = '12.5km'
    elif '25' in gridid:
        res = 25000
        res_str = '25km'
    else:
        xwm(f'Could not determine res from gridid {gridid}')

    return res, res_str


def create_regions_nc(gridid, nc_fn, product_version):
    # Create a netCDF file from geotiffs with valid snow and seaice
    #    nc_fn='./NSIDC-XXXX_{gridid.upper()}-SeaIceRegions-v1.0.nc'):

    xleft, xright, yup, ydown, crs_dict, grid_str = get_gridid_info(gridid)
    res, res_str = get_gridres(gridid)
    xdim = (xright - xleft) // res
    ydim = (yup - ydown) // res

    if 'psn' in gridid or 'e2n' in gridid:
        hem = 'north'
        fn_sets = ('nh', )
    elif 'pss' in gridid or 'e2s' in gridid:
        hem = 'south'
        fn_sets = ('sh_orig', 'sh_RH',)
    else:
        xwm(f'Could not determine hem from gridid {gridid}')

    x = np.linspace(xleft + res // 2, xright - res // 2, num=xdim, dtype=np.float32)  # noqa
    y = np.linspace(yup - res // 2, ydown + res // 2, num=ydim, dtype=np.float32)  # noqa

    # Create output netCDF file via xarray
    first_mask_str = f'{fn_sets[0]}'

    fn_dat = f'./{gridid[:3]}_fields/seaice_regions_{first_mask_str}_{gridid}.dat'  # noqa
    try:
        assert os.path.isfile(fn_dat)
    except AssertionError:
        xwm(f'No such .dat file: {fn_dat}')
    # print(f'  Reading region raster only from: {fn_dat}')

    fn_land = f'./{gridid[:3]}_fields/seaice_regions_{first_mask_str}_{gridid}_withland.dat'  # noqa
    try:
        assert os.path.isfile(fn_land)
    except AssertionError:
        xwm(f'No such withland file: {fn_land}')
    # print(f'  Reading land/region raster from: {fn_land}')

    seaice_region = np.fromfile(fn_dat, dtype=np.uint8).reshape(ydim, xdim)
    seaice_landmask = np.fromfile(fn_land, dtype=np.uint8).reshape(ydim, xdim)

    if hem == 'south':
        # Read in for RH
        fn_dat_rh = f'./{gridid[:3]}_fields/seaice_regions_{fn_sets[1]}_{gridid}.dat'  # noqa

        try:
            assert os.path.isfile(fn_dat_rh)
        except AssertionError:
            xwm(f'No such .dat file: {fn_dat_rh}')
        # print(f'  Reading region raster only from: {fn_dat_rh}')
        seaice_region_RH = np.fromfile(fn_dat_rh, dtype=np.uint8).reshape(ydim, xdim)  # noqa

        fn_land_rh = f'./{gridid[:3]}_fields/seaice_regions_{fn_sets[1]}_{gridid}_withland.dat'  # noqa
        try:
            assert os.path.isfile(fn_land_rh)
        except AssertionError:
            xwm(f'No such withland file: {fn_land_rh}')
        # print(f'  Reading land/region raster from: {fn_land_rh}')

        seaice_landmask_RH = np.fromfile(fn_land_rh, dtype=np.uint8).reshape(ydim, xdim)  # noqa

    # Separate dataset creations for NH and SH, latter has RH fields
    if hem == 'north':
        ds = xr.Dataset(
            data_vars=dict(
                sea_ice_region=(['y', 'x'], seaice_region, {
                    'standard_name': 'region',
                    'long_name': 'sea ice region mask',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_region.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_region),
                    'flag_meanings': get_flag_labels(hem, 'seaice_region', np.unique(seaice_region)),  # noqa
                    'coverage_content_type': 'image',
                }),
                sea_ice_region_surface_mask=(['y', 'x'], seaice_landmask, {
                    'standard_name': 'region',
                    'long_name': 'sea ice region mask with surface mask',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_landmask.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_landmask),
                    'flag_meanings': get_flag_labels(hem, 'seaice_landmask', np.unique(seaice_landmask)),  # noqa
                    'coverage_content_type': 'image',
                }),
                crs=([], '', crs_dict),
            ),
            coords=dict(
                x=(['x'], x, {
                    'standard_name': 'projection_x_coordinate',
                    'long_name': 'x coordinate of projection',
                    'units': 'm',
                    'coverage_content_type': 'coordinate',
                    'valid_range': np.array((xleft, xright), dtype=np.float32)
                }),
                y=(['y'], y, {
                    'standard_name': 'projection_y_coordinate',
                    'long_name': 'y coordinate of projection',
                    'units': 'm',
                    'coverage_content_type': 'coordinate',
                    'valid_range': np.array((ydown, yup), dtype=np.float32)
                }),
            ),
            attrs=dict(
                title=f'Geographic regions for sea ice for the {res_str} {grid_str} grid',  # noqa
                summary=f'This file provides a description of regions useful for sea ice on the {res_str} {grid_str} grid.  A general raster of the regions is provided without a surface mask so that these region descriptions can be used with any surface mask.  Fields are also provided with a surface mask derived from BU-MODIS land classification data ',  # noqa
                acknowledgment='These data are produced and supported by the NASA National Snow and Ice Data Center Distributed Active Archive Center',  # noqa
                id='10.5067/CYW3O8ZUNIWC',
                naming_authority='org.doi.dx',
                standard_name_authority='CF Standard Name Table (v77, 19 January 2021)',  # noqa
                keywords_vocabulary='NASA Global Change Master Directory (GCMD) Earth Science Keywords, Version 8.1',  # noqa
                license='Access Constraint: These data are freely, openly, and fully accessible, provided that you are logged into your NASA Earthdata profile (https://urs.earthdata.nasa.gov/).  Use Constraint: These data are freely, openly, and fully available to use without restrictions, provided that you cite the data according to the recommended citation at https://nsidc.org/about/use_copyright.html. For more information on the NASA EOSDIS Data Use Policy, see https://earthdata.nasa.gov/earth-observation-data/data-use-policy.',  # noqa
                product_version=product_version,
                metadata_link='10.5067/CYW3O8ZUNIWC',
                date_created=dt.datetime.now().strftime('%Y-%m-%d'),
                Conventions='CF-1.6, ACDD-1.3',
                institution='NASA National Snow and Ice Data Center Distributed Active Archive Center',  # noqa
                contributor_name='Meier, W. N., J. S. Stewart',
                contributor_role='project_scientist scientific_programmer',
                publisher_type='institution',
                publisher_institution='National Snow and Ice Data Center, Cooperative Institute for Research in Environmental Sciences, University of Colorado at Boulder, Boulder, CO',  #noqa
                publisher_url='https://nsidc.org/daac',
                publisher_email='nsidc@nsidc.org',
                geospatial_bounds_crs=geospatial_bounds_crs_str,
                geospatial_bounds=geospatial_bounds_str,
                geospatial_lat_min=geospatial_lat_min_str,
                geospatial_lat_max=geospatial_lat_max_str,
                geospatial_lat_units='degrees_north',
                geospatial_lon_min=geospatial_lon_min_str,
                geospatial_lon_max=geospatial_lon_max_str,
                geospatial_lon_units='degrees_east',
            )
        )
    elif hem == 'south':
        ds = xr.Dataset(
            data_vars=dict(
                sea_ice_region_NASA=(['y', 'x'], seaice_region, {
                    'standard_name': 'region',
                    'long_name': 'seaice region mask',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_region.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_region),
                    'flag_meanings': get_flag_labels(hem, 'seaice_region_NASA', np.unique(seaice_region)),  # noqa
                    'coverage_content_type': 'image',
                }),
                sea_ice_region_NASA_surface_mask=(['y', 'x'], seaice_landmask, {
                    'standard_name': 'region',
                    'long_name': 'seaice region mask (NASA) with surface mask',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_landmask.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_landmask),
                    'flag_meanings': get_flag_labels(hem, 'seaice_region_NASA_landmask', np.unique(seaice_landmask)),  # noqa
                    'coverage_content_type': 'image',
                }),
                sea_ice_region_RH=(['y', 'x'], seaice_region_RH, {
                    'standard_name': 'region',
                    'long_name': 'seaice region mask (RH)',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_region_RH.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_region_RH),
                    'flag_meanings': get_flag_labels(hem, 'seaice_region_RH', np.unique(seaice_region_RH)),  # noqa
                    'coverage_content_type': 'image',
                }),
                sea_ice_region_RH_surface_mask=(['y', 'x'], seaice_landmask_RH, {
                    'standard_name': 'region',
                    'long_name': 'seaice region mask (RH) with surface mask',
                    'grid_mapping': 'crs',
                    'valid_range': np.array((0, seaice_landmask_RH.max()), dtype=np.uint8),  # noqa
                    '_Unsigned': 'true',
                    '_FillValue': np.array((255), dtype=np.uint8),
                    'flag_values': np.unique(seaice_landmask_RH),
                    'flag_meanings': get_flag_labels(hem, 'seaice_landmask_RH', np.unique(seaice_landmask_RH)),  # noqa
                    'coverage_content_type': 'image',
                }),
                crs=([], '', crs_dict),
            ),
            coords=dict(
                x=(['x'], x, {
                    'standard_name': 'projection_x_coordinate',
                    'long_name': 'x coordinate of projection',
                    'units': 'm',
                    'coverage_content_type': 'coordinate',
                    'valid_range': np.array((xleft, xright), dtype=np.float32)
                }),
                y=(['y'], y, {
                    'standard_name': 'projection_y_coordinate',
                    'long_name': 'y coordinate of projection',
                    'units': 'm',
                    'coverage_content_type': 'coordinate',
                    'valid_range': np.array((ydown, yup), dtype=np.float32)
                }),
            ),
            attrs=dict(
                title=f'Geographic regions for sea ice for the {res_str} {grid_str} grid',  # noqa
                summary=f'This file provides a description of regions useful for sea ice on the {res_str} {grid_str} grid.  A general raster of the regions is provided without a surface mask so that these region descriptions can be used with any surface mask.  Fields are also provided with a surface mask derived from BU-MODIS land classification data ',  # noqa
                acknowledgment='These data are produced and supported by the NASA National Snow and Ice Data Center Distributed Active Archive Center',  # noqa
                id='10.5067/CYW3O8ZUNIWC',
                naming_authority='org.doi.dx',
                standard_name_authority='CF Standard Name Table (v77, 19 January 2021)',  # noqa
                keywords_vocabulary='NASA Global Change Master Directory (GCMD) Earth Science Keywords, Version 8.1',  # noqa
                license='Access Constraint: These data are freely, openly, and fully accessible, provided that you are logged into your NASA Earthdata profile (https://urs.earthdata.nasa.gov/).  Use Constraint: These data are freely, openly, and fully available to use without restrictions, provided that you cite the data according to the recommended citation at https://nsidc.org/about/use_copyright.html. For more information on the NASA EOSDIS Data Use Policy, see https://earthdata.nasa.gov/earth-observation-data/data-use-policy.',  # noqa
                product_version=product_version,
                metadata_link='10.5067/CYW3O8ZUNIWC',
                date_created=dt.datetime.now().strftime('%Y-%m-%d'),
                Conventions='CF-1.6, ACDD-1.3',
                institution='NASA National Snow and Ice Data Center Distributed Active Archive Center',  # noqa
                contributor_name='Stewart J. S., W. N. Meier',
                contributor_role='scientific_programmer project_scientist',
                publisher_type='institution',
                publisher_institution='National Snow and Ice Data Center, Cooperative Institute for Research in Environmental Sciences, University of Colorado at Boulder, Boulder, CO',  #noqa
                publisher_url='https://nsidc.org/daac',
                publisher_email='nsidc@nsidc.org',
                geospatial_bounds_crs=geospatial_bounds_crs_str,
                geospatial_bounds=geospatial_bounds_str,
                geospatial_lat_min=geospatial_lat_min_str,
                geospatial_lat_max=geospatial_lat_max_str,
                geospatial_lat_units='degrees_north',
                geospatial_lon_min=geospatial_lon_min_str,
                geospatial_lon_max=geospatial_lon_max_str,
                geospatial_lon_units='degrees_east',
            )
        )

    # ofn = f'seaice_regions_{gridid}.nc'
    ofn = nc_fn

    if hem == 'north':
        ds.to_netcdf(
            ofn,
            encoding={
                'sea_ice_region': {'zlib': True},
                'sea_ice_region_surface_mask': {'zlib': True},
            },
        )
    elif hem == 'south':
        ds.to_netcdf(
            ofn,
            encoding={
                'sea_ice_region_NASA': {'zlib': True},
                'sea_ice_region_NASA_surface_mask': {'zlib': True},
                'sea_ice_region_RH': {'zlib': True},
                'sea_ice_region_RH_surface_mask': {'zlib': True},
            },
        )

    print(f'Wrote: {ofn}')


if __name__ == '__main__':
    import sys

    try:
        gridid = sys.argv[1]
    except IndexError:
        gridid = 'psn25'
        print(f'Using default gridid: {gridid}')

    product_version = 'v1.0'

    if 'psn' in gridid:
        proj = 'PS'
        geospatial_bounds_crs_str = 'EPSG:3411'
        geospatial_bounds_str = 'POLYGON ((-3850000 5850000, 3750000 5850000, 3750000 -5350000, -3850000 -5350000, -3850000 5850000))'  # noqa
        geospatial_lat_min_str = 30.98
        geospatial_lat_max_str = 90.
        geospatial_lon_min_str = -180.
        geospatial_lon_max_str = 180.
    elif 'pss' in gridid:
        proj = 'PS'
        geospatial_bounds_crs_str = 'EPSG:3412'
        geospatial_bounds_str = 'POLYGON ((-3950000 4350000, 3950000 4350000, 3950000 -3950000, -3950000 -3950000, -3950000 4350000))'  # noqa
        geospatial_lat_min_str = -90.
        geospatial_lat_max_str = -39.23
        geospatial_lon_min_str = -180.
        geospatial_lon_max_str = 180.
    elif 'e2n' in gridid:
        proj = 'EASE2'
        geospatial_bounds_crs_str = 'EPSG:6931'
        geospatial_bounds_str = 'POLYGON ((-9000000 9000000, 9000000 9000000, 9000000 -9000000, -9000000 -9000000, -9000000 9000000))'  # noqa
        geospatial_lat_min_str = 0.
        geospatial_lat_max_str = 90.
        geospatial_lon_min_str = -180.
        geospatial_lon_max_str = 180.
    elif 'e2s' in gridid:
        proj = 'EASE2'
        geospatial_bounds_crs_str = 'EPSG:6932'
        geospatial_bounds_str = 'POLYGON ((-9000000 9000000, 9000000 9000000, 9000000 -9000000, -9000000 -9000000, -9000000 9000000))'  # noqa
        geospatial_lat_min_str = -90.
        geospatial_lat_max_str = 0.
        geospatial_lon_min_str = -180.
        geospatial_lon_max_str = 180.

    H = gridid[2].upper()
    res = gridid[3:]
    nc_fn = f'./NSIDC-0780_SeaIceRegions_{proj}-{H}{res}km_{product_version}.nc'
    create_regions_nc(gridid, nc_fn, product_version)
